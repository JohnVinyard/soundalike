import numpy as np
import zounds
from zounds.spectral import apply_scale

samplerate = zounds.SR11025()
BaseModel = zounds.resampled(resample_to=samplerate)

scale_bands = 96
spectrogram_duration = 64

anchor_slice = slice(spectrogram_duration, spectrogram_duration * 2)

scale = zounds.GeometricScale(
    start_center_hz=50,
    stop_center_hz=samplerate.nyquist,
    bandwidth_ratio=0.115,
    n_bands=scale_bands)
scale.ensure_overlap_ratio()

spectrogram_duration = 64

windowing_scheme = zounds.HalfLapped()
spectrogram_sample_rate = zounds.SampleRate(
    frequency=windowing_scheme.frequency * (spectrogram_duration // 2),
    duration=windowing_scheme.frequency * spectrogram_duration)


def spectrogram(x):
    x = apply_scale(
        np.abs(x.real), scale, window=zounds.OggVorbisWindowingFunc())
    x = zounds.log_modulus(x * 100)
    return x * zounds.AWeighting()


class SoundWithNoSettings(BaseModel):
    short_windowed = zounds.ArrayWithUnitsFeature(
        zounds.SlidingWindow,
        wscheme=windowing_scheme,
        wfunc=zounds.OggVorbisWindowingFunc(),
        needs=BaseModel.resampled)

    fft = zounds.ArrayWithUnitsFeature(
        zounds.FFT,
        needs=short_windowed)

    geom = zounds.ArrayWithUnitsFeature(
        spectrogram,
        needs=fft,
        store=True)

    log_spectrogram = zounds.ArrayWithUnitsFeature(
        zounds.SlidingWindow,
        wscheme=zounds.SampleRate(
            frequency=windowing_scheme.frequency * (spectrogram_duration // 2),
            duration=windowing_scheme.frequency * spectrogram_duration * 3),
        needs=geom)

    ls = zounds.ArrayWithUnitsFeature(
        zounds.SlidingWindow,
        wscheme=spectrogram_sample_rate,
        needs=geom)


@zounds.simple_in_memory_settings
class InMemorySound(SoundWithNoSettings):
    pass
