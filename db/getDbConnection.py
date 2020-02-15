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
# __version__ = '2020 0215 1148'
###############################################################################
import MySQLdb

import sqlalchemy

import dbConfig
# dbconfig is not tracked by git
import closeDbConnection # For testing

def getMysqlPackageConnection(host, user, pwd, databaseName):
    '''
    Uses MySQLdb package 
    '''
    try:
        dbConnection = MySQLdb.connect(host, user, pwd, databaseName)
        if typeCursor == 'dict':
            cursor = dbConnection.cursor(MySQLdb.cursors.DictCursor)
        elif typeCursor == 'simple':
            cursor = dbConnection.cursor()
    except Exception as e:
        print "ERROR: getDbConnection(): " + str(e)
        # TODO Write log on failure
        return False, None, None
    
    try:
        cursor.execute("SELECT VERSION()")
        results = cursor.fetchone()
        # Check if anything at all is returned
        if results:
            status = True
        else:
            status = False
    except MySQLdb.Error, e:
        print "ERROR: getDbConnection() %d IN CONNECTION: %s" % (e.args[0], e.args[1])
        return False, None, None

def buildSqlAlchemyEngineUrl(user, pwd, host, databaseName, driver='mysql'):
    '''
    #Password encoding
    #import urllib.parse
    #urllib.parse.quote_plus("kx%jj5/g")
    #'kx%25jj5%2Fg'
    #URL:
    #dialect+driver://username:password@host:port/database
    # default
    #engine = create_engine('mysql://scott:tiger@localhost/foo')
    # mysqlclient (a maintained fork of MySQL-Python)
    #engine = create_engine('mysql+mysqldb://scott:tiger@localhost/foo')
    # PyMySQL
    #engine = create_engine('mysql+pymysql://scott:tiger@localhost/foo')

    Compare to getTableMetadata.getEngine()
    '''
    # Build URL
    url = driver + '://' + user + ':' + pwd + '@' + host + '/' + databaseName
    print 'buildSqlAlchemyEngineUrl(): URL: ' + url
    return url


def getSqlalchemyEngine(url, showEcho=False):
    '''
    Returns sqlalchemy engine on success or None
    '''
     # Engine
    engine = sqlalchemy.create_engine(url, echo=showEcho)
    return engine


def getSqlalchemyConnection(user, pwd, host, databaseName, showEcho=False):
    '''
    Uses sqlalchemy package
    
    Returns
    status, connection, engine
    '''
    url = buildSqlAlchemyEngineUrl(user, pwd, host, databaseName)
    engine = getSqlalchemyEngine(url)

    # Connection
    status = False
    try:
        connection = engine.connect()
        status = True
        return status, connection, engine
    except Exception as e:
        print str(e)
        return status, None, None

def getDbConnectionParams(useLocalDb=True, userToken=0, dbName='umiami'):
    '''
    Gets connection parameters from dbConfig
    
    useLocalDb: True if using local, false if not 
    userToken: userId/token to identify the user name 
    dbName: name of the database

    Returns
    hostname, userid, password, databaseName
    '''
    # Database Server
    host = dbConfig.getHost(useLocal=useLocalDb)
    # Database Username/Password
    user = dbConfig.getUser(userToken=userToken)
    pwd  = dbConfig.getSecurityCheck(user)
    # Database Name
    databaseName = dbConfig.getDatabaseName(dbName)
           
    return host, user, pwd, databaseName

def getDbConnection(typeCursor='simple', useLocalDb=True, userToken=0, dbName='umiami', \
    verbose=False, dbPackage='sqlalchemy', showEcho=False):
    '''
    Tries to connect to a database
        typeCursor: simple or dict type of cursor
        useLocalDb: True if using local, false if not 
        userToken: userId/token to identify the user name 
        dbName: name of the database
        verbose: print some debugging info
        dbPackage: mysqldb, sqlalchemy, pymysql, etc
        showEcho: sqlalchemy-show db communications

    Returns
        status: True on success
        dbConnection: connection to the database
        cursor: cursor object (mysqldb only)
    '''

    host, user, pwd, databaseName = getDbConnectionParams(useLocalDb, userToken, dbName)

    if verbose is True:
        print host, user, pwd, databaseName

    # Create the database connection object and connect
    status = False
    dbConnection = None
    cursor = None
    if dbPackage == 'mysqldb':
        status, dbConnection, cursor = getMysqlPackageConnection(host, user, pwd, databaseName)
        return status, dbConnection, cursor
    elif dbPackage == 'sqlalchemy':        
        status, dbConnection, engine = getSqlalchemyConnection(user, pwd, host, databaseName, showEcho=showEcho)
        return status, dbConnection, engine

if __name__ == "__main__":
    status, dbConnection, cursor = getDbConnection(verbose=True, showEcho=True)
    print status, type(dbConnection), type(cursor)
    if status is True:
        closeDbConnection.closeDbConnection(cursor, dbConnection)
        #closeDbConnection.closeDbConnection(None, None)
    