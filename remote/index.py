import zounds
import glob
import shutil
from config import base_path
import os


class HammingIndexPath(object):
    def __init__(self, recent_id):
        self.recent_id = recent_id

    @classmethod
    def indices(cls):
        files = sorted(glob.glob(os.path.join(base_path, 'index_*')))
        return files

    @classmethod
    def most_recent_index(cls):
        return cls.indices()[-1]

    @classmethod
    def clean_old(cls, keep_past=2):
        files = cls.indices()
        # always keep the N newest indexes
        oldest = files[:-keep_past]
        for path in oldest:
            shutil.rmtree(path, ignore_errors=True)
            print 'removed {path}'.format(**locals())

    def __str__(self):
        filename = 'index_{recent_id}'.format(**self.__dict__)
        return os.path.join(base_path, filename)


def hamming_index(snd_cls, recent_id=None):

    if recent_id:
        path = str(HammingIndexPath(recent_id))
    else:
        path = HammingIndexPath.most_recent_index()

    return zounds.HammingIndex(
        snd_cls,
        snd_cls.hashed,
        version=snd_cls.hashed.version,
        path=path,
        listen=False,
        web_url=lambda doc, ts: doc.meta['web_url'])
