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
__version__ = '2020 0213 1151'
###############################################################################

from PyQt5.QtCore import QThread, pyqtSignal
import os, sys

import datetime
import pandas

class TransformThread(QThread):
    '''
        Thread class to get extract data from CSVs into DF

        df: pandas dataframe contains the data to transform. 
        This data should not be modified
            
    '''
    def __init__(self, df=None):
        '''
            Class constructor
        '''
        QThread.__init__(self)
        self.df = df
    
    def __del__(self):
        '''
            Class destructor
        '''
        self.wait()

    # Signals
    # contains the extracted data in a data frame
    signalTransformComplete = pyqtSignal(pandas.DataFrame)
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

            Rename columns

            Convert Date and Time

            Set missing data to Null
        '''

        self.signalProgress.emit(0,3)
        self.renameColumnsForMySql()
        self.signalProgress.emit(1,3)
        if 'Observation_Time' in self.df.keys():
            self.transformFawnDateTime('Observation_Time')
            
        self.signalProgress.emit(2,3)
        self.setNull()
        self.signalProgress.emit(3,3)
        self.signalTransformComplete.emit(self.df)
###############################################################################

    def renameColumnsForMySql(self):
        '''
        Renames the keys in the data frame to comply with MySQL requirements
        '''
        newKeys = {}
        singleUnderscore = '_'
        doubleUnderscore = '__'
        for k in self.df.keys():            
            newK = str(k)
            newK = newK.replace(' ', singleUnderscore)
            newK = newK.replace('(', doubleUnderscore)
            newK = newK.replace(')', doubleUnderscore)
            newK = newK.replace('^', doubleUnderscore)
            newK = newK.replace('-', doubleUnderscore)
            newK = newK.replace('!', doubleUnderscore)
            newK = newK.replace('@', doubleUnderscore)
            newK = newK.replace('#', doubleUnderscore)
            newK = newK.replace('$', doubleUnderscore)
            newK = newK.replace('%', doubleUnderscore)
            newK = newK.replace('&', doubleUnderscore)
            newK = newK.replace('*', doubleUnderscore)
            newK = newK.replace('+', doubleUnderscore)
            newK = newK.replace('=', doubleUnderscore)
            newK = newK.replace('.', doubleUnderscore)
            newK = newK.replace('?', doubleUnderscore)
            newK = newK.replace('<', doubleUnderscore)
            newK = newK.replace('>', doubleUnderscore)

            # TODO other special characters
            newKeys[k]=newK
        
        self.df.rename(columns=newKeys, inplace=True)    



    def convertFawnDateTime(self, dt):
        '''
        Convert to datetime object
        '''
        # Mar 1 2007  1:00 AM
        return datetime.datetime.strptime(dt, "%b %d %Y  %I:%M %p")

    def transformFawnDateTime(self, dtColName):
        '''
        Adds a python datetime series to the datafram
        ''' 
        # This operation results in a pandas Series
        dateCol = self.df[dtColName]
        series = dateCol.transform(self.convertFawnDateTime)
        
        self.df['datetime'] = series

      
    def setNull(self):
        '''
        TODO
        Probably unnecessary for dataframe implemntation
        '''
        return