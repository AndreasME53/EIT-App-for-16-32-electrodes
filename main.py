from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication
from functools import partial
import sys
from ui_app import Ui_MainWindow
from controller import Controller


class MainWindow(QMainWindow):
    def __init__(self):
        """ User can edit the Scisopecs input commands and
            if the user wished to run the program with 32
            electrode measurements or 16 electrode measurements."""
        super(MainWindow, self).__init__()
    
        ##########################################################
        ########## Sciospecs Settings and EIT App: ###############
        ##########################################################

        self.electrode_number = 32        # [32 or 16] 32 electrode system or 16 electrode system 
        self.frame_rate = 20              # [10 -- 30] the frame rate of the sciospec return measurement
        self.reference_sample_number = 30 # [1 -- 32] the reference sample number
        self.frequency = 1e4              # [1e4 -- 5e4] (hz) the AC current frequency
        self.amplitude = 1e-3             # [1e-3 -- 0.50] (Am) the AC current injection value
        self.possible_gain_list = [1, 10, 100, 1000] # The gain list
        self.gain = 1                     # [1, 10, 100, 1000] the opitional gain choices
        self.IMPEDANCE_MAX = 1000         # [1 -- inf] the threshold of the impedance value for 3D chest
        self.plot_refresh_time = 0.1      # [0.1 - 5] the refreash rate of the live EIT image plots 
        
        self.jacobian_hyperparameter_index = 6 # for 32 electrodes system
                                               # to choose hyperparameter of 
                                               # jacobian for saline tank using
                                               # skip 4 injection and skip 3 measurement
    
        ##########################################################
        ##########################################################
    
    
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        if self.electrode_number == 16:
            self.ui.radioButton.setChecked(True)
            self.ui.radioButton_2.setChecked(False)
        elif self.electrode_number == 32:
            self.ui.radioButton.setChecked(False)
            self.ui.radioButton_2.setChecked(True)

        self.controller = Controller(ui = self.ui, MainWindow=self)
        self.show()

    def closeEvent(self, event):
        self.controller.close_connection()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())