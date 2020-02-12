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
__version__ = '2020 0212 1652 Eastern'
###############################################################################
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
import os, sys

import rsg_etl_tool_ui

import findData
import readCsvIntoList

import ThreadGetCsvHeader
import ThreadExtract

class RsgEtlApp(QtWidgets.QMainWindow, rsg_etl_tool_ui.Ui_MainWindow):
    '''
        Implements the RSG ETL Tool GUI

        rpnKnownTablesCsv: relative path name (rpn) to the file containing the known tables CSV

        fqpnToData: fully qualified path name to a folder containing CSVs for ETL
    '''
    def __init__(self, rpnKnownTablesCsv, fqpnToData=None ):
        # Enable access to variables and methods in rsg_etl_tool_ui.py
        super(self.__class__, self).__init__()

        # Defined in rsg_etl_tool_ui.py. Sets up layout and widgets
        self.setupUi(self)

        # Signals and slots (http://pyqt.sourceforge.net/Docs/PyQt5/signals_slots.html)
        # Signals are connected to slots using connect(slotName)
        
        # Frame Top Frame - Buttons (slots)
        self.butOpenFolder.clicked.connect(self.slotButOpenFolderClicked)

        # Frame Top Frame - Lists (slots)
        self.lstFilesInFolder.clicked.connect(self.slotLstFilesInFolderClicked)

        # Frame Bottom Frame - Lists
        # Known Tables
        self.rpnKnownTablesCsv = rpnKnownTablesCsv
        self.assertRpnKnownTablesCsv()

        # Frame Bottom Frame - Buttons
        self.butPopulate.clicked.connect(self.slotButPopulateClicked)
        

        # Set initial GUI state
        # Disable buttons
        self.butNewTable.setEnabled(False)
        self.butPopulate.setEnabled(False)
        # Reset progress bar
        self.pbProgressBar.setMaximum(1)
        self.pbProgressBar.setValue(0)

        # Data Folder
        self.dataFolder = fqpnToData 
        self.initDataFolder()

        # Other variables
        if self.dataFolder is None:
            self.fqpnFileList = []


