from __future__ import print_function
import config
from index import hamming_index, HammingIndexPath
import sys
import uuid


def main(index_id):
    # create a new index every time.  never add to an existing index
    index_id = index_id + uuid.uuid4().hex[:4]
    with hamming_index(config.Sound, index_id, writeonly=True) as index:
        for snd in config.Sound:
            try:
                index.add(snd._id)
                print('indexed {_id}'.format(_id=snd._id), file=sys.stderr)
            except Exception as e:
                print('indexing error {e}'.format(e=e))

    HammingIndexPath.clean_old(keep_past=2)


if __name__ == '__main__':
    for index_id in config.soundalike_client \
            .poll_for_index_tasks(frequency_seconds=10):
        try:
            reload(config)
            main(index_id)
        except Exception as e:
            print('indexer.py Error', e, file=sys.stderr)
