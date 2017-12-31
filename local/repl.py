import zounds
from learner import with_hash, Network, EmbeddingPipeline, most_recent_id

if __name__ == '__main__':

    Sound = with_hash()

    pipeline = EmbeddingPipeline(most_recent_id())

    app = zounds.ZoundsApp(
        model=Sound,
        audio_feature=Sound.ogg,
        visualization_feature=Sound.geom,
        globals=globals(),
        locals=locals())
    app.start(8888)