from __future__ import print_function
import config
from index import hamming_index, HammingIndexPath
import sys
import requests
import json
import zounds
from helpers import WebTimeSlice


def create_elasticsearch_index():
    resp = requests.put(
        'http://elasticsearch:9200/segments',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'mappings': {
                'segment': {
                    'properties': {
                        'location': {
                            'type': 'geo_point'
                        }
                    }
                }
            }
        }))

    print(resp, file=sys.stderr)
    print(resp.content, file=sys.stderr)
    print(resp, file=sys.stderr)

    for snd in config.Sound:
        crts = zounds.ConstantRateTimeSeries(snd.pca)
        for ts, data, in crts.iter_slices():
            _id = hash((snd._id, ts))
            wts = WebTimeSlice(ts)
            uri = 'http://elasticsearch:9200/segments/segment/{_id}' \
                .format(**locals())
            doc = {
                # note that the array is in the order lon, lat
                'location': list(data)[::-1],
                'sound_id': snd._id,
                'start': wts.start_seconds,
                'duration': wts.duration_seconds
            }
            print(doc, file=sys.stderr)
            resp = requests.put(
                uri,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(doc))

            print(resp, file=sys.stderr)
            print(resp.content, file=sys.stderr)


def main():
    with hamming_index(config.Sound, index_id) as index:
        for snd in config.Sound:
            try:
                index.add(snd._id)
                print('indexed {_id}'.format(_id=snd._id), file=sys.stderr)
            except Exception as e:
                print('indexing error {e}'.format(e=e))

    HammingIndexPath.clean_old(keep_past=2)

    try:
        create_elasticsearch_index()
    except Exception as e:
        print(e, file=sys.stderr)

if __name__ == '__main__':
    for index_id in config.soundalike_client \
            .poll_for_index_tasks(frequency_seconds=10):
        try:
            reload(config)
            main()
        except Exception as e:
            print('indexer.py Error', e, file=sys.stderr)

