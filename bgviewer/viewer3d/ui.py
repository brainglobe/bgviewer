from PyQt5.QtWidgets import (
    QTreeView,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QMainWindow,
)
from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QFont, QColor
from PyQt5 import QtCore

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


"""
    Handles the UI for the 3d viewer based on the pyqt5 application
"""


class StandardItem(QStandardItem):
    def __init__(self, txt="", tag=None, depth=0):
        """
            Items in the tree list with some
            extended functionality to specify/update
            their look. 
        """
        super().__init__()
        self.depth = depth  # depth in the hierarchy structure
        self.tag = tag

        # Set font color/size
        fs, color = self.get_font_from_depth()
        self.bold = True  # but will be inverted
        self.toggle_active()

        # Set text
        self.setEditable(False)
        self.setForeground(color)
        self.setText(txt)

    def toggle_active(self):
        """
            When a mesh corresponding to the item's region
            get's rendered, change the font to bold
            to highlight the fact. 
        """
        self.bold = not self.bold
        fs, color = self.get_font_from_depth()

        fnt = QFont("Roboto", fs)
        fnt.setBold(self.bold)
        self.setFont(fnt)

    def get_font_from_depth(self):
        """
            Given tree depth returns
                font-size, bold, color
        """
        if self.depth < 2:
            return 16, QColor(255, 255, 255)
        elif self.depth < 5:
            return 14, QColor(220, 220, 220)
        else:
            return 12, QColor(180, 180, 180)


# ---------------------------------------------------------------------------- #
#                                   UI CLASS                                   #
# ---------------------------------------------------------------------------- #


class Window(QMainWindow):
    def __init__(self):
        """
            Create the pyqt window and the widgets
        """
        super().__init__()

        # set the title of main window
        self.setWindowTitle("Brainrender GUI")

        # set the size of window
        self.showFullScreen()

        # Change baground color
        self.setStyleSheet("background-color: rgb(40, 40, 40);")

        # add tabs
        self.tab1 = self.brainrender_canvas()
        self.initUI()

    def initUI(self):
        """
            Define overall window layout
        """
        # Left layout
        self.left_layout = QVBoxLayout()

        self.hierarchy = self.hierarchy_widget()
        self.left_layout.addWidget(self.hierarchy)
        left_widget = QWidget()
        left_widget.setLayout(self.left_layout)

        # Right layout
        self.right_widget = QTabWidget()
        self.right_widget.tabBar().setObjectName("mainTab")
        self.right_widget.addTab(self.tab1, "")
        self.right_widget.setCurrentIndex(0)
        self.right_widget.setStyleSheet(
            """QTabBar::tab{width: 0; \
            height: 0; margin: 0; padding: 0; border: none;}"""
        )

        # Put everything together
        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.right_widget)
        main_layout.setStretch(0, 80)
        main_layout.setStretch(1, 200)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def brainrender_canvas(self):
        """
            Create vtkWidget where brainrender's plotter
            will be visualised
        """
        self.vtkWidget = QVTKRenderWindowInteractor(self)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.vtkWidget)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    def hierarchy_widget(self):
        """
            Creates the structures tree hierarchy widget and populates 
            it with structures names from the brainglobe-api's Atlas.hierarchy
            tree view.
        """

        # Create QTree widget
        treeView = QTreeView()
        treeView.setExpandsOnDoubleClick(False)
        treeView.setHeaderHidden(True)
        treeView.setStyleSheet(
            "background-color: rgb(80, 80, 80); border-radius: 12px; padding: 20px 12px;"
        )

        treeModel = QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()

        # Add element's hierarchy
        tree = self.atlas.hierarchy
        items = {}
        for n, node in enumerate(tree.expand_tree()):
            # Get Node info
            node = tree.get_node(node)
            if node.tag in ["VS", "fiber tracts"]:
                continue

            # Get brainregion name
            name = self.atlas._get_from_structure(node.tag, "name")

            # Create Item
            item = StandardItem(name, node.tag, tree.depth(node.identifier))

            # Get/assign parents
            parent = tree.parent(node.identifier)
            if parent is not None:
                if parent.identifier not in items.keys():
                    continue
                else:
                    items[parent.identifier].appendRow(item)

            # Keep track of added nodes
            items[node.identifier] = item
            if n == 0:
                root = item

        # Finish up
        rootNode.appendRow(root)
        treeView.setModel(treeModel)
        treeView.expandToDepth(2)

        # Add callback
        treeView.doubleClicked.connect(self.show_hide_mesh)
        return treeView

    def keyPressEvent(self, event):
        if (
            event.key() == QtCore.Qt.Key_Escape
            or event.key() == QtCore.Qt.Key_Q
        ):
            self.close()
