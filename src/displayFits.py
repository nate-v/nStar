import numpy as np
from astropy.io import fits

def load(file_path):
  """Load a 2-D image, taking the first plane from any higher dimensions."""
  with fits.open(file_path) as hdus:
    for hdu in hdus:
      data = getattr(hdu, "data", None)
      if data is None:
        continue

      image = np.squeeze(data)
      while image.ndim > 2:
        if image.shape[0] == 0:
          break
        image = image[0]

      if image.ndim == 2:
        return np.array(image, copy=True)

  raise ValueError("No 2-D FITS image plane found in selected file.")
