import urllib
from autoencoder import most_recent_id, NoTrainedModelException
from config import Sound, soundalike_client
from learner import with_hash, Network
from multiprocessing.pool import Pool
import argparse


def work():
    recent_id = None
    cls = None

    for metadata in soundalike_client.poll_for_sound_tasks():
        try:
            new_id = most_recent_id()
            if new_id != recent_id:
                recent_id = new_id
                cls = with_hash(recent_id)
        except NoTrainedModelException:
            cls = Sound

        if cls.exists(metadata.uri.url):
            continue

        cls.process(meta=metadata, _id=metadata.uri.url)
        print 'check it out at', urllib.quote(metadata.uri.url, safe='')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--processes',
        type=int,
        default=4,
        help='how many workers should be launched in parallel?')
    args = parser.parse_args()
    pool = Pool(args.processes)

    for i in xrange(args.processes):
        pool.apply_async(work)

    pool.close()
    pool.join()
