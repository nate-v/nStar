import numpy as np

class dataFunctions:
  def normalize(self, data, low_p, high_p, gamma):

    image = np.asarray(data, dtype=np.float64)
    finite = np.isfinite(image)

    low, high = np.percentile(image[finite], [low_p, high_p])
    normalized = np.full(image.shape, np.nan, dtype=np.float64) #  <- thanks claude

    scaled = np.clip((image[finite] - low) / (high - low), 0, 1)
    normalized[finite] = scaled ** gamma
    return normalized * 255

  def detectStars(self):
    #denoise/blur
    #edge detection
    #star detection
    #store star position and radius
    #finish
    pass