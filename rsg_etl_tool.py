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
# __version__ = '2020 0215 2320'
###############################################################################
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
import os, sys

import rsg_etl_tool_ui

import findData
import readCsvIntoList

import ThreadDescribeTable
import ThreadExtract
import ThreadGetCsvHeader
import ThreadGetTableNamesFromDb
import ThreadTransform
import ThreadLoad

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

        # Frame Bottom Frame - lstTablesInDb
        # Load Known Tables
        self.rpnKnownTablesCsv = rpnKnownTablesCsv
        self.assertRpnKnownTablesCsv()
        self.lstTablesInDb.clicked.connect(self.slotLstTablesInDbItemClicked)
        self.selectedTableName = ''


        # Frame Bottom Frame - tableWidgetAttributesInSelectedTable

        # Frame Bottom Frame - Buttons (slots)
        self.butPopulate.clicked.connect(self.slotButPopulateClicked)
        

        # Set initial GUI state
        self.isDataFolderSet = False
        self.isPerformingEtl=False
        self.isDescribingTable=False
        self.isTableSelected = False

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

        # Currently selected table metadata
        self.currentTableMetaData = []


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
        self.loadKnownTablesFromDb()


    def checkState(self):
        '''
            Checks various GUI states and updates functionality accordingly
        '''
        self.checkStateLstTablesInDb()
        self.checkStateNewTableButton()
        self.checkStateOpenFolderButton()
        self.checkStatePopulate()
        
    def checkStateLstTablesInDb(self):
        ''' 
        Checks whether lstTablesInDb should be enabled
        ''' 
        if self.isPerformingEtl is True or self.isDescribingTable is True:
            self.lstTablesInDb.setEnabled(False)
        else:
            self.lstTablesInDb.setEnabled(True)

    def checkStateNewTableButton(self):
        ''' 
        Checks whether NewTableButton should be enabled
        '''
        if self.isPerformingEtl is True or self.isDescribingTable is True:
            self.butNewTable.setEnabled(False)
        else:
            self.butNewTable.setEnabled(True)
        

    def checkStateOpenFolderButton(self):
        '''
        Checks whether Open Folder button should be enabled
        '''
        if self.isPerformingEtl is True or self.isDescribingTable is True:
            self.butOpenFolder.setEnabled(False)
        else:
            self.butOpenFolder.setEnabled(True)

    def checkStatePopulate(self):
        '''
            Checks whether Populate button should be enabled
        '''
        # TODO
        msg = 'checkStatePopulate(): Check:\n'
        msg += '1. A dataFolder is selected, (Done)\n'
        msg += '2. One or more files are selected *** TODO (Just do them all otherwise)\n'
        msg += '3. A table is selected *** TODO\n'
        msg += '4. ETL is not occuring (Done)\n'
        #print msg

        if self.isDataFolderSet is True and \
            (self.isPerformingEtl is False and self.isDescribingTable is False)\
            and self.isTableSelected is True:
            self.butPopulate.setEnabled(True)
        else:
            self.butPopulate.setEnabled(False)
        
    def extractDataFromCsvToDf(self):
        '''
            Extracts data from CSVs and loads into a pandas dataframe
        '''
        # Just do all csvs for now
                
        # define and start a thread to open csv and get the header
        self.extractThread = ThreadExtract.ExtractThread(self.fqpnFileList)
        # connect the signals to slots
        self.extractThread.signalExtractComplete.connect(self.slotExtractComplete)
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
        '''
        Combines label and item to produce fqpn

        Returns fqpn
        '''
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
                self.isDataFolderSet=True
                self.checkState()
            else:
                msg = 'WARNING initDataFolder(): Command line-specified data folder was invalid. '
                msg += 'Click Open Folder to specify a valid folder.'
                print msg
                self.dataFolder = None
                self.lblSelectedDataFolder.setText(lblMsg)
        else:
            self.lblSelectedDataFolder.setText(lblMsg)

    def loadDfInDatabase(self):
        '''' 
        Implements Load process of ETL
        '''        
        # Get the table into which data will be inserted
        if self.selectedTableName == '':
            return

        # define and start a thread 
        self.loadThread = ThreadLoad.LoadThread(self.transformedDf, self.selectedTableName)
        # connect the signals to slots
        self.loadThread.signalLoadComplete.connect(self.slotLoadComplete)
        self.loadThread.signalProgress.connect(self.slotUpdatePbProgressBar)
        self.loadThread.signalStatusMsg.connect(self.slotStatusMessage)
        # Start
        self.loadThread.start()

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

    def loadKnownTablesFromDb(self):
        '''
        Retrieves Table Names from DB
        '''
        # define and start a thread to interact with DB
        self.tableNamesThread = ThreadGetTableNamesFromDb.GetTableNamesFromDbThread()
        # connect the signals to slots
        self.tableNamesThread.signalGetTableNamesFromDbComplete.connect(self.slotGetTableNamesFromDbComplete)
        self.tableNamesThread.signalProgress.connect(self.slotUpdatePbProgressBar)
        self.tableNamesThread.signalStatusMsg.connect(self.slotStatusMessage)
        # Start
        self.tableNamesThread.start()

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
        # TODO Needs more error checking
        self.loadFilesIntoList()
        self.isDataFolderSet=True
        self.checkState()


    def slotButPopulateClicked(self):
        '''
        Implements Populate Button Clicked
        '''
        self.isPerformingEtl=True
        self.checkState()
        # Extract data from CSV to df
        self.extractDataFromCsvToDf()
        # everything following is asynchronous..

    def slotDescribeTableComplete(self, describeData):
        '''
        '''
        self.isDescribingTable=False
        self.checkState()
        # update attributes table widget if not empty
        self.currentTableMetaData = describeData
        self.updateTableWidgetAttributesInSelectedTable()
            
    
    def slotExtractComplete(self, df):
        '''
        Implements end of Extract and initiates Transform
        '''
        self.extractedDataDf = df
        #print self.extractedDataDf
        # Think about second progress bar
        if self.extractedDataDf is not None:
            self.transformDataInDf()

    def slotGetTableNamesFromDbComplete(self, tableNames):
        '''
        Updates tablenames with database data
        '''
        if tableNames:
            for name in tableNames:
                self.tableNames.append(name)
            # remove duplicates        
            self.tableNames = list(set(self.tableNames))        
            self.updateLstTablesInDb()

    def slotInvalidFile(self, fileName, errorMsg):
        '''# TODO'''
        print 'slotInvalidFile(): ' + fileName + ' ' + errorMsg
        return

    def slotInvalidHeader(self, errorMsg):
        '''# TODO'''
        print 'slotInvalidHeader(): '  + errorMsg
        return

    def slotLoadComplete(self, status):
        '''
        Implements ETL end actions
        '''
        self.isPerformingEtl=False
        self.checkState()
        

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

    def slotLstTablesInDbItemClicked(self, item):
        '''
        Slot to handle single click in this list
        Checks db for data and loads Table attributes in Attributes Table Widget
        '''
        # disable populate button
        self.isDescribingTable=True
        # set selected table
        self.isTableSelected = True
        self.checkState()

        # Store the table name
        self.selectedTableName = item.data()

        # define and start a thread to interact with DB
        self.describeTableThread = ThreadDescribeTable.DescribeTableThread(self.selectedTableName)
        # connect the signals to slots
        self.describeTableThread.signalDescribeTableComplete.connect(self.slotDescribeTableComplete)
        self.describeTableThread.signalProgress.connect(self.slotUpdatePbProgressBar)
        self.describeTableThread.signalStatusMsg.connect(self.slotStatusMessage)
        # Start
        self.describeTableThread.start()

    def slotStatusMessage(self, entityAsString, message):
        '''
            Enables threads to pass status messages for printing, etc.
        '''
        print entityAsString + ' ' +  message
    

    def slotTransformComplete(self, df):
        '''
        Implements end of transform and initiates Load
        '''
        self.transformedDf = df
        self.loadDfInDatabase()

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

    def transformDataInDf(self):
        '''
            Transforms data in dataframe following extract process
            
            Rename columns

            Separate Date and Time

            Set missing data to Null
        '''
        # define and start a thread 
        self.tranformThread = ThreadTransform.TransformThread(self.extractedDataDf)
        # connect the signals to slots
        self.tranformThread.signalTransformComplete.connect(self.slotTransformComplete)
        self.tranformThread.signalProgress.connect(self.slotUpdatePbProgressBar)
        self.tranformThread.signalStatusMsg.connect(self.slotStatusMessage)
        # Start
        self.tranformThread.start()

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

    def updateTableWidgetAttributesInSelectedTable(self):
        '''
        Updates attribute table with data in self.currentTableMetaData
        '''
        # Clear
        self.tableWidgetAttributesInSelectedTable.clearContents()
        self.tableWidgetAttributesInSelectedTable.setRowCount(0)
        # Fixes some bugs by disabling sorting here
        self.tableWidgetAttributesInSelectedTable.setSortingEnabled(False)        
        # Begin inserting
        currentRowCount = self.tableWidgetAttributesInSelectedTable.rowCount()
        for row in self.currentTableMetaData:
            currentRowCount = self.tableWidgetAttributesInSelectedTable.rowCount()
            self.tableWidgetAttributesInSelectedTable.insertRow(currentRowCount)
            attribName = row['name']
            self.tableWidgetAttributesInSelectedTable.setItem(currentRowCount, \
                0, QtWidgets.QTableWidgetItem(attribName))
            d1 = str(row['type'])
            self.tableWidgetAttributesInSelectedTable.setItem(currentRowCount, \
                1, QtWidgets.QTableWidgetItem(d1))            
            nullable = str(row['nullable'])
            self.tableWidgetAttributesInSelectedTable.setItem(currentRowCount, \
                2, QtWidgets.QTableWidgetItem(nullable))            
            isPk = str(row['isPk'])
            self.tableWidgetAttributesInSelectedTable.setItem(currentRowCount, \
                3, QtWidgets.QTableWidgetItem(isPk))            
            defaultValue = str(row['default'])
            self.tableWidgetAttributesInSelectedTable.setItem(currentRowCount, \
                4, QtWidgets.QTableWidgetItem(defaultValue))
        # Re-enable sorting
        self.tableWidgetAttributesInSelectedTable.setSortingEnabled(True)

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