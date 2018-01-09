from __future__ import print_function
import config
from index import hamming_index, HammingIndexPath
import uuid

logger = config.module_logger(__file__)


def main(index_id):
    # create a new index every time.  never add to an existing index
    index_id = index_id + uuid.uuid4().hex[:4]
    with hamming_index(config.Sound, index_id, writeonly=True) as index:
        for snd in config.Sound:
            try:
                index.add(snd._id)
                logger.debug('indexed {_id}'.format(_id=snd._id))
            except Exception as e:
                logger.error('indexing error {e}'.format(e=e))

        logger.debug(index.hamming_db.env.readers())
        logger.debug(index.hamming_db.code_size)
        logger.debug(index.hamming_db.path)

    HammingIndexPath.clean_old(keep_past=2)


def poll():
    for index_id in config.soundalike_client \
            .poll_for_index_tasks(frequency_seconds=10):
        try:
            reload(config)
            main(index_id)
        except Exception as e:
            logger.error('indexer.py error {e}'.format(**locals()))


if __name__ == '__main__':
    while True:
        try:
            poll()
        except Exception as e:
            logger.error(
                'indexer error {e}.  restarting polling loop'
                    .format(**locals()))

