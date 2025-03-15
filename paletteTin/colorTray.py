from krita import *  
from PyQt5.QtCore import ( pyqtSignal, QPoint)
from PyQt5.QtGui import (QPainter, QColor)
from PyQt5.QtWidgets import (QWidget)
 
class ColorTray(QWidget):
    clicked = pyqtSignal() 
    
    def __init__(self, mixable = False):  
        self.color = QColor(200, 200, 200)# mid gray
        super().__init__() 
        self.mixable = mixable

    def paintEvent(self, e):
        self.qp = QPainter()
        self.qp.begin(self)
        if self.isMixable():
            self.drawRectangles()
        else:
            self.drawEllipse()
        self.qp.end()
    
    def drawRectangles(self):  
        self.qp.setBrush(self.color)
        self.qp.drawRect(-1, -1, self.geometry().width()+1, self.geometry().height()+1)
    
    def drawEllipse(self):
        self.qp.setBrush(self.color)
        center = QPoint(self.geometry().width() // 2, self.geometry().height() // 2)
        self.qp.drawEllipse(center, (self.geometry().width()+1)//2.2, (self.geometry().height()+1)//2.2)
    
    def toggleMixability(self):
        # Toggle the mixable state
        self.mixable = not self.mixable
        # Trigger a repaint to reflect the change
        self.update()
    
    def setColorHSV(self,h,s,v):
        self.color.setHsv(h,s,v,255)
        self.update()
    
    def getColorRGB(self):
        return {"red": self.color.red(), "green": self.color.green(), "blue":self.color.blue(), "alpha": self.color.alpha()}
    
    def setColorRGB(self,r,g,b,a = 255):
        self.color.setRgb(r, g, b, a)
        self.update()
    
    def getColorForSet(self, doc, canvas): 
        #krita class
        colorToSet = ManagedColor(doc.colorModel(), doc.colorDepth(), doc.colorProfile())
        toSet = colorToSet.fromQColor(self.color, canvas) 
         
        return toSet
    
    def isMixable(self):
        return self.mixable
    
    def exportRGB(self):
        return [self.color.red(),self.color.green(),self.color.blue()]
    
    def importRGB(self, rgb: list):
        self.setColorRGB(rgb[0],rgb[1],rgb[2])
    
    def toString(self):
        return "Red "+str(self.color.red())+" Green "+str(self.color.green())+" Blue "+str(self.color.blue())+" Alpha "+str(self.color.alpha())
    
    def exportHSV(self) -> list:
        return [self.color.hsvHue(), self.color.hsvSaturation(), self.color.value()]
    
    def mousePressEvent(self, e):
        self.clicked.emit()