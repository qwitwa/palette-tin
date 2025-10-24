from krita import *
from PyQt5.QtCore import pyqtSignal, QPoint, QLine, qDebug
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen
from PyQt5.QtWidgets import QWidget

# CROSS_COLOR = QColor(200, 50, 50)
NEUTRAL_COLOR = QColor(200, 200, 200)
TRANSPARENT_COLOR = QColor(0, 0, 0, 0)


class ColorTray(QWidget):
    clicked = pyqtSignal(int, int)

    def __init__(self, mixable=False):
        self.color = None
        super().__init__()
        self.mixable = mixable
        self.cross_pen = QPen()
        self.cross_pen.setBrush(NEUTRAL_COLOR)

    def paintEvent(self, e):
        self.qp = QPainter()
        self.qp.begin(self)
        if self.isMixable():
            self.drawRectangles()
        else:
            self.drawEllipse()
        if self.color is None:
            self.drawCross()
        self.qp.end()

    def drawCross(self) -> None:
        geom = self.geometry()
        geom_w = geom.width()
        geom_h = geom.height()
        center = QPoint(geom_w // 2, geom_h // 2)
        line_half_length = min(geom_w, geom_h) // 6
        line_width = line_half_length // 2
        right_ascending_diag = QPoint(line_half_length, line_half_length)
        left_ascending_diag = QPoint(-line_half_length, line_half_length)
        self.cross_pen.setWidth(line_width)
        self.qp.setPen(self.cross_pen)
        # self.qp.drawEllipse(center.x(), center.y(), line_half_length, line_half_length)
        self.qp.drawLine(
            QLine(center + right_ascending_diag, center - right_ascending_diag)
        )
        self.qp.drawLine(
            QLine(center + left_ascending_diag, center - left_ascending_diag)
        )

    def drawRectangles(self):
        if self.color:
            self.qp.setBrush(self.color)
        else:
            self.qp.setBrush(TRANSPARENT_COLOR)
        self.qp.drawRect(
            -1, -1, self.geometry().width() + 1, self.geometry().height() + 1
        )

    def drawEllipse(self):
        if self.color:
            self.qp.setBrush(self.color)
        else:
            self.qp.setBrush(TRANSPARENT_COLOR)
        center = QPoint(self.geometry().width() // 2, self.geometry().height() // 2)
        self.qp.drawEllipse(
            center,
            (self.geometry().width() + 1) // 2.2,
            (self.geometry().height() + 1) // 2.2,
        )

    def toggleMixability(self):
        # Toggle the mixable state
        self.mixable = not self.mixable
        # Trigger a repaint to reflect the change
        self.update()

    def deleteColor(self) -> None:
        self.color = None
        self.update()

    def setColorHSV(self, h, s, v):
        self.color = QColor()
        self.color.setHsv(h, s, v, 255)
        self.update()

    def getColorRGB(self):
        if self.color is None:
            return None
        return {
            "red": self.color.red(),
            "green": self.color.green(),
            "blue": self.color.blue(),
        }

    def setColorRGB(self, r, g, b):
        qDebug(f"debugging setColorRGB with r {r}, g {g}, b {b}")
        self.color = QColor()
        self.color.setRgb(r, g, b)
        self.update()

    def getColorForSet(self, doc, canvas):
        # krita class
        colorToSet = ManagedColor(
            doc.colorModel(), doc.colorDepth(), doc.colorProfile()
        )
        toSet = colorToSet.fromQColor(self.color, canvas)

        return toSet

    def isMixable(self):
        return self.mixable

    def exportRGB(self):
        if self.color:
            return [self.color.red(), self.color.green(), self.color.blue()]
        else:
            return None

    def importRGB(self, rgb: list):
        if rgb is not None:
            self.setColorRGB(rgb[0], rgb[1], rgb[2])
        else:
            self.deleteColor()

    def toString(self):
        if self.color is not None:
            return (
                "Red "
                + str(self.color.red())
                + " Green "
                + str(self.color.green())
                + " Blue "
                + str(self.color.blue())
            )
        else:
            return "None"

    def exportHSV(self) -> list:
        if self.color is not None:
            return [self.color.hsvHue(), self.color.hsvSaturation(), self.color.value()]
        else:
            return None

    def mousePressEvent(self, e):
        modifiers = e.modifiers()
        button = e.button()
        self.clicked.emit(button, modifiers)
