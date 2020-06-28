from PyQt5.QtWidgets import (
    QTreeView,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QMainWindow,
    QLabel,
)
from PyQt5.Qt import QStandardItemModel, QStandardItem, Qt
from PyQt5.QtGui import QFont, QColor
from napari.utils.theme import palettes
import os
from pathlib import Path

from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


"""
    Handles the UI for the 3d viewer based on the pyqt5 application
"""


class StandardItem(QStandardItem):
    def __init__(self, txt="", tag=None, depth=0, color=None):
        """
            Items in the tree list with some
            extended functionality to specify/update
            their look. 
        """
        super().__init__()
        self.depth = depth  # depth in the hierarchy structure
        self.tag = tag

        # Set font color/size
        self.bold = True  # but will be inverted
        self.toggle_active()

        # Set text
        self.setEditable(False)
        rgb = color.replace(")", "").replace(" ", "").split("(")[-1].split(",")
        self.setForeground(QColor(*[int(r) for r in rgb]))
        self.setText(txt)

        # Set checkbox
        self.setFlags(
            self.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable
        )
        self.setCheckState(Qt.Unchecked)
        self._checked = False

    def toggle_active(self):
        """
            When a mesh corresponding to the item's region
            get's rendered, change the font to bold
            to highlight the fact. 
        """
        self.bold = not self.bold
        fs = self.get_font_from_depth()

        fnt = QFont("Roboto", fs)
        fnt.setBold(self.bold)
        self.setFont(fnt)

    def get_font_from_depth(self):
        """
            Given tree depth returns
                font-size, bold, color
        """
        if self.depth < 2:
            return 16
        elif self.depth < 5:
            return 14
        else:
            return 12


# ---------------------------------------------------------------------------- #
#                                   UI CLASS                                   #
# ---------------------------------------------------------------------------- #

# for ref: https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-qtreeview
tree_css = """
QTreeView {background-color: BGCOLOR; border-radius: 12px; padding: 20px 12px;} 

QTreeView::item:hover {
    background-color: TXTCOLOR; color: BGCOLOR;
}
QTreeView::item:selected {
    background-color: TXTCOLOR; color: BGCOLOR;
}
QTreeView::item:selected:active {
    background-color: TXTCOLOR; color: BGCOLOR;
}

QTreeView::item:selected:!active {
    background-color: TXTCOLOR; color: BGCOLOR;
}



QTreeView::branch:has-children:!has-siblings:closed,
QTreeView::branch:closed:has-children:has-siblings {
        border-image: none;
        image: url(CLOSED_IMG);
}

QTreeView::branch:open:has-children:!has-siblings,
QTreeView::branch:open:has-children:has-siblings  {
        border-image: none;
        image: url(OPENED_IMG);
}
QTreeView::indicator:checked {
image: url(CHECKED_IMG);
}
QTreeView::indicator:unchecked {
image: url(UNCHECKED_IMG);
} 
"""


class Window(QMainWindow):
    def __init__(self, *args, theme="dark", fullscreen=True, **kwargs):
        """
            Create the pyqt window and the widgets
        """
        super().__init__()

        if theme not in palettes.keys():
            raise ValueError(
                f"theme argument invalid: {theme}, should be either dark or light"
            )
        self.palette = palettes[theme]

        fld = Path(os.path.dirname(os.path.realpath(__file__)))
        self.palette["branch_closed_img"] = str(
            fld / "icons" / f"right_{theme}.svg"
        ).replace("\\", "/")

        self.palette["branch_opened_img"] = str(
            fld / "icons" / f"down_{theme}.svg"
        ).replace("\\", "/")

        self.palette["checked_img"] = str(
            fld / "icons" / f"checkedbox_{theme}.svg"
        ).replace("\\", "/")

        self.palette["unchecked_img"] = str(
            fld / "icons" / f"box_{theme}.svg"
        ).replace("\\", "/")

        # set the title of main window
        self.setWindowTitle("BGVIEWER")

        # set the size of window
        if fullscreen:
            self.showFullScreen()
        else:
            self.resize(1200, 700)

        # Change baground color
        self.setStyleSheet(
            "background-color: {};".format(self.palette["foreground"])
        )

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
        label = QLabel(self.scene.atlas.atlas_name)
        label.setStyleSheet(
            f'color: {self.palette["text"]}; font-weight:800; font-size:20px'
        )
        self.left_layout.addWidget(label)
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
        # Update css
        css = tree_css.replace("BGCOLOR", self.palette["background"])
        css = css.replace("TXTCOLOR", self.palette["text"])
        css = css.replace("HIGHLIGHT", self.palette["highlight"])

        css = css.replace("CLOSED_IMG", self.palette["branch_closed_img"])
        css = css.replace("OPENED_IMG", self.palette["branch_opened_img"])

        css = css.replace("UNCHECKED_IMG", self.palette["unchecked_img"])
        css = css.replace("CHECKED_IMG", self.palette["checked_img"])

        # Create QTree widget
        treeView = QTreeView()
        treeView.setExpandsOnDoubleClick(False)
        treeView.setHeaderHidden(True)
        treeView.setStyleSheet(css)
        treeView.setWordWrap(False)

        treeModel = QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()

        # Add element's hierarchy
        tree = self.scene.atlas.hierarchy
        items = {}
        for n, node in enumerate(tree.expand_tree()):
            # Get Node info
            node = tree.get_node(node)
            if node.tag in ["VS", "fiber tracts"]:
                continue

            # Get brainregion name
            name = self.scene.atlas._get_from_structure(node.tag, "name")

            # Create Item
            item = StandardItem(
                name,
                node.tag,
                tree.depth(node.identifier),
                self.palette["text"],
            )

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
        treeView.clicked.connect(self.show_hide_mesh)
        return treeView
