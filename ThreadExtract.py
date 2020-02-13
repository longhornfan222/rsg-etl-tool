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
# __version__ = '2020 0213 1134'
###############################################################################

from PyQt5.QtCore import QThread, pyqtSignal
import os, sys
import csv

import pandas

import readDataFromCsvToDf

class ExtractThread(QThread):
    '''
        Thread class to get extract data from CSVs into DF

        csvList: list containing fqpns to CSV(s)
            
    '''
    def __init__(self, csvList=None):
        '''
            Class constructor
        '''
        QThread.__init__(self)
        self.csvList = csvList
    
    def __del__(self):
        '''
            Class destructor
        '''
        self.wait()

    # Signals
    # contains the extracted data in a data frame
    signalExtractComplete = pyqtSignal(pandas.DataFrame)
    # str1 is the fqpn to the invalid 'file'
    # str2 is the error message
    signalInvalidFile = pyqtSignal(str, str)    
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
        # 1. Verify files exist
        '''
        TODO
        self.signalProgress.emit(1,3)
        if self.fqpn is None:
            self.signalInvalidFile.emit(self.fqpn, 'FQPN is None')
            return
        if not os.path.isfile(self.fqpn):            
            self.signalInvalidFile.emit(self.fqpn, 'FQPN failed os.path.isfile() test')
            return
        '''
        # 2. Read Csvs
        dataAsList = self.readDataFromCsvList()
        # 3. Convert into dataframe
        self.signalProgress.emit(0,2)
        df = self.listToDf(dataAsList)
        self.signalProgress.emit(1,2)
        # 4. Return the data frame
        self.signalProgress.emit(2,2)
        self.signalExtractComplete.emit(df)


    def readDataFromCsvList(self):
        '''
            Reads data from multiple CSV files into a running list
        '''
        runningList = []
        count = 0
        length = len(self.csvList) + 1
        for aCsv in self.csvList:
            try:
                runningList.append(readDataFromCsvToDf.readDataFromCsvToDf(aCsv))
                count += 1
                self.signalProgress.emit(count, length)
            except Exception as e:
                errMsg = 'Line {}: '.format(sys.exc_info()[-1].tb_lineno) 
                errMsg += e.message 
                self.signalStatusMsg.emit('ERROR: ExtractThread()::readDataFromCsvList()', errMsg)  
                self.signalProgress.emit(1,1)              
                return None
        return runningList
        
    def listToDf(self, dataAsList):
        ''' 
            Converts a list of data to a dataframe
        '''
        try:
            df = pandas.concat(dataAsList)
            return df
        except Exception as e:
            errMsg = 'Line {}: '.format(sys.exc_info()[-1].tb_lineno) 
            errMsg += e.message 
            self.signalStatusMsg.emit('ERROR: ExtractThread()::readDataFromCsvList()', errMsg)
            return None