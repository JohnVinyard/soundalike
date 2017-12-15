import sys
from os import path, environ

import featureflow as ff

from remote_database import RemoteDatabase

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from common.model import \
    SoundWithNoSettings, spectrogram_duration, scale_bands, anchor_slice
from common.soundalike_client import SoundalikeClient

soundalike_client = SoundalikeClient('http', environ['SOUNDALIKE_REMOTE'])


class ModelSettings(ff.PersistenceSettings):
    id_provider = ff.UserSpecifiedIdProvider(key='_id')
    key_builder = ff.StringDelimitedKeyBuilder('|')
    database = RemoteDatabase(soundalike_client, key_builder=key_builder)


class AutoencoderSettings(ff.PersistenceSettings):
    id_provider = ff.UserSpecifiedIdProvider(key='_id')
    key_builder = ff.StringDelimitedKeyBuilder(seperator='|')
    database = ff.LmdbDatabase(
        path='/var/lib/soundalike/autoencoder',
        map_size=1e10,
        key_builder=key_builder)


class Sound(SoundWithNoSettings, ModelSettings):
    pass
