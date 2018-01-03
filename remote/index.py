from __future__ import print_function
import zounds
import glob
import shutil
from config import base_path, module_logger
import os
import sys


class NoIndexesError(Exception):
    pass


class HammingIndexPath(object):
    def __init__(self, recent_id):
        self.recent_id = recent_id

    @classmethod
    def indices(cls):
        files = sorted(glob.glob(os.path.join(base_path, 'index_*')))
        return files

    @classmethod
    def most_recent_index(cls):
        try:
            return cls.indices()[-1]
        except IndexError:
            raise NoIndexesError()

    @classmethod
    def clean_old(cls, keep_past=2):
        files = cls.indices()
        # always keep the N newest indexes
        oldest = files[:-keep_past]
        for path in oldest:
            shutil.rmtree(path, ignore_errors=True)
            print('removed {path}'.format(**locals()))

    def __str__(self):
        filename = 'index_{recent_id}'.format(**self.__dict__)
        return os.path.join(base_path, filename)


def hamming_index(snd_cls, recent_id=None, writeonly=False):
    if recent_id:
        path = str(HammingIndexPath(recent_id))
    else:
        path = HammingIndexPath.most_recent_index()

    def web_url(doc, ts):
        url = doc.meta['web_url']
        print(url, file=sys.stderr)
        return url

    def total_duration(doc, ts):
        duration = doc.geom.dimensions[0].end / zounds.Seconds(1)
        print(duration, file=sys.stderr)
        return duration

    return zounds.HammingIndex(
        snd_cls,
        snd_cls.hashed,
        version='1',
        path=path,
        listen=False,
        writeonly=writeonly,
        web_url=web_url,
        total_duration=total_duration)
