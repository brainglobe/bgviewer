from vedo import Plotter
from PyQt5.QtGui import QFont
from PyQt5.Qt import Qt
from PyQt5 import QtCore

import brainrender
from brainrender.Utils.camera import set_camera
from brainrender.scene import Scene
from vedo import addons

from bgviewer.viewer3d.ui import Window


brainrender.ROOT_COLOR = [0.8, 0.8, 0.8]
brainrender.BACKGROUND_COLOR = [228, 229, 230]

"""
    A pyqt5-based GUI for visualising brian regions in 3d. 
    It consistets of a 'tree' widget to explore the hierarchy of
    brain structures and an interactive brainrender Scene
    where the regions meshes are visualised
"""


class MainWindow(Scene, Window):
    # ---------------------------------- create ---------------------------------- #
    def __init__(
        self, *args, atlas=None, axes=None, random_colors=False, **kwargs
    ):
        """
            Adds brainrender/vedo functionality to the 
            pyqt5 application created in bgviewer.viewer3d.ui.Window

            Arguments
            ---------
            atlas: name of a brainatlas api atlas (or any atlas class supported by brainrender)
            random_colors: if True brain regions are assigned a random color
            axes: by default it's None, so no axes are shown. If True is passed
                Cartesian coordinates axes are shown
        """
        self.scene = Scene(*args, atlas=atlas, **kwargs)
        Window.__init__(self, *args, **kwargs)

        self.axes = axes

        # Create a new vedo plotter
        self.setup_plotter()
        self.random_colors = random_colors

        # update plotter
        self._update()

        # Add inset
        self.scene._get_inset()

    def setup_plotter(self):
        """
            Changes the scene's default plotter
            with one attached to the qtWidget in the 
            pyqt application. 
        """
        # Get embedded plotter
        new_plotter = Plotter(qtWidget=self.vtkWidget)
        self.scene.plotter = new_plotter

        # Get axes
        if self.axes:
            ax = addons.buildAxes(
                self.scene.root,
                xtitle="x [um]",
                xLabelOffset=0.07,
                xTitleOffset=0.1,
                xTitleJustify="bottom-left",
                ytitle="y [um]",
                yLabelOffset=0.025,
                yTitleOffset=0.1,
                yTitleJustify="bottom-left",
                ztitle="z [um]",
                zLabelOffset=0.025,
                zTitleOffset=0.1,
                zTitleJustify="bottom-left",
            )
            for a in ax.unpack():
                if "xtitle" in a.name or "xNumericLabel" in a.name:
                    a.RotateZ(180)

            self.scene.add_actor(ax)

        # Fix camera
        set_camera(self.scene, self.scene.camera)

    # ---------------------------------- Update ---------------------------------- #
    def show_hide_mesh(self, val):
        """
            When an item on the hierarchy tree is double clicked, the
            corresponding mesh is added/removed from the brainrender scene
        """
        # Get item
        idxs = self.hierarchy.selectedIndexes()
        if idxs:
            item = idxs[0]
        else:
            return
        item = item.model().itemFromIndex(val)

        # Get region name
        region = item.tag

        # Toggle checkbox
        if not item._checked:
            item.setCheckState(Qt.Checked)
            item._checked = True
        else:
            item.setCheckState(Qt.Unchecked)
            item._checked = False

        # Add/remove mesh
        if region == "root" or region == "grey":
            if self.scene.root is None:
                self.scene.add_root()
        else:
            if region not in self.scene.actors["regions"].keys():
                # Add region
                fnt = QFont("Open Sans", 12)
                fnt.setBold(True)
                item.setFont(fnt)

                if not self.random_colors:
                    self.scene.add_brain_regions(region)
                else:
                    self.scene.add_brain_regions(
                        region,
                        use_original_color=False,
                        colors=brainrender.colors.get_random_colors(1),
                    )
            else:
                del self.scene.actors["regions"][region]

            # Update hierarchy's item font
            item.toggle_active()

        # Update brainrender scene
        self._update()

    def _update(self):
        """
            Updates the scene's Plotter to add/remove
            meshes
        """
        self.scene.apply_render_style()

        self.scene.plotter.show(
            *self.scene.get_actors(),
            interactorStyle=0,
            bg=brainrender.BACKGROUND_COLOR,
        )

        # Fake a button press to force update
        self.scene.plotter.interactor.MiddleButtonPressEvent()
        self.scene.plotter.interactor.MiddleButtonReleaseEvent()

    # ----------------------------------- Close ---------------------------------- #
    def keyPressEvent(self, event):
        if (
            event.key() == QtCore.Qt.Key_Escape
            or event.key() == QtCore.Qt.Key_Q
        ):
            self.close()

    def onClose(self):
        """
            Disable the interactor before closing to prevent it from trying to act on a already deleted items
        """
        self.vtkWidget.close()
