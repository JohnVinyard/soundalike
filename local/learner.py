import argparse
from random import choice
import time
import numpy as np
import torch.nn.functional as F
import zounds
from scipy.signal import resample
from torch import nn
from zounds.learn import Conv2d
from multiprocessing.pool import Pool, cpu_count

from autoencoder import EmbeddingPipeline, most_recent_id
from config import \
    Sound, soundalike_client, spectrogram_duration, scale_bands, anchor_slice

embedding_dimension = 128


def additive_noise(anchor, neighborhood):
    amt = np.random.uniform(0.01, 0.05)
    return anchor + np.random.normal(0, amt, anchor.shape)


def nearby(anchor, neighborhood):
    slce = choice([
        slice(0, spectrogram_duration),
        slice(spectrogram_duration * 2, spectrogram_duration * 3)])
    return neighborhood[:, slce]


def time_stretch(anchor, neighborhood):
    factor = np.random.uniform(0.5, 1.5)
    new_size = int(factor * anchor.shape[1])
    rs = resample(anchor, new_size, axis=1)
    if new_size > spectrogram_duration:
        return rs[:, :spectrogram_duration, :]
    else:
        diff = spectrogram_duration - new_size
        return np.pad(
            rs, ((0, 0), (0, diff), (0, 0)), mode='constant', constant_values=0)


def pitch_shift(anchor, neighborhood):
    amt = np.random.randint(-10, 10)
    shifted = np.roll(anchor, amt, axis=-1)
    if amt > 0:
        shifted[..., :amt] = 0
    else:
        shifted[..., amt:] = 0
    return shifted


class Network(nn.Module):
    def __init__(self):
        super(Network, self).__init__()
        self.main = nn.Sequential(
            Conv2d(1, 128, (3, 5), (2, 3), (0, 0)),
            Conv2d(128, 256, (3, 3), (2, 2), (0, 0)),
            Conv2d(256, 512, (3, 3), (2, 2), (0, 0)),
            Conv2d(512, 512, (3, 3), (2, 2), (0, 0)),
            Conv2d(512, 512, (3, 3), (2, 2), (0, 0)),
        )
        self.l1 = nn.Linear(512, 256, bias=False)
        self.bn1 = nn.BatchNorm1d(256)
        self.l2 = nn.Linear(256, embedding_dimension, bias=False)

    def forward(self, x):
        x = x.view(-1, 1, spectrogram_duration, scale_bands)
        x = self.main(x)
        x = x.view(-1, 512)
        x = self.l1(x)
        x = self.bn1(x)
        x = F.leaky_relu(x, 0.2)
        x = F.dropout(x, 0.2)
        x = self.l2(x)
        return x


def access_log_spectrogram(snd):
    return snd.log_spectrogram


def learn(epochs=500, nsamples=int(1e5), init_weights=False):
    if not len(list(Sound.database.iter_ids())) > 0:
        print 'there are no sounds to learn from, exiting'
        return

    network = Network()

    if init_weights:
        recent_id = most_recent_id()
        print 'loading weights from', recent_id
        faae = EmbeddingPipeline(_id=recent_id)
        previous_network = faae.pipeline[1].network
        network.load_state_dict(previous_network.state_dict())
        print 'loaded weights from', recent_id
        del previous_network

    trainer = zounds.TripletEmbeddingTrainer(
        network,
        epochs=epochs,
        batch_size=64,
        anchor_slice=anchor_slice,
        deformations=[nearby, pitch_shift, time_stretch, additive_noise])

    pool = Pool(cpu_count())
    iterator = pool.imap_unordered(access_log_spectrogram, Sound)

    _id = 'Embedding{t}'.format(t=int(time.time() * 1e6))

    EmbeddingPipeline.process(
        _id=_id,
        samples=iterator,
        trainer=trainer,
        bits=1024,
        nsamples=nsamples)

    pool.close()
    pool.join()

    soundalike_client.add_trained_model(_id)

    print 'Learner most recent', _id

    print 'computing learned features'
    snd_class = with_hash(_id)
    for snd in snd_class:
        print snd.hashed.shape

    return _id


def index(_id):
    if not _id:
        print 'there is no trained model, exiting'
        return

    soundalike_client.add_index(_id)


def with_hash(most_recent_autoencoder_id=None):
    if most_recent_autoencoder_id is None:
        most_recent_autoencoder_id = most_recent_id()

    class Snd(Sound):
        embedding = zounds.ArrayWithUnitsFeature(
            zounds.Learned,
            learned=EmbeddingPipeline(_id=most_recent_autoencoder_id),
            pipeline_func=lambda x: x.pipeline[:-1],
            needs=Sound.ls)

        hashed = zounds.ArrayWithUnitsFeature(
            zounds.Learned,
            learned=EmbeddingPipeline(_id=most_recent_autoencoder_id),
            needs=Sound.ls,
            store=True)

    return Snd


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--learn',
        help='learn a model',
        action='store_true')
    parser.add_argument(
        '--index',
        help='build a new index',
        action='store_true')
    parser.add_argument(
        '--epochs',
        help='the number of epochs to train the model',
        type=int)
    parser.add_argument(
        '--init-weights',
        help='should weights be initialized from previous model',
        action='store_true')
    parser.add_argument(
        '--nsamples',
        help='the number of samples to train on',
        default=int(1e5),
        type=int)

    args = parser.parse_args()

    if args.learn:
        _id = learn(args.epochs, args.nsamples, args.init_weights)
    else:
        _id = most_recent_id()

    if args.index:
        print 'indexing with model', _id
        index(_id)
