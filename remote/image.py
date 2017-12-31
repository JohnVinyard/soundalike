import numpy as np
from PIL import Image
from io import BytesIO


# TODO: this should be a custom decoder instead
def generate_image(data):
    if data.ndim == 3:
        data = np.concatenate(data)

    data = np.asarray(data)
    data = np.abs(data)
    data /= np.max(data)
    data = (data * 255).astype(np.uint8)
    data = np.rot90(data)

    rgba = np.zeros(data.shape + (4,), dtype=np.uint8)
    rgba[..., 3] = data

    img = Image.fromarray(rgba, mode='RGBA')
    bio = BytesIO()
    img.save(bio, format='png')
    bio.seek(0)
    return bio


if __name__ == '__main__':
    geom = np.ones((64, 64))
    for i in xrange(10000):
        generate_image(geom)
