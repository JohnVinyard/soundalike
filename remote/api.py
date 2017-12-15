from __future__ import print_function
import httplib
import json
import urllib
from hacky_path_processor import PathProcessor
import blosc
import time
import zounds
import sys

import falcon

from config import Sound, most_recent_id, REDIS_CLIENT, DummyFeatureAccessError
from helpers import \
    WebTimeSlice, FeatureUri, SoundUri, SearchUri, Code, RandomSearchUri
from index import hamming_index
from templates import render_html
from decoder_selector import DecoderSelector


class SoundsResource(object):
    def on_get(self, req, resp):
        print('getting sounds', file=sys.stderr)
        urls = map(
            lambda _id: str(SoundUri(_id, req=req)),
            Sound.database.iter_ids())
        resp.set_header('Content-Type', 'application/json')
        resp.body = json.dumps({'sounds': urls})

    def on_post(self, req, resp):
        REDIS_CLIENT.rpush('sound', req.stream.read())
        resp.status = httplib.ACCEPTED


class BaseTaskQueueResource(object):
    def __init__(self, redis_list_name):
        super(BaseTaskQueueResource, self).__init__()
        self.redis_list_name = redis_list_name

    def on_delete(self, req, resp):
        task = REDIS_CLIENT.lpop(self.redis_list_name)
        if task is None:
            resp.status = httplib.NOT_FOUND
        else:
            resp.body = task
            resp.status = httplib.OK


class SoundQueueResource(BaseTaskQueueResource):
    def __init__(self):
        super(SoundQueueResource, self).__init__('sound')


class IndexQueueResource(BaseTaskQueueResource):
    def __init__(self):
        super(IndexQueueResource, self).__init__('index')


class TrainedModelsResource(object):
    def on_put(self, req, resp, trained_model_id):
        REDIS_CLIENT.set('trainedmodel', trained_model_id)
        resp.status = httplib.CREATED


class IndexesResource(object):
    def on_put(self, req, resp, index_id):
        REDIS_CLIENT.lpush('index', index_id)
        resp.status = httplib.ACCEPTED


class SoundResource(object):
    def on_get(self, req, resp, _id):
        # return links to the available features
        _id = urllib.unquote(_id)
        snd = Sound(_id)
        try:
            features = map(
                lambda f: str(FeatureUri(_id=_id, feature=f.key, req=req)),
                filter(lambda x: x.store, Sound.iter_features()))

            d = dict(features=features, **snd.meta)

            codes = set(
                map(lambda x: x.encoded,
                    Code.from_expanded_array(snd.hashed)))
            search_uris = map(lambda code: str(SearchUri(code, req=req)), codes)
            d['similar'] = search_uris

            resp.body = json.dumps(d)
            resp.set_header('Content-Type', 'application/json')
            resp.status = httplib.OK
        except KeyError as e:
            resp.status = httplib.NOT_FOUND


class SoundFeatureResource(object):
    def __init__(self):
        super(SoundFeatureResource, self).__init__()

    def _get_key_and_db(self, _id, feature):
        feat = Sound.features[feature]
        db = Sound.database
        kb = db.key_builder
        key = kb.build(_id, feat.key, feat.version)
        return key, db

    def on_put(self, req, resp, _id, feature):
        _id = urllib.unquote(_id)
        key, db = self._get_key_and_db(_id, feature)

        with db.write_stream(key, 'application/octet-stream') as ws:
            data = blosc.decompress(req.stream.read())
            ws.write(data)
        resp.status = httplib.NO_CONTENT

    def on_head(self, req, resp, _id, feature):
        _id = urllib.unquote(_id)
        key, db = self._get_key_and_db(_id, feature)

        if key not in db:
            resp.status = httplib.NOT_FOUND
            return

        size = db.size(key)
        resp.status = httplib.NO_CONTENT
        resp.set_header('Content-Length', size)

    def on_get(self, req, resp, _id, feature):
        _id = urllib.unquote(_id)
        try:
            ts = WebTimeSlice(req)
            feature = Sound.features[feature]
            selector = DecoderSelector()
            result = selector.decode(_id, feature, ts, req)

            resp.body = result.flo.read()
            for k, v in result.headers.iteritems():
                resp.set_header(k, v)

            # TODO: Can I fold this into DecoderSelector somehow?
            if feature.key != 'hashed':
                resp.set_header('Cache-Control', 'max-age=86400')

            resp.status = httplib.OK
        except (KeyError, DummyFeatureAccessError) as e:
            resp.status = httplib.NOT_FOUND


