from config import Sound
import os
import urllib


def split_path(path):
    head, tail = os.path.split(path)
    if not tail:
        return
    for segment in split_path(head):
        yield segment
    yield tail


class PathProcessor(object):
    def process_request(self, req, resp):
        segments = list(split_path(req.path))

        if not segments:
            return

        if (segments[0] == 'sounds' or segments[0] == 'search') and len(segments) > 1:

            stored = filter(lambda x: x.store, Sound.iter_features())
            stored = map(lambda x: x.key, stored)

            if segments[-1] in stored:
                middle = os.path.join(*segments[1:-1])
                req.path = os.path.join(
                    '/',
                    segments[0],
                    urllib.quote(middle, safe=''),
                    segments[-1]).replace('%3A%2F', '%3A%2F%2F')
            else:
                middle = os.path.join(*segments[1:])
                print middle
                req.path = os.path.join(
                    '/',
                    segments[0],
                    urllib.quote(middle, safe='')).replace('%3A%2F',
                                                           '%3A%2F%2F')