from PyQt5.QtWidgets import (
    QComboBox, QGridLayout, QLabel, QLineEdit, QFrame,
    QPushButton, QVBoxLayout, QDialog, QHBoxLayout, QCheckBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import os, json

class SettingsManager():
    def __init__(self) -> None:
        self.loadSettings()
        
    def loadSettings(self):
        jsonSetting = open(os.path.dirname(os.path.realpath(__file__)) + '/userData/settings/settings.json')
        self.setSettings(json.load(jsonSetting))
        jsonSetting.close()
        
    def setSettings(self, settings):
        self.settings = settings

    def getSettings(self):
        return self.settings
    
    def setMixingMode(self, mode: int):
        self.getSettings()["mixingMode"] = mode

    def setHistorySize(self, size: int):
        self.getSettings()["historySize"] = size

    def setMinizeRetainWitdh(self, flag: bool):
        self.getSettings()["minizeRetainWitdh"] = flag

    def getMixingMode(self) -> int:
        return int(self.getSettings()["mixingMode"])

    def getHistorySize(self) -> int:
        return int(self.getSettings()["historySize"])

    def getMinizeRetainWitdh(self) -> bool:
        return bool(self.getSettings()["minizeRetainWitdh"])

    def saveSettings(self, mixingMode: int = None, historySize: dict = None, minizeRetainWidth: bool = None):
        self.setMixingMode(mixingMode) if mixingMode is not None else None
        self.setHistorySize(historySize) if historySize else None
        self.setMinizeRetainWitdh(minizeRetainWidth) if minizeRetainWidth != None else None #mal
        jsonSetting = json.dumps(self.getSettings(), indent = 4)
        with open(os.path.dirname(os.path.realpath(__file__)) + '/userData/settings/settings.json', "w") as outfile:
            outfile.write(jsonSetting)
        


    def toString(self):
        print(f"Palette Tin docker settings: {self.getSettings()}")

class SettingsUI(QDialog):
    
    def __init__(self, settingsManager: SettingsManager , parent=None) -> None:
        super().__init__(parent)
        # self.sv = settingsService
        self.sm = settingsManager
        self.initUI()

    def initUI(self):
        # Main layout
        mainLayout = QVBoxLayout()
        
        #cycle orientation
        self.minizeRetainWidthCheckbox = QCheckBox("Retain width when minimized?")
        self.minizeRetainWidthCheckbox.setCheckState(Qt.Checked if self.sm.getMinizeRetainWitdh() else Qt.Unchecked)
        mainLayout.addWidget(self.minizeRetainWidthCheckbox)
        #image
        filename = os.path.dirname(os.path.realpath(__file__)) + '/assets/palletTin-help.png'
        imageLabel = QLabel()  # Create a QLabel to display the image
        mainLayout.addWidget(imageLabel, 10)
        pixmap = QPixmap(filename)  # Load the image file into QPixmap
        if not pixmap.isNull():  # Check if the image was loaded successfully
            imageLabel.setPixmap(pixmap)
            imageLabel.setScaledContents(True)  # Scale image to fit QLabel
            imageLabel.setAlignment(Qt.AlignCenter)  # Center the image
            imageLabel.setFixedSize(pixmap.size())  # Set the QLabel size to the image size
        else:
            imageLabel.setText("Image not found!")  # Display message if image fails to load



        # Buttons
        buttonLayout = QGridLayout()
        self.saveButton = QPushButton('Save')
        self.cancelButton = QPushButton('Cancel')
        buttonLayout.addWidget(self.saveButton, 0, 0)
        buttonLayout.addWidget(self.cancelButton, 0, 1)

        # Add buttons to the main layout
        mainLayout.addLayout(buttonLayout, 1)


        # Set main layout
        self.setLayout(mainLayout)

        # Connect the save button to a function to print the selected value
        self.saveButton.clicked.connect(self.saveSettings)
        self.cancelButton.clicked.connect(self.cancelSettings)

    def emitCloseDialog(self):
        # self.parent().closeDialog()
        self.done(0)

    def saveSettings(self):
        minizeRetainWidth = (self.minizeRetainWidthCheckbox.checkState() == Qt.Checked)

        # save
        self.sm.saveSettings(minizeRetainWidth=minizeRetainWidth)
        
        self.emitCloseDialog()

    def cancelSettings(self):
        self.emitCloseDialog()