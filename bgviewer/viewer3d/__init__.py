from PyQt5 import QtWidgets
from bgviewer.viewer3d.gui import MainWindow
import sys


def launch(*args, **kwargs):
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow(*args, **kwargs)
    app.aboutToQuit.connect(window.onClose)  # <-- connect the onClose event
    window.show()
    sys.exit(app.exec_())
