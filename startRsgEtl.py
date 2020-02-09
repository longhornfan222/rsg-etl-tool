#
# This file is part of the Air Force Institute of Technology (AFIT) 
# Resilient Sensor Grig (RSG) Extract, Transform, Load (ETL) Tool.
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
import extracter 

def startRsgEtl(pathToData=None):
    '''
        Starting point for Resilient Sensor Grid Extract, Transform, and Load tool
    '''
    # TODO GUI

    # No GUI
    searchAllSubFolders = False
    result = extracter.doExtract(pathToData, searchAllSubFolders)
    print result.info()

if __name__ == "__main__":
    pathToData = 'C:\\Users\\rdeng\\Documents\\dev\\rsg-database\\data\\Homestead\\2007'

    startRsgEtl(pathToData)

    