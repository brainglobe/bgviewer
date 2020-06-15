from vedo import Plotter
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QColor
import brainrender
from brainrender.Utils.camera import set_camera
from brainrender.scene import Scene

from bgviewer.viewer3d.ui import Window



brainrender.BACKGROUND_COLOR = 'blackboard'
brainrender.ROOT_COLOR = [.8, .8, .8]

"""
    A pyqt5-based GUI for visualising brian regions in 3d. 
    It consistets of a 'tree' widget to explore the hierarchy of
    brain structures and an interactive brainrender Scene
    where the regions meshes are visualised
"""

class MainWindow(Window,  Scene):
    # ---------------------------------- create ---------------------------------- #
    def __init__(self, *args, atlas=None, **kwargs):
        """
            Adds brainrender/vedo functionality to the 
            pyqt5 application created in bgviewer.viewer3d.ui.Window
        """
        Window.__init__(self)
        Scene.__init__(self, *args, atlas=atlas, **kwargs)

        # Create a new vedo plotter
        self.setup_plotter()

        # update plotter
        self._update()


    def setup_plotter(self):
        """
            Changes the scene's default plotter
            with one attached to the qtWidget in the 
            pyqt application. 
        """
        new_plotter = Plotter(axes=None, qtWidget=self.vtkWidget)
        self.plotter = new_plotter

        # Fix camera
        set_camera(self, self.camera)

    # ---------------------------------- Update ---------------------------------- #
    def show_hide_mesh(self, val):
        """
            When an item on the hierarchy tree is double clicked, the
            corresponding mesh is added/removed from the brainrender scene
        """
        # Get time [instance of StandardItem]
        item = self.hierarchy.selectedIndexes()[0]
        item = item.model().itemFromIndex(val)

        # Get region name
        region = item.tag

        # Add/remove mesh
        if region == 'root' or region == 'grey':
            if self.root is None:
                self.add_root()
        else:
            if region not in self.actors['regions'].keys():
                # Add region
                fnt = QFont('Open Sans', 12)
                fnt.setBold(True)
                item.setFont(fnt)

                self.add_brain_regions(region)
            else:
                del self.actors['regions'][region]

            # Update hierarchy's item font
            item.toggle_active()

        # Update brainrender scene
        self._update()


    def _update(self):
        """
            Updates the scene's Plotter to add/remove
            meshes
        """
        self.apply_render_style()

        self.plotter.show(*self.get_actors(), interactorStyle=0, bg=brainrender.BACKGROUND_COLOR)

        # Fake a button press to force update
        self.plotter.interactor.MiddleButtonPressEvent()
        self.plotter.interactor.MiddleButtonReleaseEvent()

    # ----------------------------------- Close ---------------------------------- #
    def onClose(self):
        """
            Disable the interactor before closing to prevent it from trying to act on a already deleted items
        """
        self.vtkWidget.close()