def transform_search_result(result, req, nresults):
    _id, ts = result
    ts = WebTimeSlice(ts)
    quoted_id = urllib.quote(_id, safe='')
    qs = ts.to_query_string()

    start = ts.start / zounds.Seconds(1)
    duration = ts.duration / zounds.Seconds(1)
    end = start + duration

    return dict(
        _id=_id,
        start=start,
        duration=duration,
        end=end,
        search=str(SearchUri(
            quoted_id,
            req=req,
            timeslice=ts,
            nresults=nresults)),
        bark=str(FeatureUri(
            quoted_id=quoted_id,
            feature='geom',
            timeslice_query_string=qs,
            req=req)),
        hashed=str(FeatureUri(
            quoted_id=quoted_id,
            feature='hashed',
            timeslice_query_string=qs,
            req=req)),
        audio=str(FeatureUri(
            quoted_id=quoted_id,
            feature='ogg',
            timeslice_query_string=qs,
            req=req)),
        meta=str(FeatureUri(
            quoted_id=quoted_id,
            feature='meta',
            timeslice_query_string=qs,
            req=req))
    )


class SearchResource(object):
    def __init__(self):
        super(SearchResource, self).__init__()
        self.index = None

    def _init_index(self):
        if self.index is None:
            print('initializing index')
            self.index = hamming_index(Sound, most_recent_id())
            return True
        return False

    def __del__(self):
        self.index.close()

    def on_get(self, req, resp, code=None):
        start = time.time()

        did_initialize = self._init_index()

        try:
            n_results = int(req.params['nresults'])
        except (KeyError, TypeError, ValueError):
            n_results = 5

        if code is None:
            results = self.index.random_search(
                n_results, multithreaded=True, sort=True)
        elif code.startswith('http'):
            # get the timeslice from the query string
            ts = WebTimeSlice(req)
            # then get the hash for that timeslice
            sound_id = urllib.unquote(code)
            snd = Sound(sound_id)
            hashed = snd.hashed[ts]
            middlemost = len(hashed) // 2
            hashed = hashed[middlemost]
            # then construct a link from that hash
            new_code = list(Code.from_expanded_array(hashed[None, ...]))[0]
            results = self.index.search(
                new_code.raw.tostring(),
                n_results,
                multithreaded=True,
                sort=True)
        else:
            results = self.index.search(
                Code.from_encoded(code).raw,
                n_results,
                multithreaded=True,
                sort=True)

        results = map(lambda x: transform_search_result(x, req, n_results),
                      results)

        if 'text/html' in req.get_header('Accept'):
            end = time.time() - start
            resp.body = render_html(
                results,
                did_initialize,
                end * 1000,
                str(RandomSearchUri(req=req, nresults=n_results)))
            resp.set_header('Content-Type', 'text/html')
        else:
            end = time.time() - start
            resp.body = json.dumps(
                {
                    'results': results,
                    'initialize': did_initialize,
                    'time': end * 1000,
                    'random': str(RandomSearchUri(req=req, nresults=n_results))
                })
            resp.set_header('Content-Type', 'application/json')


api = application = falcon.API(middleware=PathProcessor())

# public endpoints
api.add_route('/sounds/', SoundsResource())
api.add_route('/sounds/{_id}', SoundResource())
api.add_route('/sounds/{_id}/{feature}', SoundFeatureResource())
api.add_route('/search', SearchResource())
api.add_route('/search/{code}', SearchResource())

# secure endpoints
api.add_route('/tasks/sounds/next', SoundQueueResource())
api.add_route('/tasks/indexes/next', IndexQueueResource())
api.add_route('/indexes/{index_id}', IndexesResource())
api.add_route('/trainedmodels/{trained_model_id}', TrainedModelsResource())

print(api, file=sys.stderr)
