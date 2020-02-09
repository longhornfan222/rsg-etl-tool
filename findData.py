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
# Last Modified: 2020 0209 1430

import os, sys

def getFqpnForCsvsInFolder(folder=None):
    '''
        Searches a folder and returns a list of fully qualified paths to the CSVs
    '''
    allFqpnCsvs = None
    try:
        # Get all files in specified path
        allFilenames = os.listdir(folder)
        # Get the applicable CSVs and build the fully qualified path name
        allFqpnCsvs = [ os.path.join(folder, filename) for filename in allFilenames if filename.endswith('.csv') ]
    except Exception as e:
        errMsg = 'ERROR getFqpnForCsvsInFolder(): Line {}: '.format(sys.exc_info()[-1].tb_lineno) 
        errMsg = '\tSearch folder was: ' + str(folder)
        errMsg += e.message 
        print errMsg
        allFqpnCsvs = None    
    
    return allFqpnCsvs


def findData(pathToData = None, searchAllSubFolders = False):
    '''
        Searches for files to load

    '''
    if pathToData is None:
        print 'findData(): Invalid folder location provided (None)'
        return None

    allFqpnCsvs = None
    if searchAllSubFolders is False:
        print 'findData(): Searching only: ' + str(pathToData)               
        allFqpnCsvs = getFqpnForCsvsInFolder(pathToData)
    
    return allFqpnCsvs

if __name__ == "__main__":
    pathToData = 'C:\\Users\\rdeng\\Documents\\dev\\rsg-database\\data\\Homestead\\2007'
    
    print findData(pathToData)
