from krita import *

from PyQt5.QtCore import (Qt, QSize, QTimer, QPoint, QObject, QEvent)
from PyQt5.QtWidgets import (
    QVBoxLayout, QGridLayout, QHBoxLayout,
    QPushButton, QWidget, QLabel, QComboBox,
    QToolButton, QDesktopWidget, QSlider, QSizeGrip, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QIcon

from .colorTray import *
from .colorMixing import mixingList
from .annotationService import *
from .modules.palette.paletteHistoryService import *
from .qtExtras import *
from .rectangleQT import *
from .constants import GRAY, PALETTE_HSV_16, LockState
from .modules.palette.paletteService import *
from .settingsService import *
from functools import partial

DOCKER_NAME = 'PaletteTin'
DOCKER_ID = 'pykrita_PaletteTin'
PALETTE_HSV = PALETTE_HSV_16


class PaletteTin(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Palette Tin")

        self.canvasColor = QColor(200, 200, 200)
        self._kraActiveDocument = None
        self.annotationService = AnnotationService()
        self.sm = SettingsManager()
        self.history = PaletteHistoryService(self.sm.getHistorySize())
        self.ps = PaletteService()

        self.colorCount = 6
        self.gridCount = 8

        self.mixRate = 50
        self.mixModes = mixingList
        # self.mixModes = {
        #     "Spectral": spectral,
        #     "Weighted average": mixWeightedAverage,
        #     "Hybrid": hybridMix,
        #     "Overlay": overlayMix,
        #     "LERP": lerpBlend,
        #     "Overlay Hybrid": hybridOverlayMix,
        #     "Sat Val": satValTransfer,
        # }
        self.hybridRate = 40

        self.colorGrid = []
        self.settingDialog = None
        self.hsvDialog = None
        self.svPaletteDialog = None
        self.useFg = False
        self.lock = LockState.OPEN
        self.lockUsed = False
        self.erase = False
        self.cleanBrush = False
        self.undoStack = []
        self.scratchpad = None
        # self.setDefaultModeTimer = QTimer()

        self.setUi()
        self.connectButtons()
        self.connectColorGrid()
        self.foregroundSignal = None

    def setUi(self):
        self.rootWidget = QWidget()
        self.bodyContainer = QVBoxLayout()
        self.bodyContainer.setContentsMargins(0, 0, 0, 0)
        self.bodyContainer.setSpacing(0)
        self.rootWidget.setLayout(self.bodyContainer)
        self.setWidget(self.rootWidget)
        self.rootWidget.setMinimumSize(QSize(30, 30))

        # minimize docker
        self.minimizeButton = QPushButton()
        self.minimizeButton.setIcon(Krita.instance().icon("visible"))
        self.minimizeButton.setCheckable(True)  # Make it toggleable
        self.minimizeButton.setChecked(False)    # Initially checked (visible)
        self.minimizeButton.clicked.connect(self.toggleDockerVisibility)
        self.bodyContainer.addWidget(self.minimizeButton)

        # holds main components, non toolbuttons
        self.tinWidget = QWidget()
        self.tinContainer = QHBoxLayout()
        self.tinWidget.setLayout(self.tinContainer)
        self.tinContainer.setContentsMargins(0, 0, 0, 0)  # 4040

        # holds items related to mixing
        self.mixerWidget = QWidget()
        self.mixerContainer = QVBoxLayout()
        self.mixerWidget.setLayout(self.mixerContainer)
        self.mixerContainer.setContentsMargins(0, 0, 0, 0)

        # holds the palette related components
        self.paletteWidget = QWidget()
        self.paletteContainer = QGridLayout()
        self.paletteWidget.setLayout(self.paletteContainer)
        self.paletteContainer.setContentsMargins(0, 0, 0, 0)

        self.tinContainer.addWidget(self.mixerWidget, -1)
        self.tinContainer.addWidget(self.paletteWidget, 2)

        # palette trays
        self.paletteTrayDropdown = QComboBox()
        self.paletteTrayDropdown.addItems(['default tray'] + self.ps.getPaletteList())
        self.paletteTrayDropdown.setCurrentIndex(0)
        self.paletteTrayDropdown.setMaximumWidth(60)
        self.paletteTrayDropdown.currentIndexChanged.connect(self.loadPaletteFromTray)
        self.mixerContainer.addWidget(self.paletteTrayDropdown, 0, Qt.AlignHCenter)

        # todo make ticks work
        self.mixRateLabel = QLabel()
        self.mixRateLabel.setText("Mix %")
        self.mixRateSlider = QSlider(Qt.Orientation.Vertical, self)
        self.mixRateSlider.setRange(1, 100)
        self.mixRateSlider.setSingleStep(1)
        self.mixRateSlider.setValue(50)
        self.mixRateSlider.setPageStep(10)
        self.mixRateSlider.TickPosition(QSlider.TickPosition.TicksRight)
        self.mixRateSlider.setTickInterval(10)
        self.mixRateSlider.valueChanged.connect(lambda value: self.updateMixRate(value))
        self.mixerContainer.addWidget(self.mixRateLabel, 0, Qt.AlignHCenter)
        self.mixerContainer.addWidget(self.mixRateSlider, 0, Qt.AlignHCenter)

        # mixmode dropdown
        self.mixModeDropdown = QComboBox()
        self.mixModeDropdown.addItems(self.mixModes.keys())
        self.mixModeDropdown.setCurrentIndex(self.sm.getMixingMode())
        self.mixModeDropdown.setMaximumWidth(60)
        self.mixModeDropdown.currentIndexChanged.connect(self.mixModeChanged)
        self.mixerContainer.addWidget(self.mixModeDropdown, 0, Qt.AlignHCenter)

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

        # color spot
        self.colorSpotter = ColorTray(True)

        self.buttonLock = QToolButton()
        self.buttonLock.setIcon(Krita.instance().icon("unlocked"))
        self.buttonLock.setSizePolicy(toolbuttonSizePolicy)

        self.buttonErase = QToolButton()
        self.buttonErase.setIcon(Krita.instance().icon("krita_tool_lazybrush"))
        self.buttonErase.setSizePolicy(toolbuttonSizePolicy)

        self.buttonCleanBrush = QToolButton()
        self.buttonCleanBrush.setIcon(QIcon(os.path.dirname(os.path.realpath(__file__)) +
                                            '/assets/light_krita_tool_freehand_wash.svg'))
        self.buttonCleanBrush.setSizePolicy(toolbuttonSizePolicy)

        self.buttonUndo = QToolButton()
        self.buttonUndo.setIcon(Krita.instance().icon("edit-undo"))
        self.buttonUndo.setSizePolicy(toolbuttonSizePolicy)

        self.buttonConfigure = QToolButton()
        self.buttonConfigure.setIcon(Krita.instance().icon("configure-shortcuts"))
        self.buttonConfigure.setSizePolicy(toolbuttonSizePolicy)

        # self.buttonHsvText = QToolButton()
        # self.buttonHsvText.setIcon(Krita.instance().icon("view-list-text"))
        # self.buttonHsvText.setSizePolicy(toolbuttonSizePolicy)

        self.buttonSvPalette = QToolButton()
        self.buttonSvPalette.setIcon(Krita.instance().icon('document-save'))
        self.buttonSvPalette.setSizePolicy(toolbuttonSizePolicy)

        sizegrip = QSizeGrip(self.rootWidget)
        sizegrip.setSizePolicy(toolbuttonSizePolicy)

        self.toolboxWidget = QWidget()
        self.toolboxContainer = QHBoxLayout()
        self.toolboxWidget.setLayout(self.toolboxContainer)
        self.toolboxContainer.setContentsMargins(0, 10, 0, 0)

        self.toolboxContainer.addWidget(self.buttonLock)
        self.toolboxContainer.addWidget(self.buttonErase)
        self.toolboxContainer.addWidget(self.buttonCleanBrush)
        self.toolboxContainer.addWidget(self.buttonUndo)
        self.toolboxContainer.addWidget(self.buttonSvPalette)
        self.toolboxContainer.addWidget(self.buttonConfigure)
        self.toolboxContainer.addWidget(sizegrip)

        self.bodyContainer.addWidget(self.tinWidget, 10)
        self.bodyContainer.addWidget(self.toolboxWidget, 0)
        self.bodyContainer.addWidget(self.colorSpotter, 1)

        # pushes everything to the top
        self.spacer = QSpacerItem(1, 3, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.fillMainPaletteColors()

    def mixModeChanged(self):
        # print(self.mixModeDropdown.currentIndex())
        self.sm.saveSettings(mixingMode=self.mixModeDropdown.currentIndex())

    def updatePaletteTrayDropdown(self):
        self.paletteTrayDropdown.clear()
        self.paletteTrayDropdown.addItems(['default tray'] + self.ps.getPaletteList())

    def loadPaletteFromTray(self):
        palette = self.paletteTrayDropdown.currentText()
        # print(palette)
        if palette != 'default tray':
            try:
                self.swatchRGB = self.ps.getPaletteAsJSON(palette)['palette']
                self.history.appendPalette(self.swatchRGB)
            except Exception as e:
                print(f"Error executing loading palette does not exists or empty")

    def scratchpadUi(self):
        self.scratchpad.setModeManually(False)  # allows mode to be set by GUI controls ## TODO: Why is not setting this crashing?
        self.scratchpad.linkCanvasZoom(False)
        
        # scratchpad
        self.mixingBoardWidget = QWidget()
        self.mixingBoardContainer = QVBoxLayout()
        self.mixingBoardWidget.setLayout(self.mixingBoardContainer)
        self.mixingBoardContainer.setContentsMargins(0, 0, 0, 0)
        self.mixingBoardContainer.addWidget(self.scratchpad, 3)

        # tools
        toolbuttonSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.mixingBoardToolsWidget = QWidget()
        self.mixingBoardToolsContainer = QGridLayout()
        self.mixingBoardToolsWidget.setLayout(self.mixingBoardToolsContainer)
        self.mixingBoardToolsContainer.setContentsMargins(0, 0, 0, 0)
        self.mixingBoardToolsContainer.setHorizontalSpacing(10)

        self.buttonPaintMode = QToolButton()
        self.buttonPaintMode.setIcon(Krita.instance().icon("krita_tool_freehand"))
        self.buttonPaintMode.setAutoRaise(True)
        self.buttonPaintMode.setToolTip("Paint Mode")
        self.buttonPaintMode.setSizePolicy(toolbuttonSizePolicy)

        self.buttonPanMode = QToolButton()
        self.buttonPanMode.setIcon(Krita.instance().icon("tool_pan"))
        self.buttonPanMode.setAutoRaise(True)
        self.buttonPanMode.setToolTip("Pan Mode")
        self.buttonPanMode.setSizePolicy(toolbuttonSizePolicy)

        # TODO: do it using ctrl click 
        # https://krita-artists.org/t/how-to-right-click-on-scratchpad-to-harvest-colors/72412/8
        self.buttonColorPickMode = QToolButton()
        self.buttonColorPickMode.setIcon(Krita.instance().icon("krita_tool_color_sampler"))
        self.buttonColorPickMode.setAutoRaise(True)
        self.buttonColorPickMode.setToolTip("Color Pick Mode")
        self.buttonColorPickMode.setSizePolicy(toolbuttonSizePolicy)

        self.buttonClearScratchpad = QToolButton()
        self.buttonClearScratchpad.setAutoRaise(True)
        self.buttonClearScratchpad.setIcon(Krita.instance().icon("deletelayer"))
        self.buttonClearScratchpad.setSizePolicy(toolbuttonSizePolicy)

        self.mixingBoardToolsContainer.addWidget(self.buttonPaintMode, 0, 0, 1, 1)
        self.mixingBoardToolsContainer.addWidget(self.buttonPanMode, 0, 1, 1, 1)
        self.mixingBoardToolsContainer.addWidget(self.buttonClearScratchpad, 0, 2, 1, 1)
        self.mixingBoardToolsContainer.addWidget(self.buttonColorPickMode, 1, 0, 1, 3)

        self.mixingBoardContainer.addWidget(self.mixingBoardToolsWidget, -1, Qt.AlignHCenter)
        self.tinContainer.addWidget(self.mixingBoardWidget, 1)

        sc = next((w for w in self.scratchpad.findChildren(QWidget)
                   if w.metaObject().className() == 'KisScratchPad'), None)
        if sc:
            sc.installEventFilter(self)

        # HACK: Constantly set the painting mode until another mode is clicked
        # self.setDefaultModeTimer.timeout.connect(self.changeToPaintingMode)
        # self.setDefaultModeTimer.start(1000)

        self.buttonClearScratchpad.clicked.connect(self.clearScratchpad)
        self.buttonPaintMode.clicked.connect(self.changeToPaintingMode)
        self.buttonPanMode.clicked.connect(self.changeToPanMode)
        self.buttonColorPickMode.clicked.connect(self.changeToColorPickMode)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier:
                print("press")
                self.changeToColorPickMode()
                return False  # event handled True
        elif event.type() == QEvent.MouseButtonRelease or event.type() == QEvent.TabletRelease:
            print("release")
            # self.setDefaultModeTimer.stop()  # stop default mode timer
            QTimer.singleShot(50, lambda: self.scratchpad.setMode("painting"))
            return False  # event handled True
        return False

    def changeToColorPickMode(self):
        # self.setDefaultModeTimer.stop()  # stop default mode timer
        self.scratchpad.setMode("colorsampling")


    def changeToPaintingMode(self):
        self.scratchpad.setMode("painting")

    def clearScratchpad(self):
        self.scratchpad.clear()

    def changeToPanMode(self):
        # self.setDefaultModeTimer.stop()  # hack for setting default to paint mode
        self.scratchpad.setMode("panning")

    def changeToColorPickMode(self):
        # self.setDefaultModeTimer.stop()  # hack for setting default to paint mode
        self.scratchpad.setMode("colorsampling")

    def setScratchpadEnabled(self, enabled):
        self.scratchpad.setEnabled(enabled)

    def setMixingBoard(self, canvas):
        self.canvasColor = QColor(180, 180, 180)
        self.scratchpad = Scratchpad(canvas.view(), self.canvasColor)
        self.scratchpad.setFillColor(self.canvasColor)
        self.scratchpad.clear()
        self.expandSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.scratchpad.setSizePolicy(self.expandSizePolicy)
        self.scratchpad = Scratchpad(canvas.view(), QColor(180, 180, 180))
        self.scratchpadUi()

    def subscribeColorChanges(self):
        app = Krita.instance()
        colorSelectorNg = next((d for d in app.dockers() if d.objectName() == 'ColorSelectorNg'), None)
        for child in colorSelectorNg.findChildren(QObject):
            meta = child.metaObject()
            if meta.className() in {
                'KisColorSelectorRing', 'KisColorSelectorTriangle',
                'KisColorSelectorSimple', 'KisColorSelectorWheel'
            }:
                self.foregroundSignal = getattr(child, 'update')
                self.foregroundSignal.connect(self.onColorChange)

    def unsubscribeColorChanges(self):
        self.foregroundSignal.disconnect()
        # self.foregroundSignal = None

    def onColorChange(self):
        app = Krita.instance()
        win = app.activeWindow()
        view = win.activeView()
        cfg = view.foregroundColor().colorForCanvas(view.canvas())
        self.colorSpotter.setColorRGB(cfg.red(), cfg.green(), cfg.blue())

    def canvasChanged(self, canvas):
        '''
            important, since it uses resources from the document itself
            this handles when and how it loads a data, explain better
        '''
        if canvas:
            if Krita.instance().activeDocument() and canvas.view():
                self.connectColorGrid()
                self._kraActiveDocument = canvas.view().document()
                self.history.reset()
                self.subscribeColorChanges()
                if not self.scratchpad:
                    self.setMixingBoard(canvas)
                else:
                    self.setScratchpadEnabled(True)
            else:
                self.disconnectColorGrid()
        else:
            self.disconnectColorGrid()
            if self.foregroundSignal:
                self.unsubscribeColorChanges()
            if self.scratchpad:
                self.setScratchpadEnabled(False)
        self.annotationService.document = self._kraActiveDocument
        self.annotationService.startup()
        self.loadAnnotationColors()

    def connectButtons(self):
        self.buttonConfigure.clicked.connect(self.openSetting)
        self.buttonUndo.clicked.connect(self.undo)

    def connectColorGrid(self):
        # Disconnect existing connections to avoid multiple connections
        try:
            self.buttonLock.clicked.disconnect()
            self.buttonErase.clicked.disconnect()
            self.buttonCleanBrush.clicked.disconnect()
            self.buttonSvPalette.clicked.disconnect()
        except TypeError:
            pass
        # self.buttonFg.clicked.connect(self.toggleUseFg)
        self.buttonLock.clicked.connect(self.toggleLock)
        self.buttonErase.clicked.connect(self.toggleErase)
        self.buttonCleanBrush.clicked.connect(self.setBrushAsClean)
        self.buttonSvPalette.clicked.connect(self.openSavePalette)
        for row in self.colorGrid:
            for color in row:
                # Disconnect existing connections to avoid multiple connections
                try:
                    color.clicked.disconnect()
                except TypeError:
                    pass
                color.clicked.connect(partial(self.colorTrayClickEvent, color))

    def disconnectColorGrid(self):
        self.useFg = False
        self.buttonLock.setIcon(Krita.instance().icon("unlocked"))
        self.lock = LockState.OPEN
        self.buttonErase.setIcon(Krita.instance().icon("krita_tool_lazybrush"))
        self.erase = False
        self.buttonCleanBrush.setIcon(
            QIcon(os.path.dirname(os.path.realpath(__file__)) + '/assets/light_krita_tool_freehand_wash.svg')
        )
        self.buttonLock.disconnect()
        self.buttonErase.disconnect()
        self.buttonCleanBrush.disconnect()
        self.buttonSvPalette.disconnect()
        for row in self.colorGrid:
            for color in row:
                color.disconnect()

    def avoidLockingMinSize(self):
        self.rootWidget.setMinimumSize(30, 30)

    def toggleDockerVisibility(self):
        if not self.minimizeButton.isChecked():
            self.tinWidget.setVisible(True)
            self.toolboxWidget.setVisible(True)
            self.minimizeButton.setIcon(Krita.instance().icon("visible"))
            self.bodyContainer.removeItem(self.spacer)
            if self.currentDockerHeight > 40:
                self.rootWidget.setMinimumSize(self.currentDockerWidth, self.currentDockerHeight)
            else:
                self.rootWidget.setMinimumSize(350, 275)
            QTimer.singleShot(50, self.avoidLockingMinSize)
            self.rootWidget.setMaximumSize(1000, 1000)
        else:
            self.tinWidget.setVisible(False)
            self.toolboxWidget.setVisible(False)
            self.minimizeButton.setIcon(Krita.instance().icon("novisible"))
            self.currentDockerWidth = self.rootWidget.size().width()
            self.currentDockerHeight = self.rootWidget.size().height()
            if self.sm.getMinizeRetainWitdh():
                self.rootWidget.setMaximumSize(self.currentDockerWidth, 25)
            else:
                self.rootWidget.setMaximumSize(60, 25)
            self.bodyContainer.addSpacerItem(self.spacer)

    def setFgColor(self, colorTray):
        rgb = colorTray.getColorRGB()
        self.colorSpotter.setColorRGB(rgb['red'], rgb['green'], rgb['blue'])
        colorToSet = colorTray.getColorForSet(
            Krita.instance().activeDocument(),
            Krita.instance().activeWindow().activeView().canvas()
        )
        Krita.instance().activeWindow().activeView().setForeGroundColor(colorToSet)

    def toggleUseFg(self):
        if self.useFg:
            self.buttonFg.setIcon(Krita.instance().icon("showColoringOff"))
            self.useFg = False
        else:
            self.buttonFg.setIcon(Krita.instance().icon("showColoring"))
            self.useFg = True

    def toggleLock(self):
        if self.lock == LockState.OPEN:
            self.buttonLock.setIcon(Krita.instance().icon('mesh_cursor_locked'))
            self.lock = LockState.LOCKED
            self.lockUsed = False
        elif self.lock == LockState.LOCKED and not self.lockUsed:
            self.buttonLock.setIcon(Krita.instance().icon("locked"))
            self.lock = LockState.CLOSE
        elif self.lock == LockState.LOCKED and self.lockUsed:
            self.buttonLock.setIcon(Krita.instance().icon("unlocked"))
            self.lock = LockState.OPEN
        elif self.lock == LockState.CLOSE:
            self.buttonLock.setIcon(Krita.instance().icon("unlocked"))
            self.lock = LockState.OPEN

    def toggleErase(self):
        if self.erase:
            self.buttonErase.setIcon(Krita.instance().icon("krita_tool_lazybrush"))
            self.erase = False
        else:
            self.buttonErase.setIcon(Krita.instance().icon("draw-eraser"))
            self.erase = True

    def setBrushAsClean(self):
        # make the selection clearer
        self.buttonCleanBrush.setIcon(
            QIcon(os.path.dirname(os.path.realpath(__file__)) +
                  '/assets/light_krita_tool_freehand_wash_selected.svg')
        )
        self.cleanBrush = True

    def colorTrayClickEvent(self, colorTray):
        if self.cleanBrush:
            self.setFgColor(colorTray)
            self.cleanBrush = False
            self.buttonCleanBrush.setIcon(
                QIcon(os.path.dirname(os.path.realpath(__file__)) +
                      '/assets/light_krita_tool_freehand_wash.svg')
            )
        elif colorTray.isMixable() and self.lock == LockState.OPEN:
            self.colorMix(colorTray)
        elif self.lock == LockState.LOCKED:
            colorTray.toggleMixability()
            # if used do not return to open instead flag it and if toggle then go to open
            self.lockUsed = True
        else:
            self.setFgColor(colorTray)

    def updateMixRate(self, value):
        self.mixRate = value

    def colorMix(self, colorTray):
        mr = self.mixRate
        boxRGB = colorTray.getColorRGB()
        view = Krita.instance().activeWindow().activeView()
        cfg = view.foregroundColor().colorForCanvas(view.canvas())
        mixinMode = self.mixModes[self.mixModeDropdown.currentText()]

        if not self.erase:
            if boxRGB["red"] == GRAY["red"] and boxRGB["green"] == GRAY["green"] and boxRGB["blue"] == GRAY["blue"]:
                colorTray.setColorHSV(cfg.hue(), cfg.saturation(), cfg.value())
            else:
                primaryRGB = [boxRGB['red'], boxRGB['green'], boxRGB['blue']]
                secondaryRGB = [cfg.red(), cfg.green(), cfg.blue()]
                mixed = mixinMode(primaryRGB, secondaryRGB, mr / 100)
                red, green, blue = 0, 1, 2
                colorTray.setColorRGB(mixed[red], mixed[green], mixed[blue])
                self.setFgColor(colorTray)
        else:
            colorTray.setColorHSV(GRAY["hue"], GRAY["sat"], GRAY["val"])
            self.setFgColor(colorTray)

        self.printColorGrid()

    def loadAnnotationColors(self):
        if (self.annotationService.palette and self.colorGrid):
            for row in range(len(self.colorGrid)):
                for col in range(len(self.colorGrid[row])):
                    self.colorGrid[row][col].importRGB(self.annotationService.palette[row][col])
            self.history.appendPalette(self.annotationService.palette)

    def openSetting(self):
        if self.settingDialog is None:
            self.settingDialog = SettingsUI(self.sm, self)
            self.settingDialog.show()
        elif not self.settingDialog.isVisible():
            self.settingDialog.show()
            # self.settingDialog.loadDefault()
        else:
            pass
        self.moveDialog(self.settingDialog)

    def openSavePalette(self):
        if self.svPaletteDialog is None:
            self.svPaletteDialog = SavePaletteDialog(self, "Save Color Palette")
            self.svPaletteDialog.show()
        elif not self.svPaletteDialog.isVisible():
            self.svPaletteDialog.loadDefault()
            self.svPaletteDialog.show()
        else:
            pass
        self.moveDialog(self.svPaletteDialog)

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

    def fillMainPaletteColors(self):
        self.colorGrid[0][0].setColorHSV(PALETTE_HSV[0]["hue"], PALETTE_HSV[0]["sat"], PALETTE_HSV[0]["val"])
        self.colorGrid[1][0].setColorHSV(PALETTE_HSV[1]["hue"], PALETTE_HSV[1]["sat"], PALETTE_HSV[1]["val"])
        self.colorGrid[2][0].setColorHSV(PALETTE_HSV[2]["hue"], PALETTE_HSV[2]["sat"], PALETTE_HSV[2]["val"])
        self.colorGrid[3][0].setColorHSV(PALETTE_HSV[3]["hue"], PALETTE_HSV[3]["sat"], PALETTE_HSV[3]["val"])
        self.colorGrid[4][0].setColorHSV(PALETTE_HSV[4]["hue"], PALETTE_HSV[4]["sat"], PALETTE_HSV[4]["val"])
        self.colorGrid[5][0].setColorHSV(PALETTE_HSV[5]["hue"], PALETTE_HSV[5]["sat"], PALETTE_HSV[5]["val"])
        self.colorGrid[6][0].setColorHSV(PALETTE_HSV[6]["hue"], PALETTE_HSV[6]["sat"], PALETTE_HSV[6]["val"])
        self.colorGrid[7][0].setColorHSV(PALETTE_HSV[7]["hue"], PALETTE_HSV[7]["sat"], PALETTE_HSV[7]["val"])

        self.colorGrid[0][5].setColorHSV(PALETTE_HSV[8]["hue"], PALETTE_HSV[8]["sat"], PALETTE_HSV[8]["val"])
        self.colorGrid[1][5].setColorHSV(PALETTE_HSV[9]["hue"], PALETTE_HSV[9]["sat"], PALETTE_HSV[9]["val"])
        self.colorGrid[2][5].setColorHSV(PALETTE_HSV[10]["hue"], PALETTE_HSV[10]["sat"], PALETTE_HSV[10]["val"])
        self.colorGrid[3][5].setColorHSV(PALETTE_HSV[11]["hue"], PALETTE_HSV[11]["sat"], PALETTE_HSV[11]["val"])
        self.colorGrid[4][5].setColorHSV(PALETTE_HSV[12]["hue"], PALETTE_HSV[12]["sat"], PALETTE_HSV[12]["val"])
        self.colorGrid[5][5].setColorHSV(PALETTE_HSV[13]["hue"], PALETTE_HSV[13]["sat"], PALETTE_HSV[13]["val"])
        self.colorGrid[6][5].setColorHSV(PALETTE_HSV[14]["hue"], PALETTE_HSV[14]["sat"], PALETTE_HSV[14]["val"])
        self.colorGrid[7][5].setColorHSV(PALETTE_HSV[15]["hue"], PALETTE_HSV[15]["sat"], PALETTE_HSV[15]["val"])

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
    DOCKER_ID,
    DockWidgetFactoryBase.DockRight,
    PaletteTin
)
instance.addDockWidgetFactory(dock_widget_factory)
