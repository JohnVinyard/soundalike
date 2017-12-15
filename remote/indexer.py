import config
from index import hamming_index, HammingIndexPath

if __name__ == '__main__':

    for index_id in config.soundalike_client\
            .poll_for_index_tasks(frequency_seconds=1):
        reload(config)

        with hamming_index(config.Sound, index_id) as index:
            print 'starting to index', index_id
            index.add_all()
            print 'done indexing', index_id

        HammingIndexPath.clean_old(keep_past=2)
