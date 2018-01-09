import featureflow as ff
import zounds
from config import AutoencoderSettings as Settings, spectrogram_duration

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
        packbits=True,
        needs=unitnorm)

    pipeline = ff.PickleFeature(
        zounds.PreprocessingPipeline,
        needs=(scaled, embedding, unitnorm, simhash),
        store=True)


class NoTrainedModelException(Exception):
    pass


def most_recent_id():
    _ids = list(EmbeddingPipeline.database.iter_ids())

    if len(_ids) == 0:
        raise NoTrainedModelException()

    _ids = sorted(_ids)
    return _ids[-1]
