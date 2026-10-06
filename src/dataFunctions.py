import numpy as np

class dataFunctions:
  def normalize(self, data, low_p, high_p, gamma, reference_data=None):

    image = np.asarray(data, dtype=np.float64)
    finite = np.isfinite(image)
    reference = image if reference_data is None else np.asarray(reference_data, dtype=np.float64)
    reference_finite = np.isfinite(reference)

    low, high = np.percentile(reference[reference_finite], [low_p, high_p])
    normalized = np.full(image.shape, np.nan, dtype=np.float64) #  <- thanks claude

    if high <= low:
      low = np.min(reference[reference_finite])
      high = np.max(reference[reference_finite])
      if high <= low:
        normalized[finite] = 0
        return normalized * 255

    scaled = np.clip((image[finite] - low) / (high - low), 0, 1)
    normalized[finite] = scaled ** gamma
    return normalized * 255

  def detectStars(self, data, kernel):
    #denoise/blur
    median_data = self.medianFilterKernel(data, kernel)
    #edge detection
    #star detection
    #store star position and radius
    #finish
    pass

  def medianFilter(self, data):
    image = np.asarray(data)
    padded = np.pad(image, 1, mode="edge")
    filtered = np.empty(image.shape, dtype=np.result_type(image.dtype, np.float64))
    for row in range(image.shape[0]):
      neighbors = np.stack([padded[row + row_offset, column:column + image.shape[1]] for row_offset in range(3) for column in range(3)], axis=0)
      filtered[row] = np.median(neighbors, axis=0)
    return filtered

  def medianFilterKernel(self, data, kernel):
    if not isinstance(kernel, (int, np.integer)) or kernel < 5 or kernel % 2 == 0:
      raise ValueError("Kernel size must be an odd integer greater than 3.")
    kernel = int(kernel)

    image = np.asarray(data)
    if image.ndim != 2 or image.size == 0:
      raise ValueError("Median filter expects a non-empty 2-D image.")

    radius = kernel // 2
    padded = np.pad(image, radius, mode="edge")
    windows = np.lib.stride_tricks.sliding_window_view(padded, (kernel, kernel))
    return np.median(windows, axis=(-2, -1))

  def edgeDetection(self, data):
    pass
