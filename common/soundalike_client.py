import requests
import urlparse
import time
import zounds
import json
import httplib
import urllib
import blosc
import lmdb


class SoundalikeClient(object):
    def __init__(self, scheme, host, feature_cache=None, never_cache=set()):
        self.never_cache = never_cache
        self.host = host
        self.scheme = scheme
        self.env = None
        if feature_cache:
            self.env = lmdb.open(
                feature_cache,
                map_size=1e10,
                writemap=True,
                map_async=True,
                metasync=True)

    def _uri(self, path):
        result = urlparse.ParseResult(
            scheme=self.scheme,
            netloc=self.host,
            path=path,
            query='',
            params='',
            fragment='')
        return result.geturl()

    def _sound_feature_uri(self, _id, feature):
        escaped_id = urllib.quote(_id, safe='')
        return self._uri('/sounds/{escaped_id}/{feature}'.format(**locals()))

    def _poll(self, func, frequency_seconds=1):
        while True:
            try:
                yield func()
            except:
                time.sleep(frequency_seconds)

    def next_sound_task(self):
        resp = requests.delete(self._uri('/tasks/sounds/next'))
        resp.raise_for_status()
        task = json.loads(resp.content)
        metadata = zounds.AudioMetaData(**task)
        metadata.uri = requests.Request('GET', url=metadata.uri)
        return metadata

    def poll_for_sound_tasks(self, frequency_seconds=1):
        return self._poll(self.next_sound_task, frequency_seconds)

    def next_index_task(self):
        resp = requests.delete(self._uri('/tasks/indexes/next'))
        resp.raise_for_status()
        return resp.content

    def poll_for_index_tasks(self, frequency_seconds=1):
        return self._poll(self.next_index_task, frequency_seconds)

    def add_trained_model(self, _id):
        resp = requests.put(
            self._uri('/trainedmodels/{_id}'.format(**locals())))
        resp.raise_for_status()

    def add_index(self, _id):
        resp = requests.put(self._uri('/indexes/{_id}'.format(**locals())))
        resp.raise_for_status()

    def add_sound(self, sound_metadata):
        resp = requests.post(
            self._uri('/sounds'), data=json.dumps(sound_metadata))
        resp.raise_for_status()

    def iter_sounds(self):
        resp = requests.get(self._uri('/sounds'))
        for sound_uri in resp.json()['sounds']:
            result = urlparse.urlparse(sound_uri)
            result = result.path.replace('/sounds/', '')
            result = urllib.unquote(result)
            yield result

    def sound_feature_exists(self, _id, feature):
        resp = requests.head(self._sound_feature_uri(_id, feature))
        return resp.status_code == httplib.NO_CONTENT

    def sound_feature_size(self, _id, feature):
        resp = requests.head(self._sound_feature_uri(_id, feature))
        resp.raise_for_status()
        return int(resp.headers['Content-Length'])

    def get_sound_feature(self, _id, feature):
        cache_key = '{_id}:{feature}'.format(**locals())
        fetched_data = None

        # check if the feature exists locally
        if self.env and feature not in self.never_cache:
            with self.env.begin() as txn:
                fetched_data = txn.get(cache_key)

        # make an HTTP request, either because the feature isn't cached locally
        # or caching isn't turned on
        if not fetched_data:
            resp = requests.get(
                self._sound_feature_uri(_id, feature),
                headers={'Accept': 'application/octet-stream'})
            resp.raise_for_status()
            fetched_data = resp.content
            if resp.headers['Content-Type'] == 'application/octet-stream':
                fetched_data = blosc.decompress(fetched_data)
            # write the fetched data back to the cache
            if self.env and feature not in self.never_cache:
                with self.env.begin(write=True) as txn:
                    txn.put(cache_key, fetched_data)

        return fetched_data

    def set_sound_feature(self, _id, feature, data):

        try:
            data = blosc.compress(data, typesize=32)
        except TypeError:
            data = blosc.compress(data.getvalue(), typesize=32)

        resp = requests.put(self._sound_feature_uri(_id, feature), data=data)
        resp.raise_for_status()

    def random_search(self, nresults=20, accept='application/json'):
        resp = requests.get(
            self._uri('/search'),
            headers={'Accept': accept},
            params={'nresults': nresults})
        return resp.content

    def search(self, code, nresults=20, accept='application/json'):
        resp = requests.get(
            self._uri('/search/{code}'.format(**locals())),
            headers={'Accept': accept},
            params={'nresults': nresults})
        return resp.content
