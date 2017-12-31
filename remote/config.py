from __future__ import print_function
import zounds
import featureflow as ff

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from common.model import SoundWithNoSettings
from common.soundalike_client import SoundalikeClient
import redis

REDIS_CLIENT = redis.StrictRedis(host='redis')

soundalike_client = SoundalikeClient('http', 'api')

base_path = '/var/lib/data'

print('starting config')


class ModelSettings(ff.PersistenceSettings):
    id_provider = ff.UserSpecifiedIdProvider(key='_id')
    key_builder = ff.StringDelimitedKeyBuilder(seperator='|')
    database = ff.LmdbDatabase(
        path=path.join(base_path, 'soundalike'),
        map_size=1e11,
        key_builder=key_builder)


class DummyFeatureAccessError(Exception):
    pass


def most_recent_id():
    return REDIS_CLIENT.get('trainedmodel') or ''


class IdentityNode(ff.Node):
    def __init__(self, needs=None):
        super(IdentityNode, self).__init__(needs=needs)

    @property
    def version(self):
        return most_recent_id()

    def _process(self, data):
        raise DummyFeatureAccessError()
        yield data


class Sound(SoundWithNoSettings, ModelSettings):
    hashed = zounds.ArrayWithUnitsFeature(
        IdentityNode,
        needs=SoundWithNoSettings.ls,
        store=True)

    pca = zounds.ArrayWithUnitsFeature(
        IdentityNode,
        needs=SoundWithNoSettings.ls,
        store=True)


print('done with config')
