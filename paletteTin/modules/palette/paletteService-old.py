 
#-----------------------------------------------------------------------------#
# Palette Tin - Copyright (c) 2023 - kaichi1342                         #
# ----------------------------------------------------------------------------#
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
# ----------------------------------------------------------------------------#
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                        #
# See the GNU General Public License for more details.                        #
#-----------------------------------------------------------------------------#
# You should have received a copy of the GNU General Public License           #
# along with this program.                                                    #
# If not, see https://www.gnu.org/licenses/                                   # 
# -----------------------------------------------------------------------------
# PaletteTin is a docker that  generates color scheme palette randomly  #
# or based of the selected scheme. There are 9 color scheme available to      #
# generate from.                                                              #
# -----------------------------------------------------------------------------
    
  
from krita import *  
import os, zipfile, random, string, json
from .utils import getColorName

#from PyQt5.QtCore import ( Qt, pyqtSignal, QEvent)

#from PyQt5.QtGui import (QStandardItemModel)


from PyQt5.QtWidgets import ( 
    QLabel, QHBoxLayout, QDialog, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QFileDialog, QMessageBox
) 
 
 
class KPLCreator(): 
    def __init__(self):   
        self.schemeDict = {
            "Monochromatic"         : "mono", 
            "Accented Achromatic"   : "acct", 
            "Analogous"             : "ang", 
            "Complementary"         : "comp", 
            "Split Complementary"   : "scomp", 
            "Double Split Complementary"  : "dsc",
            "Triadic"               : "triad", 
            "Tetradic Square"       : "tetsq",  
            "Tetradic Rectangle"    : "tetrc",
            "custom": "custom"
        }
        self.schemeKey = "mono"
        self.colorDepth = "U8"
        self.colorProfile = ""
        super().__init__() 

    def setColorScheme(self, scheme):
        self.scheme = scheme
        self.schemeKey = self.schemeDict[scheme]

    def createProfile(self, file):  
        doc = Krita.instance().activeDocument()
        self.colorDepth   = doc.colorDepth()
        self.colorProfile = doc.colorProfile()
        comment = "Generated From Palette Tin Plugin - " + self.scheme + " Color Scheme."
        with open(os.path.dirname(os.path.realpath(__file__)) +  file, "w") as outfile: 
            outfile.write('<Profiles>\n')
            outfile.write('  <Profile filename="' + doc.colorProfile() + '" colorDepthId="' + doc.colorDepth() + '" colorModelId="' + doc.colorModel() + '" name="' + doc.colorProfile() + '" comment="' + comment + ' "/>\n')
            outfile.write('</Profiles>\n')


    def createColorSet(self, file, kplName, mainColor, colorGrid,  row = 4, col = 7):
        self.row = row
        self.col = col
        with open(os.path.dirname(os.path.realpath(__file__)) + file, "w") as outfile: 
            outfile.write('<ColorSet version="2.0" rows="' + str(self.row) + '" columns="' + str(self.col) + '" name="' + kplName + '" comment="">\n')
            self.kplColorGrid(outfile, mainColor, colorGrid)
            outfile.write('</ColorSet>\n')

     
    def kplColorGrid(self, outfile, mainColor, colorGrid):
        # for r in range(0, self.row):
        #    self.kplSetColorEntry(outfile, mainColor.color,  mainColor.getHueName() + '_'  , r, 0) 

        for r in range(0, self.row):
            for c in range(0, self.col):
                self.kplSetColorEntry(outfile, colorGrid[r][c].color,  getColorName(colorGrid[r][c].exportHSV()) , r, c) 
 

    def kplSetColorEntry(self, outfile, color, colorName, r, c): 
        # colorName = colorName + "r" + str(r) + "c" + str(c)
        id = ''.join(random.choices(string.ascii_uppercase, k=3))
        outfile.write(f'  <ColorSetEntry spot="true" id="{id}"  name="{colorName}" bitdepth="{self.colorDepth}">\n') 
        outfile.write('    <RGB space="' + str(self.colorProfile) + '" r="' + str(color.redF()) + '" g="' + str(color.greenF()) + '" b="' + str(color.blueF()) + '"/>\n') 
        outfile.write('    <Position row="'+str(r)+'" column="'+str(c)+'"/>\n')
        outfile.write('  </ColorSetEntry>\n')

