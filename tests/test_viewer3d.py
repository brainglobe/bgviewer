from bgviewer.viewer3d import gui
from PyQt5 import QtCore


def test_simple_launch(qtbot):
    window = gui.MainWindow()
    qtbot.addWidget(window)
    window.show()


def test_fullscreen(qtbot):
    window = gui.MainWindow(fullscreen=True)
    qtbot.addWidget(window)
    window.show()


def test_themes(qtbot):
    window = gui.MainWindow(theme="dark")
    qtbot.addWidget(window)
    window.show()

    window = gui.MainWindow(theme="light")
    qtbot.addWidget(window)
    window.show()


def test_atlas(qtbot):
    window = gui.MainWindow(atlas="allen_mouse_25um_v0.2")
    qtbot.addWidget(window)
    window.show()


def test_axes(qtbot):
    window = gui.MainWindow(axes=True)
    qtbot.addWidget(window)
    window.show()


# TODO check if this actually tests the show_hide_mesh function
def test_add_hide(qtbot):
    window = gui.MainWindow(random_colors=True)
    qtbot.addWidget(window)
    window.show()

    qtbot.mouseClick(window.hierarchy, QtCore.Qt.LeftButton)
    qtbot.mouseClick(window.hierarchy, QtCore.Qt.LeftButton)
