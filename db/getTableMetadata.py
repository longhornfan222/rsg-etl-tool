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
#
# REF: https://docs.sqlalchemy.org/en/13/core/tutorial.html
#
# __version__ = '2020 0215 2216'
###############################################################################

import pandas
import sqlalchemy as sa

import getDbConnection

def describeTable(tableName):
    '''
    Implements equivalent of DESCRIBE tableName 
    '''
    pks = getPrimaryKeys(tableName)
    attribs = getTableAttributes(tableName)
    if attribs is not None:        
        mergePksIntoAttributes(attribs, pks)
        return attribs
    else:
        return None

def getEngine(showEcho=False):
    '''
    Attempt to get sqlAlchemy engine using defaults
    Returns engine on success or None

    Compare to getDbConnection.getSqlalchemyEngine()
    '''
    # use defaults
    host, user, pwd, databaseName = getDbConnection.getDbConnectionParams()

    url = getDbConnection.buildSqlAlchemyEngineUrl(user, pwd, host, databaseName)
    try: 
        engine = getDbConnection.getSqlalchemyEngine(url, showEcho=showEcho)
        return engine
    except:
        print 'ERROR: getEngine(): Could not create engine. Returning...'
        return None       

def getPrimaryKeys(tableName, showEcho=False):
    '''
    Returns a list primary keys from Table tableName
    or None on failure/error    
    '''
    engine = getEngine(showEcho)
    if engine is None:
        return None

    insp = sa.inspect(engine)
    
    try:
        # As a list 
        pks = insp.get_primary_keys(tableName)
        return pks
    except Exception as e:
        print "ERROR: getTableAttributes(): " + str(e)
        return None

def mergePksIntoAttributes(attributes, primaryKeys):
    '''
    Merges primary keys into attributes list
    No error checking
    '''
    for a in attributes:            
        if a['name'] in primaryKeys:
            a['isPk'] = True
        else:
            a['isPk'] = False

def getTableAttributes(tableName, showEcho=False):
    '''
    Returns a list (of dictionaries) of attributes from Table tableName
    or None on failure/error    
    '''
    engine = getEngine(showEcho)
    if engine is None:
        return None

    insp = sa.inspect(engine)

    try:
        # As a list of dictionaries
        attributes = insp.get_columns(tableName)
        return attributes
    except Exception as e:
        print "ERROR: getTableAttributes(): " + str(e)
        return None

def showExamples(tableName, showEcho=False):
    '''
    Gets and stores SQL DESCRIBE table results from database

    https://docs.sqlalchemy.org/en/13/core/tutorial.html
    '''
    engine = getEngine(showEcho)
    if engine is None:
        return

    # Reflection
    # https://docs.sqlalchemy.org/en/13/core/reflection.html
    metadata = sa.MetaData()

    #isTable = doesTableExist(engine, metadata, tableName, showEcho)
    
    try:    
        messages = sa.Table(tableName, metadata, autoload=True, autoload_with=engine)
    except Exception as e:        
        print 'ERROR: getTableMetadata():'
        print '\t' + str(e)
        print 'Returning...'
        return None

    print [c.name for c in messages.columns]

    print '\n'
    print messages.exists
    print '\n'
    print messages.foreign_key_constraints
    print '\n'
    print messages.foreign_keys

    return messages.columns

if __name__ == '__main__':
    showExamples('sensordata')
    describeTable('sensordata')