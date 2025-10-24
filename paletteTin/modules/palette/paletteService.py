from krita import Krita
import os
import json
from PyQt5.QtWidgets import (
    QComboBox,
    QLabel,
    QHBoxLayout,
    QDialog,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
)


class PaletteService:
    def __init__(self) -> None:
        pass

    def getPaletteAsJSON(self, paletteName):
        baseDir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        palettePath = os.path.join(
            baseDir, "userData", "palettes", f"{paletteName}.json"
        )
        with open(palettePath, "r") as jsonFile:
            palette = json.load(jsonFile)
        return palette

    def savePaletteAsJSON(self, jsonName, paletteData, exportPath=""):
        baseDir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        if jsonName == "_default":
            return False, "Can't overwrite the default palette for now"
        if exportPath:
            paletteFile = os.path.join(exportPath, f"{jsonName}.json")
        else:
            palettesDir = os.path.join(baseDir, "userData", "palettes")
            paletteFile = os.path.join(palettesDir, f"{jsonName}.json")
        if os.path.exists(paletteFile):
            return False, "Palette name already exists."
        data = {"name": jsonName, "palette": paletteData}
        with open(paletteFile, "w") as outfile:
            json.dump(data, outfile, indent=4)
        return True, "Palette has been successfully saved."

    def getPaletteList(self):
        baseDir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        palettesDir = os.path.join(baseDir, "userData", "palettes")
        filenames = os.listdir(palettesDir)
        jsonFilenames = [
            os.path.splitext(file)[0] for file in filenames if file.endswith(".json")
        ]
        return jsonFilenames


class SavePaletteDialog(QDialog):
    def __init__(self, parent, title=""):
        super().__init__(parent)
        self.resize(200, 80)
        self.setWindowTitle(title)
        self.ps = PaletteService()
        self.setUI()

    def setUI(self):
        self.mainContainer = QVBoxLayout()
        self.mainContainer.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.mainContainer)

        self.buttonContainer = QHBoxLayout()
        self.buttonWidget = QWidget()
        self.buttonWidget.setLayout(self.buttonContainer)
        self.buttonContainer.setContentsMargins(0, 0, 0, 0)

        self.labelPalette = QLabel("Palette Name")
        self.paletteName = QLineEdit()
        self.buttonSave = QPushButton("Save")
        self.buttonExport = QPushButton("Export")

        self.mainContainer.addWidget(self.labelPalette)
        self.mainContainer.addWidget(self.paletteName)
        self.mainContainer.addWidget(self.buttonWidget)
        self.buttonContainer.addWidget(self.buttonSave)

        self.buttonSave.clicked.connect(lambda: self.savePaletteJSON(""))

    def savePaletteJSON(self, exportPath=""):
        doc = Krita.instance().activeDocument()
        if doc is None:
            QMessageBox.warning(self, "Error", "Error: No document selected.")
            return False
        if (
            doc.colorModel() != "RGBA"
            and doc.colorProfile() != "sRGB-elle-V2-srgbtrc.icc"
        ):
            QMessageBox.warning(
                self,
                "Error",
                "Error: Invalid Color Model. This function only works with RGBA model and sRGB-elle-V2-srgbtrc.icc profile.",
            )
            return False

        jsonName = self.paletteName.text().strip()
        if not jsonName:
            QMessageBox.warning(self, "Error", "Error: Empty file name.")
            return False
        jsonName = "".join(x for x in jsonName if x.isalnum() or x in "._- ")
        if not jsonName:
            QMessageBox.warning(self, "Error", "Error: Invalid file name.")
            return False

        success, message = self.ps.savePaletteAsJSON(
            jsonName, self.parent().swatchRGB, exportPath
        )
        if not success:
            QMessageBox.warning(self, "Error", f"Error: {message}")
            return False

        self.parent().updatePaletteTrayDropdown()
        QMessageBox.information(self, "Success", message)
        self.done(0)
        return True


class LoadPaletteDialog(QDialog):
    def __init__(self, parent, title=""):
        super().__init__(parent)
        self.parent = parent
        self.resize(200, 80)
        self.setWindowTitle(title)
        self.ps = parent.ps
        self.setUI()

    def setUI(self):
        self.mainContainer = QVBoxLayout()
        self.mainContainer.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.mainContainer)

        self.buttonContainer = QHBoxLayout()
        self.buttonWidget = QWidget()
        self.buttonWidget.setLayout(self.buttonContainer)
        self.buttonContainer.setContentsMargins(0, 0, 0, 0)

        self.paletteTrayDropdown = QComboBox()
        self.paletteTrayDropdown.addItems(self.ps.getPaletteList())
        self.paletteTrayDropdown.setCurrentIndex(0)
        self.paletteTrayDropdown.setMaximumWidth(60)

        self.buttonLoad = QPushButton("Load")
        self.buttonLoad.clicked.connect(self.load)

        self.mainContainer.addWidget(self.paletteTrayDropdown)
        self.mainContainer.addWidget(self.buttonLoad)

    def load(self):
        palette_name = self.paletteTrayDropdown.currentText()
        try:
            self.parent.swatchRGB = self.ps.getPaletteAsJSON(palette_name)["palette"]
            self.parent.history.appendPalette(self.parent.swatchRGB)
        except Exception:
            print("Error executing loading palette does not exists or empty")


class HelpDialog(QDialog):
    def __init__(self, parent, title=""):
        super().__init__(parent)
        self.parent = parent
        self.resize(200, 80)
        self.setWindowTitle(title)

        self.setUI()

    def setUI(self):
        self.mainContainer = QVBoxLayout()
        self.mainContainer.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.mainContainer)

        self.label = QLabel()
        self.label.setText("""
            Ellipse/Rectangle/Cross represent Locked/Modifiable/Empty.

            Left click to select a color.
            Middle click to toggle locking.
            Right click to mix.

            The eraser icon button can be toggled; when on,
            left and right click deletes. Middle click will
            quit erase mode without having to click the button again.

            Alternatively, you can always delete with Shift + Right click.

            """)
        self.mainContainer.addWidget(self.label)
