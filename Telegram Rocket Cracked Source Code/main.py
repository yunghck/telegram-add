from ui.ui_mainMenu import Ui_MainMenu
from setup import SetupClass
from scraper import ScraperClass
from addToGroup import AddToGroupClass
from bulkSend import BulkSendClass
from applicationData import ApplicationData
from settings import SettingsClass
from licensing import LicensingClass
from PyQt5 import QtCore, QtGui, QtWidgets
from assets.assets import icon
from io import BytesIO
from PIL import Image, ImageQt
from datetime import datetime
import sys
import csv
import time
import asyncio
import os
import platform
import base64
import python_socks
import json

class MainMenuClass:
    setupClass = SetupClass()
    scraperClass = ScraperClass()
    addToGroupClass = AddToGroupClass()
    applicationData = ApplicationData()
    settingsClass = SettingsClass()
    licensingClass = LicensingClass()
    bulksendClass = BulkSendClass()
    IsAddingRun = False
    IsSendMessageRun = False
    IsSendFileRun = False

    def InitializeWindow(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.wMainMenu = QtWidgets.QMainWindow()
        byte_data = base64.b64decode(icon)
        image_data = BytesIO(byte_data)
        image = Image.open(image_data)
        qImage = ImageQt.ImageQt(image)
        image = QtGui.QPixmap.fromImage(qImage)
        self.wMainMenu.setWindowIcon(QtGui.QIcon(image))
        self.ui_mainMenu = Ui_MainMenu()
        self.ui_mainMenu.setupUi(self.wMainMenu)
        self.ui_mainMenu.statusbar.addPermanentWidget(QtWidgets.QLabel(self.applicationData.version))
        self.wMainMenu.setFixedSize(self.wMainMenu.size())
        self.ui_mainMenu.btnScrap.clicked.connect(self.BtnScrap_click)
        self.ui_mainMenu.btnAddToGroup_auto.clicked.connect(self.BtnAddToGroupAuto_click)
        self.ui_mainMenu.btnBulkSendMessage.clicked.connect(self.BtnBulkSendMessage_click)
        self.ui_mainMenu.btnBulkSendFile.clicked.connect(self.BtnBulkSendFile_click)
        self.ui_mainMenu.btnEditMessage.clicked.connect(self.BtnEditMessage_click)
        self.ui_mainMenu.actionSettings.triggered.connect(self.ActionSettings_click)
        self.ui_mainMenu.actionUpdateLicense.triggered.connect(self.ActionUpdateLicense_click)
        self.ui_mainMenu.actionResetLastUsed.triggered.connect(self.ActionResetLastUsed_click)
        self.ui_mainMenu.actionAbout.triggered.connect(self.ActionAbout_click)
        self.ui_mainMenu.actionExit.triggered.connect(self.ActionExit_click)
        self.ui_mainMenu.actionCheckUpdate.triggered.connect(self.ActionCheckUpdate_click)
        self.ui_mainMenu.actionImportBackup.triggered.connect(self.ActionImportBackup_click)
        self.ui_mainMenu.actionExportBackup.triggered.connect(self.ActionExportBackup_click)
        self.ui_mainMenu.btnAddNumber.clicked.connect(self.BtnAddNewNumber_click)
        self.ui_mainMenu.btnDeleteNumber.clicked.connect(self.BtnDeleteNumber_click)
        self.ui_mainMenu.btnSelectAll.clicked.connect(self.BtnSelectAll_click)
        self.ui_mainMenu.btnDeselectAll.clicked.connect(self.BtnDeselectAll_click)
        self.LoadNumbersTable()
        self.QtSetDarkMode(self.wMainMenu)
        self.scraperClass.InitializeWindow(self)
        self.addToGroupClass.InitializeWindow(self)
        self.bulksendClass.InitializeWindow(self)
        self.settingsClass.InitializeWindow(self)
        #self.licensingClass.InitializeWindow(self, image)
        self.licensingClass.InitializeUpdateLicenseWindow(self, image)
        
        self.wMainMenu.show()
        #self.mainMenuClass.wMainMenu.show()
        #self.settingsClass.DisplayReleaseNotes(self.mainMenuClass)
        #self.CheckForUpdate(True)
        
        
        sys.exit(self.app.exec_())


    def LoadNumbersTable(self):
        rows = { }
        if os.path.isfile('./phone_numbers_database.csv') and os.access('./phone_numbers_database.csv', os.R_OK):
            with open('./phone_numbers_database.csv', encoding='UTF-8') as f:
                rows = list(csv.reader(f, delimiter=',', lineterminator='\n'))
        else:
            with open('./phone_numbers_database.csv', 'x', encoding='UTF-8') as f:
                filewriter = csv.writer(f, csv.QUOTE_MINIMAL, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                filewriter.writerow([
                    'phone number',
                    'user id',
                    'access hash',
                    'last used'])
            with open('./phone_numbers_database.csv', encoding='UTF-8') as f:
                rows = list(csv.reader(f, ',', '\n', ('delimiter', 'lineterminator')))
        #rows.remove(rows[0])
        qtModel = QtGui.QStandardItemModel()
        self.ui_mainMenu.tblPhoneNumbers.setModel(qtModel)
        qtModel.setHorizontalHeaderItem(0, QtGui.QStandardItem('phone number'))
        qtModel.setHorizontalHeaderItem(1, QtGui.QStandardItem('user id'))
        qtModel.setHorizontalHeaderItem(2, QtGui.QStandardItem('last used'))
        self.ui_mainMenu.tblPhoneNumbers.setColumnWidth(0, 130)
        self.ui_mainMenu.tblPhoneNumbers.setColumnWidth(1, 100)
        self.ui_mainMenu.tblPhoneNumbers.setColumnWidth(2, 150)
        for row in rows:
            if row == []:
                continue
            column1 = QtGui.QStandardItem(str(row[0]))
            column2 = QtGui.QStandardItem(str(row[1]))
            column3 = QtGui.QStandardItem(str(row[3]))
            arrCol = [
                column1,
                column2,
                column3]
            qtModel.appendRow(arrCol)


    def BtnScrap_click(self):
        selectionModel = self.ui_mainMenu.tblPhoneNumbers.selectionModel()
        selectedRows = selectionModel.selectedRows()
        if selectionModel.hasSelection() == False:
            self.QtShowWarning('Please select at least one phone number!')
        elif selectionModel.selectedRows().__len__() > 1:
            self.QtShowWarning('Please select only one number to scrap from!\nScrap only supports one number at a time.')
        else:
            self.QtClearLog()
            userId = selectedRows[0].sibling(selectedRows[0].row(), 1).data()
            self.setupClass.ConfigSetup_byUserId(userId, True, self)
            self.scraperClass.ScrapMembers()
            self.LoadNumbersTable()


    def BtnAddToGroupAuto_click(self):
        if self.IsAddingRun:
            self.ui_mainMenu.btnAddToGroup_auto.setText('ADD')
            self.QtLog_color('Stopping... Please Wait', '#de3210')
            QtCore.QCoreApplication.processEvents()
            self.IsAddingRun = False
            self.addToGroupClass.client.disconnect()
        else:
            selectionModel = self.ui_mainMenu.tblPhoneNumbers.selectionModel()
            selectedRows = selectionModel.selectedRows()

            try:
                defaultGroup = self.settingsClass.ReadJSONKey('defaultGroup')
                if defaultGroup == '':
                    self.QtShowWarning('Default group cannot be empty, you can edit the default group in the settings')
            finally:
                return None
            self.QtShowWarning('Cannot read default group setting key!')
            return None
            if selectionModel.hasSelection() == False:
                self.QtShowWarning('Please select at least one phone number!')
            else:
                self.QtClearLog()
                self.ui_mainMenu.btnAddToGroup_auto.setText('STOP')
                self.IsAddingRun = True
                QtCore.QCoreApplication.processEvents()
                for index in range(0, selectedRows.__len__()):

                    try:
                        userId = selectedRows[index].sibling(selectedRows[index].row(), 1).data()
                        boolConfig = self.setupClass.ConfigSetup_byUserId(userId, False, self)
                        if boolConfig:
                            self.addToGroupClass.AddToGroup('members.csv', True)
                    except Exception:
                        self.QtLog('\n')
                        self.QtLog_color(type(e).__name__ + ': ' + str(e), '#de3210')
                        continue
                    finally:
                        if self.IsAddingRun:
                            self.QtLog_color('Last row of phone number has been reached', '#de3210')
                            self.QtLog_color('The task has completed,you may choose new task or Kindly refresh it and try again !', '#de3210')
                            self.ui_mainMenu.btnAddToGroup_auto.setText('ADD')
                            self.IsAddingRun = False

                        return None




    def BtnBulkSendMessage_click(self):
        if self.IsSendMessageRun:
            self.ui_mainMenu.btnBulkSendMessage.setText('BULK SEND MESSAGE')
            self.QtLog_color('Stopping... Please Wait', '#de3210')
            QtCore.QCoreApplication.processEvents()
            self.IsSendMessageRun = False
            self.bulksendClass.client.disconnect()
        else:
            selectionModel = self.ui_mainMenu.tblPhoneNumbers.selectionModel()
            selectedRows = selectionModel.selectedRows()
            if selectionModel.hasSelection() == False:
                self.QtShowWarning('Please select at least one phone number!')
            else:
                self.QtClearLog()
                self.ui_mainMenu.btnBulkSendMessage.setText('STOP')
                self.IsSendMessageRun = True
                QtCore.QCoreApplication.processEvents()
                for index in range(0, selectedRows.__len__()):

                    try:
                        userId = selectedRows[index].sibling(selectedRows[index].row(), 1).data()
                        boolConfig = self.setupClass.ConfigSetup_byUserId(userId, False, self)
                        if boolConfig:
                            self.bulksendClass.BulkSendMessage('members.csv', True)
                    except Exception:
                        self.QtLog('\n')
                        self.QtLog_color(type(e).__name__ + ': ' + str(e), '#de3210')
                        continue
                    finally:
                        if self.IsSendMessageRun:
                            self.QtLog_color('Last row of phone number has been reached', '#de3210')
                            self.QtLog_color('The task has completed,you may choose new task or Kindly refresh it and try again !', '#de3210')
                            self.ui_mainMenu.btnBulkSendMessage.setText('BULK SEND MESSAGE')
                            self.IsSendMessageRun = False

                        return None



    def BtnBulkSendFile_click(self):
        if self.IsSendFileRun:
            self.ui_mainMenu.btnBulkSendFile.setText('BULK SEND IMAGE')
            self.QtLog_color('Stopping... Please Wait', '#de3210')
            QtCore.QCoreApplication.processEvents()
            self.IsSendFileRun = False
            self.bulksendClass.client.disconnect()
        else:
            selectionModel = self.ui_mainMenu.tblPhoneNumbers.selectionModel()
            selectedRows = selectionModel.selectedRows()
            if selectionModel.hasSelection() == False:
                self.QtShowWarning('Please select at least one phone number!')
            else:
                self.QtClearLog()
                self.ui_mainMenu.btnBulkSendFile.setText('STOP')
                self.IsSendFileRun = True
                QtCore.QCoreApplication.processEvents()
                for index in range(0, selectedRows.__len__()):

                    try:
                        userId = selectedRows[index].sibling(selectedRows[index].row(), 1).data()
                        boolConfig = self.setupClass.ConfigSetup_byUserId(userId, False, self)
                        if boolConfig:
                            self.bulksendClass.BulkSendFile('members.csv', True)
                    except Exception:
                        self.QtLog('\n')
                        self.QtLog_color(type(e).__name__ + ': ' + str(e), '#de3210')
                        continue
                    finally:
                        if self.IsSendFileRun:
                            self.QtLog_color('Last row of phone number has been reached', '#de3210')
                            self.QtLog_color('The task has completed,you may choose new task or Kindly refresh it and try again !', '#de3210')
                            self.ui_mainMenu.btnBulkSendFile.setText('BULK SEND FILE')
                            self.IsSendFileRun = False

                        return None



    def BtnEditMessage_click(self):
        self.bulksendClass.wSaveMessage.show()


    def BtnSelectAll_click(self):
        self.ui_mainMenu.tblPhoneNumbers.selectAll()


    def BtnDeselectAll_click(self):
        self.ui_mainMenu.tblPhoneNumbers.clearSelection()


    def BtnAddNewNumber_click(self):
        self.settingsClass.ui_AddNumber.AppId.clear()
        self.settingsClass.ui_AddNumber.HashCode.clear()
        self.settingsClass.ui_AddNumber.phoneNumber.clear()
        self.settingsClass.wAddNumber.show()


    def BtnDeleteNumber_click(self):
        selectionModel = self.ui_mainMenu.tblPhoneNumbers.selectionModel()
        selectedRows = selectionModel.selectedRows()
        if selectionModel.hasSelection() == False:
            self.QtShowWarning('Please select at least one phone number!')
        else:
            reply = QtWidgets.QMessageBox.question(self.wMainMenu, 'Are you sure?', 'Selected numbers will be deteled.', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                rows = { }
                with open('./phone_numbers_database.csv', encoding='UTF-8') as f:
                    rows = list(csv.reader(f, delimiter=',', lineterminator='\n'))
                    for selectedIndex in range(0, selectedRows.__len__()):
                        phoneNumber = selectedRows[selectedIndex].sibling(selectedRows[selectedIndex].row(), 0).data()
                        userId = selectedRows[selectedIndex].sibling(selectedRows[selectedIndex].row(), 1).data()
                        for rowIndex in range(0, rows.__len__()):
                            if rows[rowIndex][1] == userId:
                                rows.remove(rows[rowIndex])
                                if os.path.exists(phoneNumber + '.session'):
                                    os.remove(phoneNumber + '.session')
                if not None:
                    pass
                with open('./phone_numbers_database.csv', 'w', encoding='UTF-8') as f:
                    writer = csv.writer(f, delimiter=',', lineterminator='\n')
                    for row in rows:
                        phone = row[0]
                        id = row[1]
                        hash = row[2]
                        lastUsed = row[3]
                        writer.writerow([
                            phone,
                            id,
                            hash,
                            lastUsed])
                if not None:
                    pass
                self.LoadNumbersTable()


    def ActionSettings_click(self):
        self.settingsClass.LoadSettings()
        self.settingsClass.wSettings.show()


    def ActionUpdateLicense_click(self):
        self.settingsClass.LoadSettings()
        self.licensingClass.wUpdateLicensing.show()


    def ActionResetLastUsed_click(self):
        self.msgBox = QtWidgets.QMessageBox()
        self.msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        self.QtSetDarkMode(self.msgBox)
        returnValue = self.msgBox.question(self.msgBox, 'Warning', 'Are you sure to refresh?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if returnValue == QtWidgets.QMessageBox.Yes:
            rows = { }
            with open('./phone_numbers_database.csv', encoding='UTF-8') as f:
                rows = list(csv.reader(f, delimiter=',', lineterminator='\n'))
            if not None:
                pass
            with open('./phone_numbers_database.csv', 'w', encoding='UTF-8') as f:
                writer = csv.writer(f, delimiter=',', lineterminator='\n')
                for row in rows:
                    phone = row[0]
                    id = row[1]
                    hash = row[2]
                    lastUsed = ''
                    writer.writerow([
                        phone,
                        id,
                        hash,
                        lastUsed])
            if not None:
                pass
            self.LoadNumbersTable()


    def ActionExit_click(self):
        self.wMainMenu.close()


    def ActionAbout_click(self):
        message = '<b style="font-size:15px">Telegram Rocket</b><br>\n        License Key:\n        ' + "Cracked" + ' <br>\n        License Expiry:\n        ' + "never" + '  <br>\n        Version: \n        ' + self.applicationData.version + '<br>\n        OS:\n        ' + platform.system() + ' ' + os.name.title() + ' ' + platform.release() + ' <br>\n        Website: <a href="https://www.telegramrocket.com">www.telegramrocket.com</a> <br>\n        Support: <a href="mailto:admin@telegramrocket.com">admin@telegramrocket.com</a>\n        '
        self.QtShowAbout("", message)
        return
        
        key = ''
        expiry = ''

        try:
            key = self.settingsClass.ReadJSONKey('licenseKey')
            expiry = self.settingsClass.ReadJSONKey('expiry')
        finally:
            pass
        e = None

        try:
            key = 'Not Activated'
            expiry = 'None'
        finally:
            e = None
            del e
        e = None
        del e
        daysRemaining = self.licensingClass.CalculateExpiry()


        strTimeDiffrence = '\xe2\x88\x9e days remaining' if daysRemaining == -1 else str(daysRemaining) + ' days remaining'
        title = 'Telegram Rocket'
        message = '<b style="font-size:15px">Telegram Rocket</b><br>\n        License Key:\n        ' + key + ' <br>\n        License Expiry:\n        ' + expiry + ' (' + strTimeDiffrence + ') <br>\n        Version: \n        ' + self.applicationData.version + '<br>\n        OS:\n        ' + platform.system() + ' ' + os.name.title() + ' ' + platform.release() + ' <br>\n        Website: <a href="https://www.telegramrocket.com">www.telegramrocket.com</a> <br>\n        Support: <a href="mailto:admin@telegramrocket.com">admin@telegramrocket.com</a>\n        '
        self.QtShowAbout(title, message)


    def ActionCheckUpdate_click(self):
        self.licensingClass.CheckForUpdate(False)


    def ActionImportBackup_click(self):
        reply = QtWidgets.QMessageBox.question(self.wMainMenu, 'Import Backup', 'Importing a backup will override the existing configuration files, proceed?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.settingsClass.ImportBackup(self, False)
            self.LoadNumbersTable()


    def ActionExportBackup_click(self):
        reply = QtWidgets.QMessageBox.question(self.wMainMenu, 'Export Backup', 'Configuration files such as members and phone numbers will exported into a zip file.', QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if reply == QtWidgets.QMessageBox.Ok:
            self.settingsClass.ExportBackup()


    def QtShowWarning(self, message):
        self.msgBox = QtWidgets.QMessageBox.warning(self.wMainMenu, 'Warning', message)
        QtCore.QCoreApplication.processEvents()


    def QtShowInformation(self, title, message):
        self.msgBox = QtWidgets.QMessageBox().information(self.wMainMenu, title, message)
        QtCore.QCoreApplication.processEvents()


    def QtShowAbout(self, title, message):
        self.msgBox = QtWidgets.QMessageBox()
        self.msgBox.about(self.wMainMenu, title, message)
        self.QtSetDarkMode(self.msgBox)
        QtCore.QCoreApplication.processEvents()


    def QtLog(self, messsage):
        self.ui_mainMenu.textLogger.setTextColor(QtGui.QColor('white'))
        self.ui_mainMenu.textLogger.append(messsage)
        QtCore.QCoreApplication.processEvents()


    def QtLog_color(self, messsage, color):
        self.ui_mainMenu.textLogger.setTextColor(QtGui.QColor(str(color)))
        self.ui_mainMenu.textLogger.append(messsage)
        QtCore.QCoreApplication.processEvents()


    def QtClearLog(self):
        self.ui_mainMenu.textLogger.clear()
        QtCore.QCoreApplication.processEvents()


    def QtSetDarkMode(self, element):
        darkModeToggle = self.settingsClass.ReadJSONKey('setDarkMode')
        if darkModeToggle == 'Enabled':
            element.setStyleSheet('QPushButton{ background-color: #666666; color: #ffffff}QPushButton:Disabled{ background-color: #474747; color: #555555;}QTextBrowser{ background-color: #000000;}QTableView{ background-color: #000000; color: #ffffff;}QListView{ background-color: #000000; color: #ffffff;}QMessageBox{ background-color: #555555; color: #ffffff;}QLabel{ color: #ffffff;}QGroupBox{ background-color: #555555;color: #ffffff;}')
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor('#ffffff'))
            palette.setColor(QtGui.QPalette.Button, QtGui.QColor('#555555'))
            palette.setColor(QtGui.QPalette.Light, QtGui.QColor('#7f7f7f'))
            palette.setColor(QtGui.QPalette.Midlight, QtGui.QColor('#6a6a6a'))
            palette.setColor(QtGui.QPalette.Dark, QtGui.QColor('#2a2a2a'))
            palette.setColor(QtGui.QPalette.Mid, QtGui.QColor('#393939'))
            palette.setColor(QtGui.QPalette.Text, QtGui.QColor('#ffffff'))
            palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor('#ffffff'))
            palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor('#ffffff'))
            palette.setColor(QtGui.QPalette.Base, QtGui.QColor('#000000'))
            palette.setColor(QtGui.QPalette.Window, QtGui.QColor('#555555'))
            palette.setColor(QtGui.QPalette.Shadow, QtGui.QColor('#000000'))
            palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor('#308cc6'))
            palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor('#ffffff'))
            palette.setColor(QtGui.QPalette.Link, QtGui.QColor('#0000ff'))
            palette.setColor(QtGui.QPalette.LinkVisited, QtGui.QColor('#ff00ff'))
            palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor('#2a2a2a'))
            palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor('#ffffdc'))
            palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor('#000000'))
            palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtGui.QColor('#555555'))
            element.setPalette(palette)


if __name__ == '__main__':
    mainMenuClass = MainMenuClass()
    mainMenuClass.InitializeWindow()