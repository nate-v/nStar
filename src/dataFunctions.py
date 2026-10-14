import numpy as np
import scipy.ndimage as ndimg

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

    scaled = np.clip((image[finite] - low) / (high - low), 0, 1500)
    normalized[finite] = scaled ** gamma
    return normalized * 255

  def detectStars(self, data, kernel):
    med_data = self.medianFilterKernel(data, kernel)
    star_x, star_y, star_r = self.localMaximaDetection(med_data, kernel, 0.001)
    return star_x, star_y, star_r

  def medianFilter(self, data):
    image = np.asarray(data)
    padded = np.pad(image, 1, mode="edge")
    filtered = np.empty(image.shape, dtype=np.result_type(image.dtype, np.float64))
    for row in range(image.shape[0]):
      neighbors = np.stack([padded[row + row_offset, column:column + image.shape[1]] for row_offset in range(3) for column in range(3)], axis=0)
      filtered[row] = np.median(neighbors, axis=0)
    return filtered

  def medianFilterKernel(self, data, kernel):
    if not isinstance(kernel, (int, np.integer)) or kernel < 2 or kernel % 2 == 0:
      raise ValueError("Kernel size must be an odd integer greater than 2.")
    kernel = int(kernel)

    image = np.asarray(data)
    radius = kernel // 2
    padded = np.pad(image, radius, mode="edge")
    windows = np.lib.stride_tricks.sliding_window_view(padded, (kernel, kernel))
    return np.median(windows, axis=(-2, -1))

  def backgroundNormalization(self, data, h):
    image = np.asarray(data)
    background = np.nanmedian(image)*h
    return image - background

  def edgeDetection(self, data): # i guess useless lol
    padded = np.pad(data, 1, mode="edge")
    sobelX = np.empty(data.shape, dtype=np.result_type(data.dtype, np.float64))
    sobelY = np.empty(data.shape, dtype=np.result_type(data.dtype, np.float64))
    sobel = np.empty(data.shape, dtype=np.result_type(data.dtype, np.float64))
    G_y = np.array([
      [-1, -2, -1],
      [0, 0, 0],
      [1, 2, 1]
    ]).flatten()
    G_x = np.array([
      [-1, 0, 1],
      [-2, 0, 2],
      [-1, 0, 1]
    ]).flatten()
    for row in range(data.shape[0]):
      neighbors = np.stack([padded[row + row_offset, column:column + data.shape[1]] for row_offset in range(3) for column in range(3)], axis=0)
      sobelX[row] = np.sum(neighbors * G_x[:, None], axis=0)
      sobelY[row] = np.sum(neighbors * G_y[:, None], axis=0)
    sobel = np.sqrt(pow(sobelX, 2) + pow(sobelY, 2))
    return sobel

  def localMaximaDetection(self, data, proximity, threshold):
    dmax = ndimg.maximum_filter(data, proximity) # maximum filter
    maxima = (data == dmax) # bool mask for local max within proximity
    dmin = ndimg.minimum_filter(data, proximity)
    background = ndimg.median_filter(data, size=2 * proximity + 1)
    delta = ((dmax - dmin) > threshold) # bool mask for filter difference is greater than threshold
    maxima[~delta] = False # remove local maxima that don't satisfy min delta in proximity

    labeled = np.zeros(maxima.shape, dtype=np.int32)
    n_obj = ndimg.label(maxima, output=labeled)
    slices = ndimg.find_objects(labeled)
    x, y, r = [], [], []

    for object_id, object_slice in enumerate(slices, start=1):
      if object_slice is None:
        continue

      rows, columns = np.where(labeled[object_slice] == object_id)
      rows = rows + object_slice[0].start
      columns = columns + object_slice[1].start
      peak_index = np.argmax(data[rows, columns])
      peak_row = rows[peak_index]
      peak_column = columns[peak_index]

      peak_value = data[peak_row, peak_column]
      background_value = background[peak_row, peak_column]
      prominence = peak_value - background_value
      half_prominence = background_value + prominence / 2

      pending = [(peak_row, peak_column)]
      component = set()
      while pending:
        row, column = pending.pop()
        if (
          (row, column) in component
          or row < 0
          or row >= data.shape[0]
          or column < 0
          or column >= data.shape[1]
          or data[row, column] < half_prominence
        ):
          continue

        component.add((row, column))
        pending.extend(
          (row + row_offset, column + column_offset)
          for row_offset in (-1, 0, 1)
          for column_offset in (-1, 0, 1)
          if row_offset != 0 or column_offset != 0
        )

      x.append(float(np.mean(columns)))
      y.append(float(np.mean(rows)))
      r.append(float(np.sqrt(len(component) / np.pi)))

    return x, y, r


  # def doEverythingTemp(self, data):
  #   new_dat = self.medianFilterKernel(data, 5)
  #   new_dat = self.backgroundNormalization(new_dat, 2)
  #   new_dat = self.edgeDetection(new_dat)
  #   new_dat = self.medianFilterKernel(new_dat, 5)
  #   return new_dat