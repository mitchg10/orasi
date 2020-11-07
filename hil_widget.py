#!/usr/bin/python

"""
Author: Ellen Sawitzki
"""
import time
from PyQt5.QtWidgets import (QLabel, QWidget, QSlider, QApplication,
                             QHBoxLayout, QVBoxLayout, QGridLayout, 
                             QStyleOption, QStyle, QPushButton)
from PyQt5.QtCore import QObject, Qt, QSize
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QIcon
import sys

class HILWidget(QWidget):
    def __init__(self, num = None):
        super().__init__()
        if num is None: 
            self.HILnum = QLabel("NA")
        else:
            self.HILnum = QLabel(num)
        
        self.color = 'w'
        
        # self.speed = QLabel("0")
        self.curDistance = QLabel("0")
        self.curTime = QLabel("0")
        self.curTest = QLabel("0")
        self.lifeDistance = QLabel("0")
        self.lifeTime = QLabel("0")
        self.lifeTest = QLabel("0")
        curQL = QLabel("session")
        lifeQL = QLabel("lifetime")
        dUnit = QLabel("miles")
        tUnit = QLabel("hours")
        # sUnit = QLabel("mph")
        testUnit = QLabel("tests")

        self.resetButton = QPushButton()
        self.resetButton.setIconSize(QSize(60,60))

        layout = QGridLayout()

        layout.addWidget(self.HILnum, 0, 0, 1, 1)
        layout.addWidget(curQL, 0, 1)
        layout.addWidget(lifeQL, 0, 2)
        layout.addWidget(self.curDistance, 1, 1)
        layout.addWidget(self.curTime, 2, 1)
        layout.addWidget(self.curTest, 3, 1)
        layout.addWidget(self.lifeDistance, 1, 2)
        layout.addWidget(self.lifeTime, 2, 2)
        layout.addWidget(self.lifeTest, 3, 2)
        # layout.addWidget(self.speed, 3, 1)
        layout.addWidget(dUnit, 1, 3)
        layout.addWidget(tUnit, 2, 3)
        layout.addWidget(testUnit, 3, 3)
        # layout.addWidget(sUnit, 3, 3)
        layout.addWidget(self.resetButton, 0, 3)
        self.setLayout(layout)
        
        self.HILnum.setStyleSheet("font: bold 50px")
        # self.testNum.setStyleSheet("font: bold 20px")
        self.resetButton.setStyleSheet("background-color: rgba(255, 255, 255, 0); border: 0px; outline: 0px")
        
        self.setBackground(self.color)

    def paintEvent(self, e):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def setBackground(self, color):
        if not color == self.color: 
            hilNumColor = "white"
            icon = QIcon('reset_white.png')
            if color == 'r':
                styleColor = "252, 87, 45, 90"
            elif color == 'g':
                styleColor = "71, 156, 89, 90"
                hilNumColor = "white"
                icon = QIcon('reset_white.png')
            elif color == 'y':
                styleColor = "255, 201, 101, 90"
            elif color == 'h':
                styleColor = "109, 113, 117, 90"
            elif color == 'b':
                styleColor = "0, 0, 0, 90"
                hilNumColor = "white"
            elif color == 't':
                styleColor = "0, 0, 0, 0"
                hilNumColor = "black"
                icon = QIcon('reset_black.png')
            else:
                return

            self.resetButton.setIcon(icon)
            self.setStyleSheet("HILWidget{ background-color: rgba(" + styleColor + "); } QLabel{ color: " + hilNumColor + "; font: 18px }")
            self.color = color    
        

def main():
    app = QApplication(sys.argv)
    hw = HILWidget()
    hw.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

