from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRect

class RectangleWidget(QWidget):
    def __init__(self):
        super().__init__()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Solid blue rectangle
        painter.setBrush(QBrush(QColor(0, 0, 255)))  # Solid blue
        outerRect = QRect(10, 10, self.width()-20, self.height()-20)
        painter.drawRect(outerRect)
        
        # Transparent inner rectangle
        painter.setBrush(QBrush(Qt.transparent))  # Transparent fill
        painter.setPen(QPen(QColor(0, 0, 0)))  # Black outline
        innerRectWidth = outerRect.width() // 2
        innerRectHeight = outerRect.height() // 2
        innerRectX = outerRect.center().x() - innerRectWidth // 2
        innerRectY = outerRect.center().y() - innerRectHeight // 2
        innerRect = QRect(innerRectX, innerRectY, innerRectWidth, innerRectHeight)
        painter.drawRect(innerRect)