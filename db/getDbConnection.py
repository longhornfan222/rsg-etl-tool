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
# __version__ = '2020 0211 0800 Eastern'
###############################################################################
import MySQLdb

def getDbConnection(typeCursor):
    
    # initialize variables
    use_local_database = True
    cursor = []
    status = False

    # connect to database
    if use_local_database is True:
        # Database Server
        host = 'localhost'
        # Database Username/Password
        user = ''
        password = ''
        # Database Name
        db_name = 'MQ'
    # TODO else

    # Create the database connection object and connect
    dbConnection = MySQLdb.connect(host, user, password, db_name)
    
    if typeCursor == 'dict':
        cursor = dbConnection.cursor(MySQLdb.cursors.DictCursor)
    elif typeCursor == 'simple':
        cursor = dbConnection.cursor()

    try:
        cursor.execute("SELECT VERSION()")
        results = cursor.fetchone()
        # Check if anything at all is returned
        if results:
            status = True
        else:
            status = False
    except MySQLdb.Error, e:
        print "ERROR: dbConnect() %d IN CONNECTION: %s" % (e.args[0], e.args[1])

    return status, dbConnection, cursor

if __name__ == "__main__":
    print 'getDbConnection(): TODO implement testing'
    return