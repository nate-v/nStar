import sys

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
    self.gamma = 0.5
    self.applyStretch = False

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
      self.image_data = displayFits.load(file_path)
    except (OSError, ValueError) as error:
      QMessageBox.critical(self, "Could not load FITS file", str(error))
      return

    self.ui.statusbar.showMessage(f"{file_path}")
    self.show_fits(self.image_data)

  def show_fits(self, data):
    if self.applyStretch:
      norm_data = dataFunctions.dataFunctions().normalize(data, 1.0, 99.5, self.gamma)
    else:
      norm_data = data
    if self.fits_window is None:
      self.fits_window = FitsDisplayWindow(norm_data)
    else:
      self.fits_window.set_image_data(norm_data)

    self.fits_window.show()

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