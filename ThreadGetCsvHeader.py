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
__version__ = '2020 0212 1053 Eastern'
###############################################################################

from PyQt5.QtCore import QThread, pyqtSignal
import os
import csv

class GetCsvHeaderThread(QThread):
    '''
        Thread class to get retrieve the header row from a specified CSV file
            fqpn: Fully qualified path (name) to the CSV file
        
            Returns the header as a list
    '''
    def __init__(self, fqpn=None):
        '''
            Class constructor
        '''
        QThread.__init__(self)
        self.fqpn = fqpn
    
    def __del__(self):
        '''
            Class destructor
        '''
        self.wait()

    # Signals
    # str1 is the fqpn to the invalid 'file'
    # str2 is the error message
    signalInvalidFile = pyqtSignal(str, str)
    # str is the header extracted from the csv
    # E.G. var1 name, var2 name, var3 name, ...
    signalHeaderAsList = pyqtSignal(list)
    # str contains an error message
    signalInvalidHeader = pyqtSignal(str)
    # int1 contains the progress value
    # int2 contains the maximum value
    signalProgress = pyqtSignal(int, int)
    # str1 is the class & method
    # str2 is a status messgage
    signalStatusMsg = pyqtSignal(str, str)

    def run(self):
        '''
            Executes thread
        '''
        # 1. Verify file exists
        self.signalProgress.emit(1,3)
        if self.fqpn is None:
            self.signalInvalidFile.emit(self.fqpn, 'FQPN is None')
            return
        if not os.path.isfile(self.fqpn):            
            self.signalInvalidFile.emit(self.fqpn, 'FQPN failed os.path.isfile() test')
            return

        # 2. Extract header
        self.signalProgress.emit(2,3)
        header = self.extractCsvHeader()
        
        # 3. Return header as a list
        self.signalProgress.emit(3,3)
        if header is not None:
            self.signalHeaderAsList.emit(header)

  

    def extractCsvHeader(self):
        '''
            Opens/Closes the CSV file in self.fqpn

            Returns the header as a list or None on errors
        '''

        part1 = 'GetCsvHeaderThread::extractCsvHeader():'
        part2 = 'Attempting to read headers from: ' + self.fqpn
        self.signalStatusMsg.emit(part1, part2 )
        with open(self.fqpn, 'r') as inFile:
            reader = csv.reader(inFile)
            header = []
            try:
                header = reader.next()
            except Exception as e:
                self.signalInvalidHeader.emit(e.message)
                return None
            return header