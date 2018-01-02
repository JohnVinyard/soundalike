import featureflow as ff
import zounds
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from config import AutoencoderSettings as Settings, spectrogram_duration
import numpy as np

anchor_slice = slice(spectrogram_duration, spectrogram_duration * 2)

BasePipeline = zounds.learning_pipeline()


class EmbeddingPipeline(BasePipeline, Settings):
    scaled = ff.PickleFeature(
        zounds.InstanceScaling,
        needs=BasePipeline.shuffled)

    embedding = ff.PickleFeature(
        zounds.PyTorchNetwork,
        trainer=ff.Var('trainer'),
        post_training_func=(lambda x: x[:, anchor_slice]),
        needs=dict(data=scaled))

    unitnorm = ff.PickleFeature(
        zounds.UnitNorm,
        needs=embedding)

    simhash = ff.PickleFeature(
        zounds.SimHash,
        bits=ff.Var('bits'),
        needs=unitnorm)

    pca = ff.PickleFeature(
        zounds.SklearnModel,
        model=PCA(n_components=2),
        needs=unitnorm)

    centered = ff.PickleFeature(
        zounds.SklearnModel,
        model=MinMaxScaler(feature_range=(-1, 1)),
        needs=pca)

    # scale the PCA values to look like geo-coordinates
    geo_scaled = ff.PickleFeature(
        zounds.Multiply,
        factor=np.array([85, 170]),
        needs=centered)

    pipeline = ff.PickleFeature(
        zounds.PreprocessingPipeline,
        needs=(scaled, embedding, unitnorm, simhash),
        store=True)

    pca_pipeline = ff.PickleFeature(
        zounds.PreprocessingPipeline,
        needs=(scaled, embedding, unitnorm, pca, centered, geo_scaled),
        store=True)


class NoTrainedModelException(Exception):
    pass


def most_recent_id():
    _ids = list(EmbeddingPipeline.database.iter_ids())

    if len(_ids) == 0:
        raise NoTrainedModelException()

    _ids = sorted(_ids)
    return _ids[-1]
