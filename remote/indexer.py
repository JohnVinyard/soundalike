from __future__ import print_function
import config
from index import hamming_index, HammingIndexPath
import sys

if __name__ == '__main__':

    for index_id in config.soundalike_client \
            .poll_for_index_tasks(frequency_seconds=10):
        reload(config)

        with hamming_index(config.Sound, index_id) as index:
            for snd in config.Sound:
                try:
                    index.add(snd._id)
                    print('indexed {_id}'.format(_id=snd._id), file=sys.stderr)
                except Exception as e:
                    print('indexing error {e}'.format(e=e))

        HammingIndexPath.clean_old(keep_past=2)
