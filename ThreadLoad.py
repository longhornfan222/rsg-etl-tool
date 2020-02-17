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
#__version__ = '2020 0217 0629'
###############################################################################

from PyQt5.QtCore import QThread, pyqtSignal
import os, sys

import sqlalchemy as sa

import pandas

import db.getDbConnection, db.closeDbConnection

class LoadThread(QThread):
    '''
        Thread class to load data into the database

        df: pandas data frame containing the transformed data to load

        dbTableName: name of the database table name into which the data will
            be loaded
            
    '''
    def __init__(self, df=None, dbTableName=None, showEcho=False, useLocalDb=True, userToken=0, dbName='umiami'):
        '''
            Class constructor
        '''
        QThread.__init__(self)
        self.df = df
        self.dbTableName = dbTableName

        self.showEcho = showEcho
        self.useLocalDb = useLocalDb
        self.userToken = userToken
        self.dbName = dbName        
    
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
    engine = None
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
        Attempts to connect to database. sqlalchemy manages closing connections (typically) 
        https://docs.sqlalchemy.org/en/13/core/connections.html#engine-disposal

        status: True when the connection is successful
        self.connection: stores the connection until closed
        self.engine: stores the engine 
        
        '''
        msg1 = 'LoadThread::attemptDbConnection():'
        msg2 = 'Attempting to connected to DB...'
        self.signalStatusMsg.emit(msg1, msg2)

        status, self.connection, self.engine = db.getDbConnection.getDbConnection(
            useLocalDb=self.useLocalDb, userToken=self.userToken, dbName=self.dbName,
            showEcho=self.showEcho)
        if status is False:
            msg1 = 'ERROR: LoadThread::attemptDbConnection(): '
            msg2 = 'Failed to connect to DB using defaults. Check db/dbConfig.py\n'
            msg2 += 'TODO Write failure details to log file\n'
            self.signalStatusMsg.emit(msg1, msg2)
            self.signalLoadComplete.emit(False)            
        return status

    '''
    def attemptDbLoad(self):
        ###
        Attempts to load data into database. Closes connection on failure

        status: True when successful
        ###
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
    '''

    def attemptDbLoad(self):
        '''
        Attempts to load data into database

        status: True when successful
        '''

        msg1 = 'LoadThread::attemptDbLoad():'
        msg2 = 'Attempting to load data...'
        self.signalStatusMsg.emit(msg1, msg2)

        # identify primary key (pk) -- composite?
        pkList = self.getPrimaryKey()        
        # create the table if it doesn't exist
        status = self.checkCreateTable(pkList)
        if status is False:
            return False
        msg1 = 'LoadThread::attemptDbLoad():'
        msg2 = 'Table \"' + str(self.dbTableName).lower() + '\" exists or was added.'
        self.signalStatusMsg.emit(msg1, msg2)

        # insert the data - check for failures
        msg1 = 'LoadThread::attemptDbLoad():'
        msg2 = 'Attempting to insert data...'
        self.signalStatusMsg.emit(msg1, msg2)        
        result = self.insertData()

        
        return True

    def checkCreateTable(self, pkList):
        '''
        Checks if self.dbTableName table exists or creates it

        pkList contains a list of primary keys

        Returns/updates:
        self.metadata and self.table exist
        status is true on success
        '''        
        # Create sqlalchemy metadata object
        self.metadata = sa.MetaData()
        # Define table in metadata
        self.table = sa.Table(self.dbTableName, self.metadata)

        # Add columns to table
        status = False
        for key in self.df.keys():
            # Check if primary key            
            isPk = False
            if key in pkList:                
                isPk = True
            # Get the data type
            colType = self.getType(key)
            # Define the column
            col = sa.schema.Column(str(key), colType, primary_key=isPk )
            # add the column to the table
            try:
                self.table.append_column(col)
            except Exception as e:
                status = False
                msg1 = 'LoadThread::checkCreateTable():'
                msg2 = str(e)
                self.signalStatusMsg.emit(msg1, msg2)                
                return status

        # Create table if it doesn't exist
        try:
            self.metadata.create_all(self.engine, checkfirst=True)
            status = True            
        except Exception as e:
            status = False
            msg1 = 'LoadThread::checkCreateTable():'
            msg2 = str(e)
            self.signalStatusMsg.emit(msg1, msg2)            
            status = False
        
        return status

    def getPrimaryKey(self):
        '''
        Returns a list of the attributes to use for primary key (pk)
                
        For now (FAWN Reports), location and dateTimeSampled. Revise 
        as date/requirements are better understood
        '''
        pkList = ['FAWN_Station', 'dateTimeSampled']
        return pkList    

    def getType(self, key):
        '''
        Returns a data type using the lookup dictionary and the key. Default
        is effectively varchar(100)
        '''
        # Look up dictionary
        typesDict = {
            'float64': sa.DECIMAL(17,2),
            'object': sa.String(50),
            'datetime64[ns]':sa.DateTime()
        }        
        dataType = self.df.dtypes[key]

        if str(dataType) in typesDict.keys():
            return typesDict[str(dataType)]
        else:
            # 'Default' => varchar(100)
            return sa.String(100)
        
    def insertData(self):
        '''
        Attempts to insert data in self.table 

        Returns/updates:
        self.table and the database contain the data on success
        status is true on success
        '''

        #ins = users.insert().values(firstname='Ryan', lastname='Engle')        
        # build insert statement (could execute many as dictionary)
        ins = self.table.insert()

        errCount = 0
        insertCount = 0
        dfCount = self.df.shape[0]
        # INSERT INTO person (name, balance) VALUES ('Joe', 100)
        for index, row in self.df.iterrows():            
            sql = 'INSERT INTO ' + self.dbTableName + ' ('
            # Add columns (keys)
            for key in self.df.keys():
                sql += str(key) + ', '
            # trim last ', '
            sql = sql[:-2]
            sql += ') VALUES ('
            
            for key in self.df.keys():
                if str(row[key]) == 'nan':
                    sql += ' NULL, '
                else:                    
                    # repr preserves precision when converting to string
                    # https://stackoverflow.com/questions/3481289/converting-a-python-float-to-a-string-without-losing-precision
                    sql += '\'' +  repr(row[key]) + '\', '
            sql = sql[:-2] + ')'

            # Execute insert            
            try:
                self.engine.execute(sql)
            except Exception as e:
                # should be duplicates
                print e
                errCount += 1
            
            insertCount += 1
            self.signalProgress.emit(insertCount, dfCount)
            #print insertCount, dfCount, errCount
        
        print errCount
        return True

        