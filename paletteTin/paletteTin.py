from krita import *

from PyQt5.QtCore import Qt, QSize, QTimer, QPoint, QObject, QEvent
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QLabel,
    QComboBox,
    QToolButton,
    QDesktopWidget,
    QSlider,
    QSizeGrip,
    QSpacerItem,
    QSizePolicy,
)
from PyQt5.QtGui import QIcon

from .colorTray import *
from .colorMixing import mixingList
from .annotationService import *
from .modules.palette.paletteHistoryService import *
from .constants import PALETTE_HSV_16
from .modules.palette.paletteService import *
from functools import partial

DOCKER_NAME = "PaletteTin"
DOCKER_ID = "pykrita_PaletteTin"
PALETTE_HSV = PALETTE_HSV_16


class PaletteTin(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Palette Tin")

        self.canvasColor = QColor(200, 200, 200)
        self._kraActiveDocument = None
        self.annotationService = AnnotationService()
        self.history = PaletteHistoryService(1000)
        self.ps = PaletteService()

        self.colorCount = 6
        self.gridCount = 8

        self.mixRate = 50
        self.mixModes = mixingList
        self.hybridRate = 40

        self.colorGrid = []
        self.hsvDialog = None
        self.saveDialog = None
        self.loadDialog = None
        self.helpDialog = None
        self.erase_mode = False
        self.undoStack = []

        self.setUi()
        self.connectButtons()
        self.connectColorGrid()

    def setUi(self):
        self.rootWidget = QWidget()
        self.bodyContainer = QVBoxLayout()
        self.bodyContainer.setContentsMargins(2, 2, 2, 2)
        self.bodyContainer.setSpacing(0)
        self.rootWidget.setLayout(self.bodyContainer)
        self.setWidget(self.rootWidget)
        self.rootWidget.setMinimumSize(QSize(30, 30))

        # holds main components, non toolbuttons
        self.tinWidget = QWidget()
        self.tinContainer = QHBoxLayout()
        self.tinWidget.setLayout(self.tinContainer)
        self.tinContainer.setContentsMargins(0, 0, 0, 0)  # 4040

        # holds items related to mixing
        self.mixerWidget = QWidget()
        self.mixerContainer = QVBoxLayout()
        self.mixerWidget.setLayout(self.mixerContainer)
        self.mixerContainer.setContentsMargins(0, 5, 0, 5)

        # holds the palette related components
        self.paletteWidget = QWidget()
        self.paletteContainer = QGridLayout()
        self.paletteWidget.setLayout(self.paletteContainer)
        self.paletteContainer.setContentsMargins(0, 0, 0, 0)

        self.tinContainer.addWidget(self.paletteWidget, 2)

        # # palette trays
        # self.paletteTrayDropdown = QComboBox()
        # self.paletteTrayDropdown.addItems(["default tray"] + self.ps.getPaletteList())
        # self.paletteTrayDropdown.setCurrentIndex(0)
        # self.paletteTrayDropdown.currentIndexChanged.connect(self.loadPaletteFromTray)

        # todo make ticks work
        self.mixRateLabel = QLabel()
        self.mixRateSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.mixRateSlider.setRange(1, 100)
        self.mixRateSlider.setSingleStep(1)
        starting_mix_rate = 50
        self.mixRateSlider.setValue(starting_mix_rate)
        self.updateMixRateLabel(starting_mix_rate)
        self.mixRateSlider.setPageStep(10)
        self.mixRateSlider.TickPosition(QSlider.TickPosition.TicksRight)
        self.mixRateSlider.setTickInterval(10)
        self.mixRateSlider.valueChanged.connect(lambda value: self.updateMixRate(value))

        # mixmode dropdown, this is its own source of truth, options are dict keys
        self.mixModeDropdown = QComboBox()
        self.mixModeDropdown.addItems(self.mixModes.keys())
        self.mixModeDropdown.setCurrentIndex(2)
        self.mixModeDropdown.setMaximumHeight(60)

        self.mixRateBox = QWidget()
        self.mixRateBoxContainer = QHBoxLayout()
        self.mixRateBox.setLayout(self.mixRateBoxContainer)
        self.mixRateBoxContainer.setContentsMargins(0, 0, 0, 0)
        self.mixRateBoxContainer.addWidget(self.mixRateLabel)
        self.mixRateBoxContainer.addWidget(self.mixRateSlider)

        self.mixerContainer.addWidget(self.mixModeDropdown, 0, Qt.AlignHCenter)
        self.mixerContainer.addWidget(self.mixRateBox, 0)

        # COLOR GRID
        for r in range(self.gridCount):
            self.colorGrid.append([])
            for c in range(self.colorCount):
                # Set mixable=False for the first and last columns
                mixable = not (c == 0 or c == self.colorCount - 1)
                self.colorGrid[r].append(ColorTray(mixable=mixable))
                self.paletteContainer.addWidget(self.colorGrid[r][c], r, c, 1, 1)

        # toolbox holds action buttons
        toolbuttonSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.buttonErase = QToolButton()
        self.buttonErase.setIcon(Krita.instance().icon("draw-eraser"))
        self.buttonErase.setSizePolicy(toolbuttonSizePolicy)

        self.buttonUndo = QToolButton()
        self.buttonUndo.setIcon(Krita.instance().icon("edit-undo"))
        self.buttonUndo.setSizePolicy(toolbuttonSizePolicy)

        self.buttonHelp = QToolButton()
        self.buttonHelp.setIcon(Krita.instance().icon("system-help"))
        self.buttonHelp.setSizePolicy(toolbuttonSizePolicy)

        self.buttonSave = QToolButton()
        self.buttonSave.setIcon(Krita.instance().icon("document-save"))
        self.buttonSave.setSizePolicy(toolbuttonSizePolicy)

        self.buttonLoad = QToolButton()
        self.buttonLoad.setIcon(Krita.instance().icon("document-open"))
        self.buttonLoad.setSizePolicy(toolbuttonSizePolicy)

        sizegrip = QSizeGrip(self.rootWidget)
        sizegrip.setSizePolicy(toolbuttonSizePolicy)

        self.toolboxWidget = QWidget()
        self.toolboxContainer = QHBoxLayout()
        self.toolboxWidget.setLayout(self.toolboxContainer)
        self.toolboxContainer.setContentsMargins(0, 0, 0, 0)

        self.toolboxContainer.addWidget(self.buttonErase)
        self.toolboxContainer.addWidget(self.buttonUndo)
        self.toolboxContainer.addWidget(self.buttonSave)
        self.toolboxContainer.addWidget(self.buttonLoad)
        self.toolboxContainer.addWidget(self.buttonHelp)

        self.toolboxContainer.addWidget(sizegrip)

        # self.bodyContainer.addWidget(self.paletteTrayDropdown)
        self.bodyContainer.addWidget(self.tinWidget, 10)
        self.bodyContainer.addWidget(self.mixerWidget, 0)
        self.bodyContainer.addWidget(self.toolboxWidget, 0)

        # pushes everything to the top
        self.spacer = QSpacerItem(1, 3, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.loadPaletteByName("_default")

    # def updatePaletteTrayDropdown(self):
    #     self.paletteTrayDropdown.clear()
    #     self.paletteTrayDropdown.addItems(["default tray"] + self.ps.getPaletteList())

    # def loadPaletteFromTray(self):
    #     palette = self.paletteTrayDropdown.currentText()
    #     self.loadPaletteByName(palette)

    def loadPaletteByName(self, name):
        try:
            self.swatchRGB = self.ps.getPaletteAsJSON(name)["palette"]
            self.history.appendPalette(self.swatchRGB)
        except Exception:
            print("Error executing loading palette does not exists or empty")

    def canvasChanged(self, canvas):
        """
        important, since it uses resources from the document itself
        this handles when and how it loads a data, explain better
        """
        if canvas:
            if Krita.instance().activeDocument() and canvas.view():
                self.connectColorGrid()
                self._kraActiveDocument = canvas.view().document()
                self.history.reset()
            else:
                self.disconnectColorGrid()
        else:
            self.disconnectColorGrid()
        self.annotationService.document = self._kraActiveDocument
        self.annotationService.startup()
        self.loadAnnotationColors()

    def connectButtons(self):
        self.buttonErase.clicked.connect(self.toggleEraseMode)
        self.buttonUndo.clicked.connect(self.undo)
        self.buttonSave.clicked.connect(self.openSaveDialog)
        self.buttonLoad.clicked.connect(self.openLoadDialog)
        self.buttonHelp.clicked.connect(self.openHelpDialog)

    def connectColorGrid(self):
        for row in self.colorGrid:
            for color in row:
                # Disconnect existing connections to avoid multiple connections
                try:
                    color.clicked.disconnect()
                except TypeError:
                    pass
                color.clicked.connect(partial(self.colorTrayClickEvent, color))

    def disconnectColorGrid(self):
        for row in self.colorGrid:
            for color in row:
                color.disconnect()

    def avoidLockingMinSize(self):
        self.rootWidget.setMinimumSize(30, 30)

    def setFgColor(self, colorTray):
        rgb = colorTray.getColorRGB()
        if rgb is None:
            return
        colorToSet = colorTray.getColorForSet(
            Krita.instance().activeDocument(),
            Krita.instance().activeWindow().activeView().canvas(),
        )
        Krita.instance().activeWindow().activeView().setForeGroundColor(colorToSet)

    def toggleEraseMode(self):
        if self.erase_mode:
            self.erase_mode = False
            self.buttonErase.setStyleSheet("QToolButton{color : unset;}")
            self.rootWidget.setCursor(Qt.ArrowCursor)
        else:
            self.erase_mode = True
            self.buttonErase.setStyleSheet("QToolButton{background-color : red;}")
            self.rootWidget.setCursor(Qt.CrossCursor)

    def colorTrayClickEvent(self, colorTray, button, modifiers):
        if self.erase_mode:
            if button == Qt.MiddleButton:
                self.toggleEraseMode()
            elif colorTray.mixable:
                colorTray.deleteColor()
            return

        if button == Qt.LeftButton:
            if colorTray.color is None:
                self.colorMix(colorTray)
            else:
                self.setFgColor(colorTray)
        elif button == Qt.RightButton and colorTray.mixable:
            if modifiers == Qt.ShiftModifier:
                colorTray.deleteColor()
            else:
                self.colorMix(colorTray)
        elif button == Qt.MiddleButton:
            if colorTray.color is not None:
                colorTray.toggleMixability()

    def updateMixRate(self, value):
        self.updateMixRateLabel(value)
        self.mixRate = value

    def updateMixRateLabel(self, value):
        self.mixRateLabel.setText(f"Mix {value}%")

    def colorMix(self, colorTray):
        mr = self.mixRate
        view = Krita.instance().activeWindow().activeView()
        cfg = view.foregroundColor().colorForCanvas(view.canvas())
        mixinMode = self.mixModes[self.mixModeDropdown.currentText()]

        boxRGB = colorTray.getColorRGB()
        secondaryRGB = [cfg.red(), cfg.green(), cfg.blue()]
        red, green, blue = 0, 1, 2
        if boxRGB is None:
            mixed = secondaryRGB
            colorTray.setColorRGB(mixed[red], mixed[green], mixed[blue])
        else:
            primaryRGB = [boxRGB["red"], boxRGB["green"], boxRGB["blue"]]
            mixed = mixinMode(primaryRGB, secondaryRGB, mr / 100)
            colorTray.setColorRGB(mixed[red], mixed[green], mixed[blue])
        self.setFgColor(colorTray)
        self.printColorGrid()

    def loadAnnotationColors(self):
        if self.annotationService.palette and self.colorGrid:
            for row in range(len(self.colorGrid)):
                for col in range(len(self.colorGrid[row])):
                    self.colorGrid[row][col].importRGB(
                        self.annotationService.palette[row][col]
                    )
            self.history.appendPalette(self.annotationService.palette)

    def openSaveDialog(self):
        if self.saveDialog is None:
            self.saveDialog = SavePaletteDialog(self, "Save Color Palette")
            self.saveDialog.show()
        elif not self.saveDialog.isVisible():
            self.saveDialog.show()
        else:
            pass
        self.moveDialog(self.saveDialog)

    def openLoadDialog(self):
        if self.loadDialog is None:
            self.loadDialog = LoadPaletteDialog(self, "Load Color Palette")
            self.loadDialog.show()
        elif not self.loadDialog.isVisible():
            self.loadDialog.show()
        else:
            pass
        self.moveDialog(self.loadDialog)

    def openHelpDialog(self):
        if self.helpDialog is None:
            self.helpDialog = HelpDialog(self, "Info")
            self.helpDialog.show()
        elif not self.helpDialog.isVisible():
            self.helpDialog.show()
        else:
            pass
        self.moveDialog(self.helpDialog)

    def moveDialog(self, dialog):
        gp = self.mapToGlobal(QPoint(0, 0))
        if self.x() < (QDesktopWidget().screenGeometry().width() // 2):
            dialog.move(gp.x() + self.frameGeometry().width() + 10, gp.y() + 30)
        else:
            dialog.move(gp.x() - (dialog.frameGeometry().width() + 5), gp.y() + 30)

    def undo(self):
        prev = self.history.returnPreviousPalette()
        if self.colorGrid and prev:
            for row in range(len(self.colorGrid)):
                for col in range(len(self.colorGrid[row])):
                    self.colorGrid[row][col].importRGB(prev[row][col])

    def printHSV(self):
        if self.hsvDialog:
            self.hsvDialog.printHSV()

    def printColorGrid(self):
        save = []
        for row in range(len(self.colorGrid)):
            dd = []
            for col in range(len(self.colorGrid[row])):
                dd.append(self.colorGrid[row][col].exportRGB())
            save.append(dd)
        self.history.appendPalette(save)
        self.annotationService.savePalette(save)

    @property
    def swatchRGB(self):
        # Getter method for swatchRGB
        save = []
        for row in range(len(self.colorGrid)):
            dd = [cell.exportRGB() for cell in self.colorGrid[row]]
            save.append(dd)
        return save

    @swatchRGB.setter
    def swatchRGB(self, palette):
        # Setter method for swatchRGB
        if self.colorGrid:
            for row in range(len(self.colorGrid)):
                for col in range(len(self.colorGrid[row])):
                    self.colorGrid[row][col].importRGB(palette[row][col])


instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(
    DOCKER_ID, DockWidgetFactoryBase.DockRight, PaletteTin
)
instance.addDockWidgetFactory(dock_widget_factory)