class PaletteService():
    
    def __init__(self) -> None:
        pass

    def getPaletteAsJSON(self, paletteName):
        palette = None
        jsonSetting = open(os.path.dirname(os.path.realpath(__file__ + '/../../')) + f'/userData/palettes/{paletteName}.json')
        palette = json.load(jsonSetting)
        jsonSetting.close()
        return palette

    def savePaletteAsJSON(self, paletteName):
        pass

    def getPaletteList(self):
        # parentDir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        parentDir =  f"{os.path.dirname(os.path.realpath(__file__ + '/../../'))}/userData/palettes"
        # List all files in that directory
        filenames = os.listdir(parentDir)
        
        # Filter files with .json extension and remove the extension
        jsonFilenames = [os.path.splitext(file)[0] for file in filenames if file.endswith('.json')]

        return jsonFilenames



class SavePaletteDialog(QDialog):
    def __init__(self, parent, title = "" ):
        super().__init__(parent)
        
        self.resize(200,80)  
        self.setWindowTitle(title)  

        self.ps = PaletteService()

        self.KPLMaker = KPLCreator()
        self.setUI() 

    # UI LAYOUT
    def setUI(self):
        self.mainContainer = QVBoxLayout() 
        self.mainContainer.setContentsMargins(5, 5, 5, 5)
    
        self.setLayout(self.mainContainer)  

        self.buttonContainer =  QHBoxLayout()
        self.buttonWidget = QWidget()
        self.buttonWidget.setLayout(self.buttonContainer)
        self.buttonContainer.setContentsMargins(0, 0, 0, 0)
        
        self.labelPalette      = QLabel("Palette Name") 
        self.paletteName       = QLineEdit() 
        self.buttonSave        = QPushButton("Save") 
        self.buttonExport       = QPushButton("Export") 
        self.labelTest         = QLabel()

        self.mainContainer.addWidget(self.labelPalette) 
        self.mainContainer.addWidget(self.paletteName) 
 
        self.mainContainer.addWidget(self.buttonWidget) 

        self.buttonContainer.addWidget(self.buttonSave)  
        self.buttonContainer.addWidget(self.buttonExport) 

        #self.mainContainer.addWidget(self.labelTest) 

        self.dlg = QFileDialog()
        self.dlg.setFileMode(QFileDialog.AnyFile)
 
        self.buttonSave.clicked.connect(lambda: self.savePaletteJSON(""))
        self.buttonExport.clicked.connect(self.browseDirectory)

    def loadDefault(self):
        self.paletteName.setText("")
 

    def browseDirectory(self):    
        filepath = str(QFileDialog.getExistingDirectory(self, "Select Directory")) 
        self.savePalette(filepath) 
         
    def savePaletteJSON(self, filepath = ""):   
        doc = Krita.instance().activeDocument()
       
        if doc == None: 
            QMessageBox.warning(self, "Error", "Error: No document selected.")  
            return False
        if doc.colorModel() != "RGBA" and doc.colorProfile() != "sRGB-elle-V2-srgbtrc.icc":
            QMessageBox.warning(self, "Error", "Error: Invalid Color Model: This function only works with RGBA model and sRGB-elle-V2-srgbtrc.icc profile.") 
            return False

        if  self.paletteName.text() == "": 
            QMessageBox.warning(self, "Error", "Error: Empty file name.") 
            return False

        jsonName = self.paletteName.text()
        jsonName = "".join(x for x in jsonName if x.isalnum() or  x in "._- ")
     
        if jsonName == "": 
            QMessageBox.warning(self, "Error", "Error: Invalid file name.") 
            return False

        # self.KPLMaker.setColorScheme("custom")
        # self.KPLMaker.createProfile('/paletteTemplate/profiles.xml')
        # self.KPLMaker.createColorSet('/paletteTemplate/colorset.xml', jsonName, self.parent().colorspotter, self.parent().colorGrid, 8, 6 )
         
        # self.saveKPL(jsonName, filepath)
        self.saveJSON(jsonName, filepath)
        self.done(0)
        return True
    
    def saveJSON(self, jsonName, filepath = ""):   
        paletteFile = f'{os.path.dirname(os.path.realpath(__file__))}/../../palettes/{jsonName}.json' if filepath == "" else f"{filepath}/{jsonName}.json"
        isExist = os.path.exists(paletteFile)

        if isExist : 
            QMessageBox.warning(self, "Error", "Error: Palette name already exist.") 
            return False

        data = {
            "name": jsonName,
            "palette": self.parent().swatchRGB
        }
        jsonSetting = json.dumps(data, indent = 4)
        with open(f"{os.path.dirname(os.path.realpath(__file__ + '/../../'))}/userData/palettes/{jsonName}.json", "w") as outfile:
            outfile.write(jsonSetting)

        self.parent().updatePaletteTrayDropdown()
     
        QMessageBox.information(self, "Success", "Palette have been succesfully saved.")

        return True 
    
    def getJSON(self):
        pass

    def PaletteList(self, paletteName):
        pass
 

    def savePalette(self, filepath = ""):   
        doc = Krita.instance().activeDocument()
       
        if doc == None: 
            QMessageBox.warning(self, "Error", "Error: No document selected.")  
            return False
        if doc.colorModel() != "RGBA" and doc.colorProfile() != "sRGB-elle-V2-srgbtrc.icc":
            QMessageBox.warning(self, "Error", "Error: Invalid Color Model: This function only works with RGBA model and sRGB-elle-V2-srgbtrc.icc profile.") 
            return False

        if  self.paletteName.text() == "": 
            QMessageBox.warning(self, "Error", "Error: Empty file name.") 
            return False

        kplName = self.paletteName.text()
        kplName = "".join(x for x in kplName if x.isalnum() or  x in "._- ")
     
        if kplName == "": 
            QMessageBox.warning(self, "Error", "Error: Invalid file name.") 
            return False

        self.KPLMaker.setColorScheme("custom")
        self.KPLMaker.createProfile('/paletteTemplate/profiles.xml')
        self.KPLMaker.createColorSet('/paletteTemplate/colorset.xml', kplName, self.parent().colorspotter, self.parent().colorGrid, 8, 6 )
         
        self.saveKPL(kplName, filepath)
        self.done(0)
        return True


    def saveKPL(self, kplName, filepath = ""):   
        
        # paletteFile = os.path.dirname(os.path.realpath(__file__)) + '/../../palettes/' + kplName + '.kpl' if filepath == "" else filepath + '/' + kplName + '.kpl'
        # paletteFile = f"/home/joseeb/.local/share/krita/palettes/{kplName}.kpl" if filepath == "" else f"{filepath}/{kplName}.kpl"
        paletteFile = f'{os.path.dirname(os.path.realpath(__file__))}/../../palettes/{kplName}.kpl' if filepath == "" else f"{filepath}/{kplName}.kpl"
        isExist = os.path.exists(paletteFile)

        if isExist : 
            QMessageBox.warning(self, "Error", "Error: Palette name already exist.") 
            return False

        contentLoc  = os.path.dirname(os.path.realpath(__file__)) + '/paletteTemplate'
        with zipfile.ZipFile(paletteFile, 'w') as paletteZip:
            for folderName, subfolders, filenames in os.walk(contentLoc):
                for filename in filenames: 
                    filePath = os.path.join(folderName, filename) 
                    paletteZip.write(filePath, os.path.basename(filePath))
     
        QMessageBox.information(self, "Success", "Palette have been succesfully saved.")

        return True 
 
    # def getHueName(self):
    #     hue = self.color.hsvHue()
    #     if hue >= 0     and hue <= 5        : return "red"
    #     elif hue >= 6   and hue <= 35       : return "orange"
    #     elif hue >= 36  and hue <= 65       : return "yellow" 
    #     elif hue >= 66  and hue <= 170      : return "green" 
    #     elif hue >= 171 and hue <= 185      : return "cyan" 
    #     elif hue >= 186 and hue <= 255      : return "blue" 
    #     elif hue >= 256 and hue <= 280      : return "purple" 
    #     elif hue >= 281 and hue <= 325      : return "magenta" 
    #     elif hue >= 326 and hue <= 345      : return "pink" 
    #     else                                : return "red" 