###############################################################################

    def assertRpnKnownTablesCsv(self):
        '''
        '''
        errMsg = 'ERROR: assertRpnKnownTablesCsv(): Invalid known tables file: '
        errMsg += str(self.rpnKnownTablesCsv)
        errMsg += '\nExiting...'

        if self.rpnKnownTablesCsv is None:
            print errMsg
            exit()
        if not os.path.isfile(self.rpnKnownTablesCsv):
            print errMsg
            exit()
        self.loadKnownTablesCsvIntoList()


    def checkState(self, isDataFolderSet=False):
        '''
            Checks various GUI states and updates functionality accordingly
            TODO
        '''
        self.checkStatePopulate(isDataFolderSet)

    def checkStatePopulate(self, isDataFolderSet=False):
        '''
            Checks whether Populate button should be enabled
        '''
        msg = 'TODO: checkStatePopulate(): Check:\n1. A dataFolder is selected,'
        msg += '\n2. one or more files are selected,'
        msg += '\n3. and a table is selected'
        print msg

        if isDataFolderSet is True:
            self.butPopulate.setEnabled(True)
        
    def extractDataFromCsvToDf(self):
        '''
            Extracts data from CSVs and loads into a pandas dataframe
        '''
        # Just do all csvs for now
                
        # define and start a thread to open csv and get the header
        self.extractThread = ThreadExtract.ExtractThread(self.fqpnFileList)
        # connect the signals to slots
        self.extractThread.signalExtractedData.connect(self.slotUpdateExtractedData)
        self.extractThread.signalProgress.connect(self.slotUpdatePbProgressBar)
        self.extractThread.signalStatusMsg.connect(self.slotStatusMessage)
        # Start
        self.extractThread.start()


    def getFolder(self, previousFolder=None):
        '''
            Prompts user with dialog to select folder
        '''
        widgetTitle = 'Data Folder'
        if previousFolder is None:
            previousFolder = '.'
    
        fqpn = None
        # Option 1
        fqpn, cwd = QtWidgets.QFileDialog.getOpenFileName(self, widgetTitle, previousFolder)
        # Option 2
        #folder = QtWidgets.QFileDialog.getExistingDirectory(self, widgetTitle, previousFolder)
        # Get the folder name 
        # WARNING Remove if using option 2 above
        folder = os.path.dirname(fqpn)

        # determine if folder is valid
        is_a_directory = os.path.isdir(folder)
        directory_exists = os.path.exists(folder)
        if (is_a_directory is False) or (directory_exists is False):            
            msg = 'getFolder(): WARNING: Invalid directory (' + str(folder) +') selected.'
            print msg
            folder = None
        
        return folder    

    def getFqpnFromListItem(self, item):
        fqpn = os.path.join(self.lblSelectedDataFolder.text(), item.data())
        return fqpn


    def initDataFolder(self):
        '''
            Initializes data folder if specified at command line during class creation
        '''
        lblMsg = 'Please select a folder to open'
        if self.dataFolder is not None:            
            msg = 'initDataFolder(): Attempting to use command line-specified folder: '
            msg += str(self.dataFolder) 
            print msg
            # Verify data folder is a valid folder
            if os.path.isdir(self.dataFolder):
                print 'initDataFolder(): Initializing with folder ' + self.dataFolder
                self.lblSelectedDataFolder.setText(self.dataFolder)
                self.loadFilesIntoList()
                self.checkState(isDataFolderSet=True)
            else:
                msg = 'WARNING initDataFolder(): Command line-specified data folder was invalid. '
                msg += 'Click Open Folder to specify a valid folder.'
                print msg
                self.dataFolder = None
                self.lblSelectedDataFolder.setText(lblMsg)
        else:
            self.lblSelectedDataFolder.setText(lblMsg)


    def loadFilesIntoList(self):
        '''
            Uses self.dataFolder as folder to load Files Into List
        '''
        self.fqpnFileList = findData.findData(self.dataFolder)
        self.updateLstFilesInFolder()

    def loadKnownTablesCsvIntoList(self):
        ''' 
            Load tables names from csv file to tables in DB list
        '''
        # Read csv into a python list
        self.tableNames = readCsvIntoList.readCsvIntoList(self.rpnKnownTablesCsv)
        # Munge table names to MySQL
        if self.tableNames is not None:
            # TODO validate
            pass
            
        else:
            errMsg = 'ERROR: loadKnownTablesCsvIntoList(): Error loading Table Names in ' 
            errMsg += self.rpnKnownTablesCsv
            exit()
        # Put data from csv into rsg-etl-tool gui list
        self.updateLstTablesInDb()

    def slotButOpenFolderClicked(self):
        '''
            Slot to handle Open Folder button click
        '''
        folder = self.getFolder(self.dataFolder)
        if folder is None:
            # Verify this is the expected behavior.. Consider cancel action
            return

        # Update GUI
        self.dataFolder = folder
        self.lblSelectedDataFolder.setText(self.dataFolder)
        # Fill list with files & update gui list
        # Needs more error checking
        self.loadFilesIntoList()

        self.checkState(isDataFolderSet=True)


    def slotButPopulateClicked(self):
        '''
            Implements Populate Button Clicked
        '''
        # Extract data from CSV to df
        self.extractDataFromCsvToDf()
        # Tranform data in df
        #self.transformDataInDf()
        # Load data into DB
        #self.loadDataToDb()
        return

    def slotInvalidFile(self, fileName, errorMsg):
        '''# TODO'''
        print 'slotInvalidFile(): ' + fileName + ' ' + errorMsg
        return

    def slotInvalidHeader(self, errorMsg):
        '''# TODO'''
        print 'slotInvalidHeader(): '  + errorMsg
        return

    def slotLstFilesInFolderClicked(self,item):
        '''
            Slot to handle single click in lstFilesinFolder
            Populates columns in selected file list
            Creates a thread to open the selected file
        '''
        
        fqpn = self.getFqpnFromListItem(item)
        
        # define and start a thread to open csv and get the header
        self.getCsvHeaderThread = ThreadGetCsvHeader.GetCsvHeaderThread(fqpn)
        # connect the signals to slots
        self.getCsvHeaderThread.signalHeaderAsList.connect(self.slotUpdateColumnsInSelectedFileList)
        self.getCsvHeaderThread.signalInvalidFile.connect(self.slotInvalidFile)
        self.getCsvHeaderThread.signalInvalidHeader.connect(self.slotInvalidHeader)
        self.getCsvHeaderThread.signalProgress.connect(self.slotUpdatePbProgressBar)
        self.getCsvHeaderThread.signalStatusMsg.connect(self.slotStatusMessage)
        self.getCsvHeaderThread.start()

        return

    def slotStatusMessage(self, entityAsString, message):
        '''
            Enables threads to pass status messages for printing, etc.
        '''
        print entityAsString + ' ' +  message

    def slotUpdatePbProgressBar(self, progressAmount=0, maximumAmount=0):
        '''
            updates progress bar
        '''
        self.pbProgressBar.setMaximum(maximumAmount)
        self.pbProgressBar.setValue(progressAmount)

    def slotUpdateColumnsInSelectedFileList(self, header):
        '''
            Updates columns in selected file list list :) with data from header
        '''
        # Clear list
        self.lstColumnsInSelectedFile.clear()
        for col in header:
            self.lstColumnsInSelectedFile.addItem(col)

    def slotUpdateExtractedData(self, df):
        self.extractedDataDf = df
        print self.extractedDataDf

    def updateLstTablesInDb(self):
        '''
            Updates lstTablesInDb 
        '''
        self.lstTablesInDb.clear()
        self.tableNames.sort()
        for tableName in self.tableNames:
            self.lstTablesInDb.addItem(tableName)

    def updateLstFilesInFolder(self):
        '''
            Updates lstFilesInFolder using fqpn data from self.fileList
        '''
        self.lstFilesInFolder.clear()
        for f in self.fqpnFileList:
            self.lstFilesInFolder.addItem(os.path.basename(f))

        

def start(rpnKnownTablesCsv, pathToData=None):
    '''
        Starts the application execution loop
        TODO fully implement pathToData
    '''
    app = QtWidgets.QApplication(sys.argv)
    form = RsgEtlApp(rpnKnownTablesCsv, pathToData)
    form.show()
    app.exec_()

if __name__ == "__main__":
    fqpnToData = 'C:\\Users\\rdeng\\OneDrive\\01 AFIT\\Projects\\01 DDDAS\\UMiami_Data\\Fort Lauderdale\\2007'
    rpnKnownTablesCsv = os.path.join('mysql', 'knownTables.csv')
    #rpnKnownTablesCsv = None
    #start(rpnKnownTablesCsv, fqpnToData)
    start(rpnKnownTablesCsv)