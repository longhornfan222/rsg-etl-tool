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
__version__ = '2020 0210 2100 Eastern'
###############################################################################
from PyQt5 import QtWidgets
import os, sys

 # Recall previously selected folder or choose new folder
def getFolder(parent, previousFolder=None):
    '''
        Prompts user with dialog to select folder
    '''
    folder = None
    widgetTitle = 'Data Folder'
    if previousFolder is None:
        folder = QtWidgets.QFileDialog(parent)
    else:
        folder = QtWidgets.QFileDialog.getExistingDirectory( widgetTitle, previousFolder )

    # determine if folder is valid
    is_a_directory = os.path.isdir(folder)
    directory_exists = os.path.exists(folder)
    if (is_a_directory is False) or (directory_exists is False):            
        msg = 'getFolder(): ERROR: Invalid directory (' + str(folder) +') selected.'
        print msg
        folder = None
    
    return folder

