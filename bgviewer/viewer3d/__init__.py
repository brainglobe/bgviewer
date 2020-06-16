from PyQt5 import QtWidgets
from bgviewer.viewer3d.gui import MainWindow
import sys
import argparse


def launch(*args, **kwargs):
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow(*args, **kwargs)
    app.aboutToQuit.connect(window.onClose)  # <-- connect the onClose event
    window.show()
    sys.exit(app.exec_())


def launch_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--full-screen",
        dest="fullscreen",
        required=False,
        default=False,
        help="Pass True to have the viewer launch in fullscreen mode",
    )

    parser.add_argument(
        "-t",
        "--theme",
        dest="theme",
        required=False,
        default="dark",
        help="'dark' or 'light' color theme'",
    )

    parser.add_argument(
        "-a",
        "--atlas",
        dest="atlas",
        required=False,
        default=None,
        help="Pass the name of a brainglobe atlas to explore with the 3d viewer",
    )

    return parser


def main():
    args = launch_parser().parse_args()

    launch(theme=args.theme, fullscreen=args.fullscreen, atlas=args.atlas)
