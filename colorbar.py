from Generic.Model.Data.File.lib.MatlabFile import MatlabFile
import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsTextItem
from PyQt5.QtCore import Qt, QRect, QRectF
from PyQt5.QtGui import QImage, QBrush
import cairo
import pathlib

class ImageColorbar(QGraphicsView):
    def __init__(self, parent, x, y, w, h, show_colorbar, show_labels):
        super().__init__(parent=parent)

        self.show_colorbar = show_colorbar 
        self.show_labels = show_labels

        self.file_path = pathlib.Path(__file__).parent.resolve()
        self.color_array_path = str(pathlib.Path.joinpath(self.file_path, "Cyqiq", "View", "GUI", "ImageColorbar", "lib", "resources", "Colormap.mat"))

        self.setScene(QGraphicsScene())

        self.colormap = None
        self.colormap_maximum_index = None
        self.b_colormap_function = None
        self.g_colormap_function = None
        self.r_colormap_function = None
        self.a_colormap_function = None
        self.initialize_colormap()

        self.colorbar = QImage()
        self.initialize_surface_cairo()

        self.setGeometry(QtCore.QRect(x, y, w, h))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        # print(self.size())
        # print("Image Size:", self.colorbar.size())
        # print("Scene Rectangle Size:", self.sceneRect())
        self.setMaximumSize(QtCore.QSize(w, h))

        self.graphicsScene = self.scene()
        self.scene_width = self.sceneRect().width()

        # Remove the outline or border of the QGraphicsView
        self.setFrameShape(QGraphicsView.NoFrame)
        self.setFrameShadow(QGraphicsView.Plain)

        if self.show_labels:
            # Set the background brush of the scene to be transparent
            self.setBackgroundBrush(Qt.transparent)

            # Set the viewport of the QGraphicsView to have a transparent background
            self.setViewport(None)

            # Set the background color of the viewport to be transparent
            self.setStyleSheet("background: transparent;")

            self.update_legend_labels(1.0)



    # Initializer
    def initialize_colormap(self):
        colormap_array_dict = MatlabFile.open(self.color_array_path)
        colormap = np.squeeze(colormap_array_dict["map"]) * 255
        colormap = colormap[1:]
        colormap = np.hstack([colormap, np.ones([colormap.shape[0], 1]) * 255])
        colormap[:] = colormap[:, [2, 1, 0, 3]]
        colormap = np.vstack([np.array([255, 255, 255, 255]), colormap, np.array([255, 255, 255, 255])])
        self.colormap = colormap.astype(np.uint8)
        self.colormap_maximum_index = self.colormap.shape[0] - 1

    def initialize_surface_cairo(self):
        width_orig = self.colormap.shape[0]
        width = self.colormap.shape[0]
        height = 1
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        image_rgba = surface.get_data()

        image_rgba[:] = self.colormap[:].flatten()
        surface.mark_dirty()

        # Convert Cairo surface to QImage
        image_data = surface.get_data()
        image_format = QImage.Format_ARGB32

        width = image_data.shape[0]
        factor = 1.51
        image = QImage(image_data, width, height, image_format)
        scaled_image = image.scaled(width_orig*factor, 1, Qt.AspectRatioMode.IgnoreAspectRatio)
        
        rect = QRect(0, 0, width_orig*factor, height)
        self.colorbar = scaled_image.copy(rect)

        self.setSceneRect(0, 0, width_orig*0.375, height)
        if self.show_colorbar:
            self.setBackgroundBrush(QBrush(self.colorbar))        

    def update_legend_labels(self, colorbar_value):
        self.graphicsScene.clear()

        legend_values = np.linspace(-1 * colorbar_value, colorbar_value, 6)
        zero_percent_label_text = "{:.2f}".format(legend_values[0])
        twenty_percent_label_text = "{:.2f}".format(legend_values[1])
        fourty_percent_label_text = "{:.2f}".format(legend_values[2])
        sixty_percent_label_text = "{:.2f}".format(legend_values[3])
        eighty_percent_label_text = "{:.2f}".format(legend_values[4])
        hundred_percent_label_text = "{:.2f}".format(legend_values[5])

        self.draw_text(0, zero_percent_label_text)
        self.draw_text(20, twenty_percent_label_text)
        self.draw_text(40, fourty_percent_label_text)
        self.draw_text(60, sixty_percent_label_text)
        self.draw_text(80, eighty_percent_label_text)
        self.draw_text(100, hundred_percent_label_text)    

    def draw_text(self, pos, label):
        # Calculate the x-coordinates based on the percentages
        x_coord = self.scene_width * pos/100.0
        y_coord = -0.0

        if pos==100:
            x_coord -= 40

        # Create QGraphicsTextItems at the desired percentages
        text_item = QGraphicsTextItem(label)
        text_item.setPos(x_coord, y_coord)
        text_item.setFlag(QGraphicsTextItem.ItemIgnoresTransformations)  # Ensures the text is not affected by transformations

        # Add the text items to the scene
        self.graphicsScene.addItem(text_item)


        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    x = 0
    y = 0
    w = 1130
    h = 61
    colorbar = ImageColorbar(window, x, y,      w, h, show_colorbar=True, show_labels=False)
    labelBar = ImageColorbar(window, x, y+h,    w, 20, show_colorbar=False, show_labels=True)

    labelBar.update_legend_labels(colorbar_value=50)

    window.setGeometry(QtCore.QRect(x, y, w, h+20))

    window.show()
    sys.exit(app.exec_())
