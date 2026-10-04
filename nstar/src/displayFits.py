import numpy as np
from astropy.io import fits

def load(file_path):
  with fits.open(file_path) as hdus:
    for hdu in hdus:
      data = getattr(hdu, "data", None)
      if data is not None and getattr(data, "ndim", None) == 2:
        return np.array(data, copy=True)

  raise ValueError("No FITS image data found in selected file.")

def display(file):
  pass

