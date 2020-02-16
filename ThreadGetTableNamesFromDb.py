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
#__version__ = '2020 0215 2233'
###############################################################################

from PyQt5.QtCore import QThread, pyqtSignal
import os, sys

import sqlalchemy

import db.getDbConnection

class GetTableNamesFromDbThread(QThread):
    '''
        Thread class to retrieve table names from a database                  
    '''
    def __init__(self, showEcho=False, useLocalDb=True, userToken=0, dbName='umiami'):
        '''
            Class constructor
        '''
        QThread.__init__(self)
        self.showEcho = showEcho

        self.useLocalDb = useLocalDb
        self.userToken = userToken
        self.dbName = dbName
    
    def __del__(self):
        '''
            Class destructor
        '''
        self.engine.dispose()
        self.wait()

    # Signals
    # list contains attribute metadata or None on error
    signalGetTableNamesFromDbComplete = pyqtSignal(list)
    # int1 contains the progress value
    # int2 contains the maximum value
    signalProgress = pyqtSignal(int, int)
    # str1 is the class & method
    # str2 is a status messgage
    signalStatusMsg = pyqtSignal(str, str)

    engine = None
    tableNames = []

    def run(self):
        '''
        Execute
        '''
        self.signalProgress.emit(0,3)    
        # get engine
        self.attemptToGetEngine()
        if self.engine is None:
            self.signalProgress.emit(3,3)   
            self.tableNames = []
            self.signalGetTableNamesFromDbComplete.emit(self.tableNames)          
            return
        self.signalProgress.emit(1,3)
        # check if table exists in database and describe table
        self.attemptToGetTableNames()
        if not self.tableNames:
            self.signalProgress.emit(3,3)   
            self.signalGetTableNamesFromDbComplete.emit(self.tableNames)          
            return
        # return results
        self.signalProgress.emit(3,3)   
        self.signalGetTableNamesFromDbComplete.emit(self.tableNames)

    def attemptToGetEngine(self):
        '''
        Attempts to get database engine (sqlalchemy)
        ''' 
        msg1 = 'GetTableNamesFromDbThread::attemptToGetEngine():'
        msg2 = 'Attempting to get database engine...'
        self.signalStatusMsg.emit(msg1, msg2)     
        self.getEngine()
        if self.engine is None:    
            msg1 = 'ERROR: GetTableNamesFromDbThread::attemptToGetEngine():'
            msg2 = 'Could not create engine.'
            self.signalStatusMsg.emit(msg1, msg2)      
        msg1 = 'GetTableNamesFromDbThread::attemptToGetEngine():'
        msg2 = 'Database engine created successfully'
        self.signalStatusMsg.emit(msg1, msg2)

    def attemptToGetTableNames(self):
        '''
        Attempts to get table names
        ''' 
        msg1 = 'GetTableNamesFromDbThread::attemptToGetTableNames():'
        msg2 = 'Starting...'
        self.signalStatusMsg.emit(msg1, msg2)     
        
        # explicitly set to empty
        # table names
        self.tableNames = []
        self.getTableNames()
        if not self.tableNames:
            return        
        
        msg1 = 'GetTableNamesFromDbThread::attemptToGetTableNames():'
        msg2 = 'Finished sucessfully.'
        self.signalStatusMsg.emit(msg1, msg2)     

    def getEngine(self):
        '''
        Attempt to get sqlAlchemy engine using defaults
        Returns engine on success or None

        Compare to db.getDbConnection.getSqlalchemyEngine()
        '''
        # Get engine/connection parameters
        host, user, pwd, databaseName = db.getDbConnection.getDbConnectionParams(\
            useLocalDb=self.useLocalDb, userToken=self.userToken, dbName=self.dbName)
        # Build the url
        url = db.getDbConnection.buildSqlAlchemyEngineUrl(user, pwd, host, databaseName)
        # Get the engine
        try: 
            self.engine = db.getDbConnection.getSqlalchemyEngine(url, showEcho=self.showEcho)            
        except:
            self.engine = None

    def getTableNames(self):
        '''
        Stores list of table names in self.tableNames or [] on failure/error    
        '''
        insp = sqlalchemy.inspect(self.engine)
        
        try:
            # As a list 
            self.tableNames = insp.get_table_names()
        except Exception as e:
            self.tableNames = []
            msg1 = 'ERROR: GetTableNamesFromDbThread::getTableNames():'
            msg2 = str(e)
            self.signalStatusMsg.emit(msg1, msg2)
