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

    fullscreen_parser = parser.add_mutually_exclusive_group(required=False)
    fullscreen_parser.add_argument('--fullscreen', dest='fullscreen', action='store_true')
    fullscreen_parser.add_argument('--no-fullscreen', dest='fullscreen', action='store_false')
    parser.set_defaults(fullscreen=False)

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

    randomcolors_parser = parser.add_mutually_exclusive_group(required=False)
    randomcolors_parser.add_argument('--randomcolors', dest='randomcolors', action='store_true')
    randomcolors_parser.add_argument('--no-randomcolors', dest='randomcolors', action='store_false')
    parser.set_defaults(randomcolors=False)


    axes_parser = parser.add_mutually_exclusive_group(required=False)
    axes_parser.add_argument('--axes', dest='axes', action='store_true')
    axes_parser.add_argument('--no-axes', dest='axes', action='store_false')
    parser.set_defaults(axes=False)

    return parser


def main():
    args = launch_parser().parse_args()

    launch(
        theme=args.theme,
        fullscreen=args.fullscreen,
        atlas=args.atlas,
        random_colors=args.randomcolors,
        axes=args.axes
    )
