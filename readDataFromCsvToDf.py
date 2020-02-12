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
# Last Modified: 2020 0212 1415

import pandas as pd
import os.path as ospath
import sys

def readDataFromCsvToDf(pathToCsvFile = None):
    """
        Reads data from a CSV file into pandas dataframe
        
        Output
    """
    df = None
    try:
        df = pd.read_csv(pathToCsvFile)
    except Exception as e:
        errMsg = 'ERROR readDataFromCsvToDf(): Line {}: '.format(sys.exc_info()[-1].tb_lineno) 
        errMsg += e.message 
        print errMsg
        df = None

    return df

if __name__ == "__main__":
    # Path to data for Resilient Smart Grid DDDAS (UMiami)
    pathToData = 'C:\\Users\\rdeng\\Documents\\dev\\rsg-database\\data\\Homestead\\2007'
    aCsv = 'FAWN_report.csv'

    aCsvFile = ospath.join(pathToData, aCsv)
    df = readDataFromCsvToDf(aCsvFile)

    if df is not None:
        print df.keys()
