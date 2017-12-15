from featureflow import Decoder, JSONFeature
import zounds
from image import generate_image
from config import Sound
from io import BytesIO
import blosc


class DecodeResult(object):
    def __init__(self, flo, headers):
        self.headers = headers
        self.flo = flo


class BaseDecoder(object):
    def __init__(self):
        super(BaseDecoder, self).__init__()

    def decode(self, _id, feature, cls, timeslice):
        raise NotImplementedError()

    def matches(self, feature, request):
        return False


class RawDecoder(BaseDecoder):
    def __init__(self):
        super(RawDecoder, self).__init__()

    def decode(self, _id, feature, cls, timeslice):
        f = feature(_id=_id, persistence=cls, decoder=Decoder())
        f = BytesIO(blosc.compress(f.read(), typesize=32))
        return DecodeResult(f, {'Content-Type': 'application/octet-stream'})

    def matches(self, feature, request):
        return True


class JsonDecoder(BaseDecoder):
    def __init__(self):
        super(JsonDecoder, self).__init__()

    def matches(self, feature, request):
        return isinstance(feature, JSONFeature)

    def decode(self, _id, feature, cls, timeslice):
        f = feature(_id=_id, persistence=cls, decoder=Decoder())
        f = BytesIO()
        return DecodeResult(f, {'Content-Type': 'application/json'})


class ArrayWithUnitsImageDecoder(BaseDecoder):
    def __init__(self):
        super(ArrayWithUnitsImageDecoder, self).__init__()

    # TODO: Generate images without matplotlib?
    def decode(self, _id, feature, cls, timeslice):
        # TODO: Why is image generation so slow?
        f = feature(_id=_id, persistence=cls)
        img_bytes = generate_image(f[timeslice])
        return DecodeResult(img_bytes, {'Content-Type': 'image/png'})

    def matches(self, feature, request):
        return \
            isinstance(feature, zounds.ArrayWithUnitsFeature) \
            and '*/*' in request.get_header('Accept')


class OggVorbisDecoder(BaseDecoder):
    def __init__(self):
        super(OggVorbisDecoder, self).__init__()

    def decode(self, _id, feature, cls, timeslice):
        # TODO: Why is ogg generation so slow?
        if timeslice == zounds.TimeSlice():
            f = feature(
                _id=_id, persistence=cls, decoder=Decoder())
        else:
            wrapper = feature(_id=_id, persistence=cls)
            f = wrapper[timeslice].encode(fmt='OGG', subtype='VORBIS')
        return DecodeResult(f, {'Content-Type': 'audio/ogg'})

    def matches(self, feature, request):
        return isinstance(feature, zounds.OggVorbisFeature)


class DecoderSelector(object):
    def __init__(self):
        super(DecoderSelector, self).__init__()
        self._decoders = (
            ArrayWithUnitsImageDecoder(),
            OggVorbisDecoder(),
            JsonDecoder(),
            RawDecoder()
        )

    def decode(self, _id, feature, time_slice, request):
        try:
            decoder = filter(
                lambda x: x.matches(feature, request), self._decoders)[0]
            return decoder.decode(_id, feature, Sound, time_slice)
        except IndexError:
            raise ValueError('no suitable decoder found')