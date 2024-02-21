"""
    Script Name: IT_ExportDataTool
    Author: Gabe Wong, Technical Artist

    Usage:
    This tool will go through a selection and store the transform data into an external text file that will later
    be read by a secondary tool in UE4. It's the first step in the process of auto populating assets in the UE4 editor.

"""

import ConfigParser
import os

import pymel.core as pm
from PySide2 import QtWidgets
from maya import OpenMayaUI as omui
from maya import cmds
from shiboken2 import wrapInstance

import IT_GlobalVar

# Get and store the path to the data file, and the full path including file name.
# TODO: move this out of the cadet folders to user path
dataFilePath = os.path.join(os.path.dirname(__file__), '../../../config/')
dataFileFull = os.path.normpath(os.path.join(dataFilePath, 'it_export_dataFile.ini'))

# Check if the directory exists and if not, create it.
dirExists = os.path.isdir(dataFilePath)
if not dirExists:
    os.mkdir(dataFilePath)
    # TODO: move to unified itoys_mayatools logging
    IT_GlobalVar.logger.info("Config directory doesn't exist.  Creating it.")
config = ConfigParser.RawConfigParser()


def getMayaMainWindow():
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    return ptr


class RunExportDataTool(QtWidgets.QDialog):
    def __init__(self):
        # region
        try:
            pm.deleteUI('exportDataTool')
        except:
            print('No previous UI exists')
        parent = QtWidgets.QDialog(parent=getMayaMainWindow())
        parent.setObjectName('exportDataTool')
        # The parent variable below allows the tool window to stay in Maya and not be hidden in the background.
        super(RunExportDataTool, self).__init__(parent=parent)
        self.setWindowTitle('IT_ExportDataTool')

        # Get the geometry of the screen/resolution, the center point, then move the new window upper left corner.
        qtRectangle = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.buildUI()

        # endregion

    def buildUI(self):
        # region
        layout = QtWidgets.QGridLayout(self)
        layout.setVerticalSpacing(10)
        layout.setColumnMinimumWidth(0, 200)
        layout.setColumnMinimumWidth(1, 200)

        self.textSourceName = QtWidgets.QLineEdit()
        self.textSourceName.setPlaceholderText("Enter asset name as it's spelled in UE4 content browser.")
        layout.addWidget(self.textSourceName, 0, 0, 1, 2)

        btnAddMeshData = QtWidgets.QPushButton('Add Mesh Data')
        btnAddMeshData.clicked.connect(self.exportData)
        btnAddMeshData.setToolTip(
            'Select all top-level groups you want to export transform data for before clicking this button.  Can be pre or post conversion.')
        layout.addWidget(btnAddMeshData, 1, 0)

        btnLoadMeshName = QtWidgets.QPushButton('Load Mesh Name')
        btnLoadMeshName.clicked.connect(self.loadMeshName)
        btnLoadMeshName.setToolTip(
            'Select the mesh in the outliner whose name you want to use (should match UE4 spelling) and click this button to load name into the textfield.')
        layout.addWidget(btnLoadMeshName, 1, 1)

        btnClearMeshData = QtWidgets.QPushButton('Clear Mesh Data')
        btnClearMeshData.clicked.connect(self.clearMeshData)
        btnClearMeshData.setToolTip(
            'Empty out any existing data in the it_export_datafile.ini to help prevent multiple actors from being spawned in UE4.')
        layout.addWidget(btnClearMeshData, 2, 0)

        btnClearTextField = QtWidgets.QPushButton('Clear Textfield')
        btnClearTextField.clicked.connect(self.clearTextField)
        btnClearTextField.setToolTip('Clear the asset name textfield.')
        layout.addWidget(btnClearTextField, 2, 1)

        btnOpenDataFile = QtWidgets.QPushButton('Open Data File')
        btnOpenDataFile.clicked.connect(self.openDataFile)
        btnOpenDataFile.setToolTip('Opens the data file in Notepad to view data contents.')
        layout.addWidget(btnOpenDataFile, 3, 0)

        self.cbAssetFromUE4 = QtWidgets.QCheckBox()
        self.cbAssetFromUE4.setText('Asset(s) from UE4?')
        self.cbAssetFromUE4.setToolTip(
            'Check this box only if you are exporting data for assets that were exporting out of UE4 and imported into Maya.')
        layout.addWidget(self.cbAssetFromUE4, 3, 1)
        # endregion

    def exportData(self):
        # region
        currentSelection = pm.ls(sl=True)
        meshSourceName = self.textSourceName.text()

        if not currentSelection:
            IT_GlobalVar.logger.error("You have nothing selected.  Please select the base mesh(es)")
            return

        if meshSourceName == "":
            IT_GlobalVar.logger.error(
                "You have not specified the source mesh for the current selection.  This is the name of the asset as it exists in UE4.")
            return

        if os.path.exists(dataFileFull):
            IT_GlobalVar.logger.info("Export data config INI file found!")
        else:
            IT_GlobalVar.logger.error("Mesh transform data config INI does not exist.  Creating config file now.")
            d = open(dataFileFull, "w+")
            config.add_section("Placeholder")
            config.set("Placeholder", "TempValue", "000")
            config.write(d)
            IT_GlobalVar.logger.info("Sample data written.  You can find the data file at: " + dataFileFull)
            d.close()

        for selObj in currentSelection:
            pm.select(selObj)
            locationX = cmds.getAttr(selObj + '.translateX')
            locationY = cmds.getAttr(selObj + '.translateY')
            locationZ = cmds.getAttr(selObj + '.translateZ')
            rotationX = cmds.getAttr(selObj + '.rotateX')
            rotationY = cmds.getAttr(selObj + '.rotateY')
            rotationZ = cmds.getAttr(selObj + '.rotateZ')
            scaleX = cmds.getAttr(selObj + '.scaleX')
            scaleY = cmds.getAttr(selObj + '.scaleY')
            scaleZ = cmds.getAttr(selObj + '.scaleZ')

            d = open(dataFileFull, "w+")
            config.read(dataFileFull)
            config.add_section(selObj)
            config.set(selObj, "translateX", locationX)
            config.set(selObj, "translateY", locationY)
            config.set(selObj, "translateZ", locationZ)
            config.set(selObj, "rotateX", rotationX)
            config.set(selObj, "rotateY", rotationY)
            config.set(selObj, "rotateZ", rotationZ)
            config.set(selObj, "scaleX", scaleX)
            config.set(selObj, "scaleY", scaleY)
            config.set(selObj, "scaleZ", scaleZ)
            config.set(selObj, "meshSourceName", meshSourceName)
            if self.cbAssetFromUE4.isChecked() == True:
                config.set(selObj, "assetFromUE4", "true")
            else:
                config.set(selObj, "assetFromUE4", "false")
            config.write(d)
            d.close()
            IT_GlobalVar.logger.info("Saved [" + selObj + "] transform values to data ini file!")
        # endregion

    def clearTextField(self):
        self.textSourceName.setText("")

    def clearMeshData(self):
        # Clear all old data from the data ini file.
        d = open(dataFileFull, "w+")
        config.read(dataFileFull)
        allSections = config.sections()
        IT_GlobalVar.logger.info("Clearing out the data config file...")
        for section in allSections:
            config.remove_section(section)
        d.close()

    def loadMeshName(self):
        currentSelection = pm.ls(sl=True)

        if not currentSelection:
            IT_GlobalVar.logger.error("You have nothing selected.  Please select the base mesh(es)")
            return

        if len(currentSelection) > 1:
            IT_GlobalVar.logger.error(
                "You have too many objects selected to be loaded in as the source mesh name.  Please only select one mesh.")
            return

        for obj in currentSelection:
            self.textSourceName.setText(str(obj))

    def openDataFile(self):
        try:
            import subprocess
            subprocess.Popen(["notepad.exe", dataFileFull])
        except:
            IT_GlobalVar.logger.exception()
