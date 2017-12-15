import urllib
from autoencoder import most_recent_id, NoTrainedModelException
from config import Sound, soundalike_client
from learner import with_hash, Network

if __name__ == '__main__':
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
