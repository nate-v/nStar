import sys

from PySide6.QtWidgets import (
  QApplication,
  QFileDialog,
  QMainWindow,
  QMessageBox,
)

from ui_nStarMainGUI import Ui_MainWindow
import displayFits

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    self.image_data = None

    self.ui.actionImport_FITS.triggered.connect(self.import_fits)
    self.ui.actionDisplay_FITS.triggered.connect(self.display_fits)

  def import_fits(self):
    file_path, _ = QFileDialog.getOpenFileName(self, "Open FITS file", "", "FITS files (*.fits *.fit *.fts);;All files (*)",)
    if not file_path:  # cancelled by user
      return

    try:
      self.image_data = displayFits.load(file_path)
    except (OSError, ValueError) as error:
      QMessageBox.critical(self, "Could not load FITS file", str(error))
      return

    self.ui.statusbar.showMessage(
      f"Loaded {file_path} — image shape: {self.image_data.shape}"
    )

  def display_fits(self): # duh what do you think this does
    pass

def main():
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  return app.exec()


if __name__ == "__main__":
  raise SystemExit(main())