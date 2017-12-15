import numpy as np
from PIL import Image

import matplotlib
matplotlib.use('Agg')
from io import BytesIO


def generate_2d_image(data):
    data = np.asarray(data)
    data = (np.abs(data) * 255).astype(np.uint8)
    img = Image.fromarray(np.rot90(data), mode='L')
    bio = BytesIO()
    img.save(bio, format='png')
    bio.seek(0)
    return bio


# TODO: this should be a custom decoder instead
def generate_image(data):
    if data.ndim == 3:
        data = np.concatenate(data)

    data = np.asarray(data)
    data = np.abs(data)

    data /= np.max(data)
    data = (data * 255).astype(np.uint8)
    img = Image.fromarray(np.rot90(data), mode='L')
    bio = BytesIO()
    img.save(bio, format='png')
    bio.seek(0)
    return bio