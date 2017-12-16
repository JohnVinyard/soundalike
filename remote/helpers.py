from __future__ import print_function
import zounds
import urllib
import urlparse
import base64
import sys


class Code(object):
    def __init__(self, raw_bytes):
        super(Code, self).__init__()
        self.raw_bytes = raw_bytes

    @property
    def raw(self):
        return self.raw_bytes

    @property
    def encoded(self):
        return base64.urlsafe_b64encode(self.raw_bytes)

    @classmethod
    def from_encoded(cls, code):
        code = urllib.unquote(code)
        return Code(base64.urlsafe_b64decode(code))

    @classmethod
    def from_expanded_array(cls, arr):
        packed = arr.packbits(axis=1)
        for p in packed:
            yield Code(p)


ONE_SECOND = zounds.Seconds(1)


class WebTimeSlice(zounds.TimeSlice):
    def __init__(self, request_or_ts):
        if isinstance(request_or_ts, zounds.TimeSlice):
            ts = request_or_ts
            start = ts.start
            duration = ts.duration
        else:
            request = request_or_ts
            try:
                start = float(request.params['start'])
                start = zounds.Picoseconds(int(start * 1e12))
            except (KeyError, ValueError):
                start = zounds.Picoseconds(0)

            try:
                duration = float(request.params['duration'])
                duration = zounds.Picoseconds(int(duration * 1e12))
            except (KeyError, ValueError):
                duration = None

        super(WebTimeSlice, self).__init__(duration=duration, start=start)

    def to_query_string(self):
        q = dict()
        if self.start:
            q['start'] = self.start / ONE_SECOND
        if self.duration:
            q['duration'] = self.duration / ONE_SECOND
        return q


class BaseUri(object):
    def __init__(self, scheme=None, host=None, req=None):
        super(BaseUri, self).__init__()
        self.scheme = scheme or req.forwarded_scheme
        self.host = host or req.forwarded_host

    def path(self):
        raise NotImplementedError()

    def query(self):
        return dict()

    def __str__(self):
        result = urlparse.ParseResult(
            scheme=self.scheme,
            netloc=self.host,
            path=self.path(),
            query=urllib.urlencode(self.query()),
            params='',
            fragment='')
        return result.geturl()


class SoundUri(BaseUri):
    def __init__(self, _id, scheme=None, host=None, req=None):
        super(SoundUri, self).__init__(scheme, host, req)
        self._id = urllib.quote(_id, safe='')

    def path(self):
        return '/sounds/{_id}'.format(**self.__dict__)


class FeatureUri(BaseUri):
    def __init__(
            self,
            _id=None,
            quoted_id=None,
            feature=None,
            timeslice=None,
            timeslice_query_string=None,
            scheme=None,
            host=None,
            req=None):
        super(FeatureUri, self).__init__(scheme, host, req)
        self.timeslice_query_string = timeslice_query_string
        self.timeslice = timeslice
        self.feature = feature
        self._id = quoted_id or urllib.quote(_id, safe='')

    def query(self):
        if not self.timeslice and not self.timeslice_query_string:
            return super(FeatureUri, self).query()

        if self.timeslice_query_string:
            return self.timeslice_query_string

        return self.timeslice.to_query_string()

    def path(self):
        return '/sounds/{_id}/{feature}'.format(**self.__dict__)


class RandomSearchUri(BaseUri):
    def __init__(
            self,
            scheme=None,
            host=None,
            req=None,
            nresults=None):
        super(RandomSearchUri, self).__init__(scheme, host, req)
        self.nresults = nresults

    def query(self):
        query = super(RandomSearchUri, self).query()
        if self.nresults:
            query.update(nresults=self.nresults)
        return query

    def path(self):
        return '/search/'


class SearchUri(BaseUri):
    def __init__(
            self,
            code,
            timeslice=None,
            scheme=None,
            host=None,
            req=None,
            nresults=None):
        super(SearchUri, self).__init__(scheme, host, req)
        self.nresults = nresults
        self.timeslice = timeslice
        self.code = code

    def query(self):
        query = super(SearchUri, self).query()

        if self.timeslice:
            query.update(self.timeslice.to_query_string())

        if self.nresults:
            query.update(nresults=self.nresults)

        return query

    def path(self):
        return '/search/{code}'.format(**self.__dict__)
