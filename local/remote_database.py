import httplib
from io import BytesIO

from featureflow import Database
from requests.exceptions import HTTPError


class WriteStream(object):
    def __init__(self, _id, feature, client):
        self.feature = feature
        self._id = _id
        self.client = client
        self.buf = BytesIO()

    def __enter__(self):
        return self

    def __exit__(self, t, value, traceback):
        self.close()

    def close(self):
        self.buf.seek(0)
        self.client.set_sound_feature(self._id, self.feature, self.buf)

    def write(self, data):
        self.buf.write(data)


class RemoteDatabase(Database):
    def __init__(self, client, key_builder=None):
        super(RemoteDatabase, self).__init__(key_builder)
        self.client = client

    def _extract(self, key):
        _id, feature, version = self.key_builder.decompose(key)
        return _id, feature

    def write_stream(self, key, content_type):
        _id, feature = self._extract(key)
        return WriteStream(_id, feature, self.client)

    def read_stream(self, key):
        _id, feature = self._extract(key)

        try:
            content = self.client.get_sound_feature(_id, feature)
            return BytesIO(content)
        except HTTPError as e:
            if e.response.status_code == httplib.NOT_FOUND:
                raise KeyError(key)
            else:
                raise

    def size(self, key):
        """
        Fetch the size of the remote object
        """
        _id, feature = self._extract(key)
        return self.client.sound_feature_size(_id, feature)

    def iter_ids(self):
        """
        Iterate over all remote ids
        """
        return self.client.iter_sounds()

    def __contains__(self, key):
        _id, feature = self._extract(key)
        return self.client.sound_feature_exists(_id, feature)

    def __delitem__(self, key):
        raise NotImplementedError()
