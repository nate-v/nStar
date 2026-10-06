import sys

import numpy as np
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
  QApplication,
  QFileDialog,
  QMainWindow,
  QMessageBox,
)

import dataFunctions
import displayFits
from ui_nStarMainGUI import FitsDisplayWindow, Ui_MainWindow

class MainWindow(QMainWindow):

  def __init__(self):
    super().__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    self.image_data = None
    self.filtered_image_data = None
    self.median_filter_enabled = False
    self.gamma = 0.5
    self.applyStretch = False

    self.median_filter_action = QAction("Median filter", self)
    self.median_filter_action.setCheckable(True)
    self.median_filter_action.setChecked(False)
    self.median_filter_action.toggled.connect(self.toggle_median_filter)
    self.ui.menuData.addAction(self.median_filter_action)

    self.ui.actionImport_FITS.triggered.connect(self.import_fits)
    self.ui.actionIncrease.triggered.connect(self.increase_gamma)
    self.ui.actionDecrease.triggered.connect(self.decrease_gamma)
    self.ui.actionDefault.triggered.connect(self.default_gamma)
    self.ui.actionApply.triggered.connect(self.apply_stretch)
    self.ui.actionRemove.triggered.connect(self.remove_stretch)
    self.ui.actionDisplay_FITS.triggered.connect(self.display_fits)
    self.ui.actionView_parameters.triggered.connect(self.view_parameters)


    self.fits_window = None

  def import_fits(self):
    file_path, _ = QFileDialog.getOpenFileName(self, "Open FITS file", "", "FITS files (*.fits *.fit *.fts);;All files (*)",)
    if not file_path:  # cancelled by user
      return

    try:
      image_data = displayFits.load(file_path)
      filtered_image_data = dataFunctions.dataFunctions().medianFilterKernel(image_data, 7)
    except (OSError, ValueError) as error:
      QMessageBox.critical(self, "Could not load FITS file", str(error))
      return

    self.image_data = image_data
    self.filtered_image_data = filtered_image_data
    self.ui.statusbar.showMessage(f"{file_path}")
    self.show_fits(self.image_data)

  def show_fits(self, data):
    reference_data = self.image_data if self.image_data is not None else data

    if self.median_filter_enabled and self.filtered_image_data is not None:
      display_data = self.filtered_image_data
    else:
      display_data = data

    if self.applyStretch:
      norm_data = dataFunctions.dataFunctions().normalize(
        display_data, 1.0, 99.5, self.gamma, reference_data=reference_data
      )
      vmin, vmax = 0, 255
    else:
      norm_data = display_data
      finite_pixels = reference_data[np.isfinite(reference_data)]
      vmin, vmax = finite_pixels.min(), finite_pixels.max()
      if vmin == vmax:
        vmin, vmax = vmin - 0.5, vmax + 0.5
    
    if self.fits_window is None:
      self.fits_window = FitsDisplayWindow(norm_data, vmin, vmax)
    else:
      self.fits_window.set_image_data(norm_data, vmin, vmax)
    self.fits_window.show()

  def toggle_median_filter(self, enabled):
    self.median_filter_enabled = enabled
    if self.image_data is not None:
      self.show_fits(self.image_data)

  def display_fits(self):
    if self.image_data is None:
      QMessageBox.critical(self, "No image imported.", str("No image imported."))
      return
    self.show_fits(self.image_data)

  def increase_gamma(self):
    if self.image_data is not None and self.gamma < 1.0:
      self.gamma = min(1.0, self.gamma + 0.1)
      self.show_fits(self.image_data)

  def decrease_gamma(self):
    if self.image_data is not None and self.gamma > 0.1:
      self.gamma = max(0.1, self.gamma - 0.1)
      self.show_fits(self.image_data)

  def default_gamma(self):
    if self.image_data is not None:
      self.gamma = 0.5
      self.show_fits(self.image_data)

  def apply_stretch(self):
    if self.image_data is None:
      return
    self.applyStretch = True
    self.show_fits(self.image_data)

  def remove_stretch(self):
    if self.image_data is None:
      return
    self.applyStretch = False
    self.show_fits(self.image_data)

  def view_parameters(self):
    if self.applyStretch:
      QMessageBox.about(self, "Stretch parameters", f"low p: 1.0\nhigh p: 99.5\ngamma: {self.gamma}")
    else:
      QMessageBox.about(self, "Stretch parameters", "No stretch applied")


def main():
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  return app.exec()


if __name__ == "__main__":
  raise SystemExit(main())