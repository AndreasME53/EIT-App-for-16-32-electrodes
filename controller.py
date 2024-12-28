from ui_app import Ui_MainWindow
from checkElectrodes import generate_electrodes , adjust_electrodes, reset, Create_MsgBox
from PyQt5 import QtWidgets
from typing import Dict , List
from impedance import generate_impeadance

from Cyqiq.Presenter.Presenter.lib.Presenter import Presenter

above_threshold_color = "#ee4b2b"
bellow_threshold_color = "#aaff00"
threshold = 8

class Controller:
    def __init__(self, ui: Ui_MainWindow, MainWindow):

        reset()

        self.ui = ui 
        self.main_window = MainWindow
        self.init_pages()
        self.pages_buttons_action()
        self.electrode_number = MainWindow.electrode_number
        self.IMPEDANCE_MAX = MainWindow.IMPEDANCE_MAX
        self.amplitude = MainWindow.amplitude


    def init_pages(self):
        """_summary_"""

    def pages_buttons_action(self) -> None:
        """_summary_"""

        self.ui.get_started_pushButton.clicked.connect(
            lambda : self.ui.stackedWidget_main.setCurrentIndex(1)
        )

        # self.ui.get_started_pushButton.clicked.connect(
        #     self.get_started
        # )

        self.ui.rotate_pushButton.clicked.connect(
            self.rotate_torso
        )

        self.ui.check_connection_pushButton.clicked.connect(
            self.check_connection 

        )

        self.ui.adjust_electrodes_connection_pushButton.clicked.connect(
            self.adjust_electrodes 

        )

        self.ui.view_impedance_connection_pushButton.clicked.connect(
            self.StartMeasurementTask 
        )

        #Connect the slider's valueChanged signal to a slot
        self.ui.horizontalSlider.valueChanged.connect(self.slider_value_changed)

        self.presenter = None
        self.imageDisplayActive = False
        self.presenter_initalized = False

    def slider_value_changed(self, value):
        # Update the label text with the current slider value
        self.color_modulation_value = value * 0.1
        self.ui.labelBar.update_legend_labels(self.color_modulation_value)
        self.presenter.set_color_modulation_value(self.color_modulation_value)

    # def get_started(self):
    #     reset()
    #     self.ui.stackedWidget_main.setCurrentIndex(1)

    
    def StartMeasurementTask(self):
        self.imageDisplayActive = True

        if self.electrode_number == 16:
            self.ui.verticalSlider_xy.setVisible(False)

        # print ("Value", self.ui.verticalSlider_xy.value())

        self.ui.view_impedance_connection_pushButton.setText("Restart Measurement")
        if self.presenter_initalized:
            self.close_connection()
            self.presenter_initalized = False

        self.ui.stackedWidget.setCurrentIndex(4)
        self.ui.label_5.setVisible(False)
        self.ui.label_9.setVisible(True)
        self.ui.label_10.setVisible(True)
        self.ui.horizontalSlider.setVisible(True)
        self.ui.colorbar.setVisible(True)
        self.ui.labelBar.setVisible(True)

        # if not self.presenter_initalized:
        self.presenter = Presenter(self.ui, self.main_window)
        self.presenter.set_color_modulation_value(self.ui.horizontalSlider.value() * 0.1)
        self.presenter_initalized = True
        self.presenter.start()
        self.presenter.start_measurement()

        self.ui.view_impedance_connection_pushButton.setEnabled(True)

        #get_measurements()

    def close_connection(self):
        if self.presenter_initalized:
            # self.presenter.stop_measurement()
            self.presenter.stop()


    def check_connection(self):
        # info_box = Create_MsgBox("Checking Electrode Connections! Please Wait....")
        self.ui.check_connection_pushButton.setEnabled(False)
        (test_electrodes_values, adjusted) = generate_electrodes(self.IMPEDANCE_MAX, self.amplitude,self.electrode_number)
        self.assign_color_to_electrodes(self.ui.gridLayout_front , test_electrodes_values['front'])
        self.assign_color_to_electrodes(self.ui.gridLayout_back , test_electrodes_values['back'])
        self.assign_color_to_electrodes(self.ui.gridLayout_left , test_electrodes_values['left'])
        self.assign_color_to_electrodes(self.ui.gridLayout_right , test_electrodes_values['right'])
        # adjusted = True
        if adjusted:
            self.ui.adjust_electrodes_connection_pushButton.setEnabled(False)
            self.ui.view_impedance_connection_pushButton.setEnabled(True)
        else:
            self.ui.adjust_electrodes_connection_pushButton.setEnabled(True)
        # info_box.close()
    

    def adjust_electrodes(self):
        self.ui.adjust_electrodes_connection_pushButton.setEnabled(False)

        (test_electrodes_values, adjusted) = adjust_electrodes(self.IMPEDANCE_MAX, self.amplitude,self.electrode_number)
        self.assign_color_to_electrodes(self.ui.gridLayout_front , test_electrodes_values['front'])
        self.assign_color_to_electrodes(self.ui.gridLayout_back , test_electrodes_values['back'])
        self.assign_color_to_electrodes(self.ui.gridLayout_left , test_electrodes_values['left'])
        self.assign_color_to_electrodes(self.ui.gridLayout_right , test_electrodes_values['right'])

        # uncomment the below code when electodes are connected and proper impedance values are recevied
        if adjusted:
            self.ui.adjust_electrodes_connection_pushButton.setEnabled(False)
            self.ui.view_impedance_connection_pushButton.setEnabled(True)
        else:
            self.ui.adjust_electrodes_connection_pushButton.setEnabled(True)

        # comment / remove the below code when electodes are connected and proper impedance values are recevied
        # self.ui.adjust_electrodes_connection_pushButton.setEnabled(False)
        # self.ui.view_impedance_connection_pushButton.setEnabled(True)
    



    def rotate_torso(self):
        current_index = self.ui.stackedWidget.currentIndex()
        if self.imageDisplayActive:
            if self.electrode_number == 32:
                if current_index == 6 :
                    self.ui.stackedWidget.setCurrentIndex(4)
                else :
                    self.ui.stackedWidget.setCurrentIndex(current_index + 1)
        else:
            if current_index == 3 :
                self.ui.stackedWidget.setCurrentIndex(0)
            else :
                self.ui.stackedWidget.setCurrentIndex(current_index + 1)




    def assign_color_to_electrodes(self , gridLayout: QtWidgets.QGridLayout , test_electrodes_values: List[int]):
        # Assuming 'gridLayout' is the QGridLayout instance --- 5 k ohms
        index_electrode = 0 
        row_count = gridLayout.rowCount()
        column_count = gridLayout.columnCount()
        for row in range(row_count):
            for column in range(column_count):
                layout_item = gridLayout.itemAtPosition(row, column)
                if layout_item is not None:
                    widget = layout_item.widget()
                    if widget is not None:

                        if test_electrodes_values[index_electrode] > threshold:
                            widget.setStyleSheet(
                               f"""
                                border: none;
                                border-radius: 6px;
                                background-color : {above_threshold_color} ; 
                                """
                            )
                        else :
                            widget.setStyleSheet(
                               f"""
                                border: none;
                                border-radius: 6px;
                                background-color : {bellow_threshold_color} ; 
                                """
                            )
                        index_electrode += 1
