#
# This file is part of the Air Force Institute of Technology (AFIT) 
# Resilient Sensor Grid (RSG) Extract, Transform, Load (ETL) Tool.
#
# Written by:
#               Ryan D. L. Engle
#               ryan.engle@afit.edu, rdengle@gmail.com
#               Air Force Institute of Technology
#               Department of Systems Engineering & Management (ENV)
#               2950 Hobson Way
#               Wright Patterson AFB, Ohio  45433-7765  USA
#
# This source code is property of the United States Government.
#
# NO PART OF THIS PROGRAM MAY BE COPIED, REPRODUCED, OR DUPLICATED WITHOUT
# THE EXPRESSED WRITTEN PERMISSION FROM AFIT/ENV.
#
# # This software is provided "AS IS" and the author disclaims all warranties with 
# regard to this software. In no event shall the author be liable for any indirect 
# or consequential damages arising out of, or in connection with, the use of this 
# software. USE AT YOUR OWN RISK.
#
__version__ = '2020 0210 1750 Eastern'
###############################################################################
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
import sys

import rsg_etl_tool_ui

class RsgEtlApp(QtWidgets.QMainWindow, rsg_etl_tool_ui.Ui_MainWindow):
    def __init__(self):
        # Enable access to variables and methods in rsg_etl_tool_ui.py
        super(self.__class__, self).__init__()

        # Defined in rsg_etl_tool_ui.py. Sets up layout and widgets
        self.setupUi(self)

        # Signals and slots (http://pyqt.sourceforge.net/Docs/PyQt5/signals_slots.html)
        # Signals are connected to slots using connect(slotName)
        # File menu - Slots
        # Example
        # self.actionLoad_Signal_Set.triggered.connect(self.loadSignalSet)
        
        # Frame 1 - Buttons (slots)
        #self.butLoad.clicked.connect(self.loadSmsFiles)




def start(pathToData=None):
    app = QtWidgets.QApplication(sys.argv)
    form = RsgEtlApp()
    form.show()
    app.exec_()


if __name__ == "__main__":
    start()