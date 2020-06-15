import napari
import json
import pandas as pd

from pathlib import Path
from napari.utils.io import magic_imread
from qtpy import QtCore
from qtpy.QtWidgets import (
    QGridLayout,
    QWidget,
    QTextBrowser,
    QLabel,
)

from bgviewer.display_region_name import display_brain_region_name
from bgviewer.gui_utils import add_button, choose_directory_dialog


class ViewerWidget(QWidget):
    def __init__(self, viewer, annotations_opacity=0.3):
        super(ViewerWidget, self).__init__()
        self.viewer = viewer
        self.annotations_opacity = annotations_opacity
        self.setup_layout()

    def setup_layout(self):
        self.instantiated = False
        layout = QGridLayout()

        self.load_atlas_button = add_button(
            "Load atlas", layout, self.load_atlas, 0, 0, minimum_width=200,
        )
        self.load_reference_button = add_button(
            "Load reference image",
            layout,
            self.load_reference,
            1,
            0,
            visibility=False,
        )
        self.load_annotated_button = add_button(
            "Load annotated image",
            layout,
            self.load_annotated,
            2,
            0,
            visibility=False,
        )

        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(4)
        self.status_label = QLabel()

        self.status_label.setText("Ready")

        layout.addWidget(self.status_label, 4, 0)

        self.info_box = QTextBrowser()
        self.info_box.setVisible(False)
        layout.addWidget(self.info_box)
        self.setLayout(layout)

    def load_atlas(self):
        self.status_label.setText("Loading...")
        directory = choose_directory_dialog(
            parent=self, prompt="Select atlas directory"
        )

        # deal with existing dialog
        if directory != "":
            self.atlas_directory = Path(directory)
            self.initialise_atlas_paths()
            self.load_structures()
            self.load_atlas_button.setText("Load new atlas")
            self.load_reference_button.setVisible(True)
            self.load_annotated_button.setVisible(True)
            self.fill_info_box()

        self.status_label.setText("Ready")

    def initialise_atlas_paths(self):
        self.metadata_path = self.atlas_directory / "metadata.json"
        self.structures_path = self.atlas_directory / "structures.json"
        self.annotated_path = self.atlas_directory / "annotation.tiff"
        self.reference_path = self.atlas_directory / "reference.tiff"
        self.meshes_dir = self.atlas_directory / "meshes"

    def load_structures(self):
        self.structures = pd.read_json(self.structures_path)

    def fill_info_box(self):
        metadata_formatted = self.load_metadata()
        self.info_box.setVisible(True)
        self.info_box.setText(metadata_formatted)

    def load_metadata(self):
        metadata_formatted = ""
        with open(self.metadata_path) as json_file:
            self.metadata = json.load(json_file)
        for item in self.metadata:
            metadata_formatted = (
                metadata_formatted + f"{item}: {self.metadata[item]}\n"
            )

        return metadata_formatted

    def load_reference(self):
        self.load_image(self.reference_path, name="Reference")

    def load_annotated(self):
        self.annotation_labels = self.load_labels(
            self.annotated_path,
            name="Annotations",
            opacity=self.annotations_opacity,
        )

        @self.annotation_labels.mouse_move_callbacks.append
        def display_region_name(layer, event):
            display_brain_region_name(layer, self.structures)

    def load_image(
        self, image_path, use_dask=True, stack=True, name=None, opacity=1
    ):
        image = self.viewer.add_image(
            magic_imread(image_path, use_dask=use_dask, stack=stack),
            name=name,
            opacity=opacity,
        )
        return image

    def load_labels(
        self, image_path, use_dask=True, stack=True, name=None, opacity=1
    ):
        labels = self.viewer.add_labels(
            magic_imread(image_path, use_dask=use_dask, stack=stack),
            name=name,
            opacity=opacity,
        )
        return labels


def main():

    with napari.gui_qt():
        viewer = napari.Viewer(title="brainglobe atlas viewer")
        viewer_widget = ViewerWidget(viewer,)
        viewer.window.add_dock_widget(
            viewer_widget, name="Atlas viewer", area="right"
        )


if __name__ == "__main__":
    main()
