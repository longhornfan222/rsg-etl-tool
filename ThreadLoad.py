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
__version__ = '2020 0213 2208'
###############################################################################

from PyQt5.QtCore import QThread, pyqtSignal
import os, sys

import pandas

import db.getDbConnection, db.closeDbConnection

class LoadThread(QThread):
    '''
        Thread class to load data into the database

        df: pandas data frame containing the transformed data to load

        dbTableName: name of the database table name into which the data will
            be loaded
            
    '''
    def __init__(self, df=None, dbTableName=None):
        '''
            Class constructor
        '''
        QThread.__init__(self)
        self.df = df
        self.dbTableName = dbTableName
    
    def __del__(self):
        '''
            Class destructor
        '''
        self.wait()

    # Signals
    # bool is True on successful load
    signalLoadComplete = pyqtSignal(bool)
    # int1 contains the progress value
    # int2 contains the maximum value
    signalProgress = pyqtSignal(int, int)
    # str1 is the class & method
    # str2 is a status messgage
    signalStatusMsg = pyqtSignal(str, str)

    connection = None
    cursor = None

    def run(self):
        '''
        Execute
        '''
        # get connection
        if self.attemptDbConnection() is False:
            self.signalLoadComplete.emit(False)
            return
        msg1 = 'LoadThread::run():'
        msg2 = 'Successfully connected to DB'
        self.signalStatusMsg.emit(msg1, msg2)       

        # load data
        loadStatus = self.attemptDbLoad()
        if loadStatus is True:
            msg1 = 'LoadThread::run():'
            msg2 = 'Successfully loaded/update data'
            self.signalStatusMsg.emit(msg1, msg2)
        else:
            msg1 = 'LoadThread::run():'
            msg2 = 'Failed to load/update data'
            self.signalStatusMsg.emit(msg1, msg2)                      

        # close connection
        msg1 = 'LoadThread::run():'
        msg2 = 'Closing DB connection'
        self.signalStatusMsg.emit(msg1, msg2)
        db.closeDbConnection.closeDbConnection(self.cursor, self.connection)

        self.signalLoadComplete.emit(loadStatus)
            


    def attemptDbConnection(self):
        '''
        Attempts to connect to database using defaults in dbConfig.py. 

        status: True when the connection is successful
        self.connection: stores the connection until closed
        self.cursor: stores the cursor until closed
        '''
        msg1 = 'LoadThread::attemptDbConnection():'
        msg2 = 'Attempting to connected to DB...'
        self.signalStatusMsg.emit(msg1, msg2)

        status, self.connection, self.cursor = db.getDbConnection.getDbConnection()
        if status is False:
            msg1 = 'ERROR: LoadThread::attemptDbConnection(): '
            msg2 = 'Failed to connect to DB using defaults. Check db/dbConfig.py\n'
            msg2 += 'TODO Write failure details to log file\n'
            self.signalStatusMsg.emit(msg1, msg2)
            self.signalLoadComplete.emit(False)
            db.closeDbConnection.closeDbConnection(self.cursor, self.connection)
        return status

    def attemptDbLoad(self):
        '''
        Attempts to load data into database. Closes connection on failure

        status: True when successful
        '''
        msg1 = 'LoadThread::attemptDbLoad():'
        msg2 = 'Attempting to load/update data'
        self.signalStatusMsg.emit(msg1, msg2)

        try:
            self.df.to_sql(self.dbTableName, self.connection, chunksize=10000, \
                index=False, if_exists='append')
            
        except ValueError as vx:
            print vx
            return False
        except Exception as e:
            print str(e)
            return False
        else:
            print "Table %s created successfully." % self.dbTableName  
            return True  

    