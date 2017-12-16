import zounds
from config import Sound

if __name__ == '__main__':
    app = zounds.ZoundsApp(
        model=Sound,
        audio_feature=Sound.ogg,
        visualization_feature=Sound.geom,
        globals=globals(),
        locals=locals())
    app.start(8888)