#!/usr/bin/python

"""
Author: Ellen Sawitzki
"""
import time
from PyQt5.QtWidgets import (QLabel, QWidget, QSlider, QApplication,
                             QHBoxLayout, QVBoxLayout, QGridLayout, 
                             QStyleOption, QStyle)
from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QFont, QColor, QPen
import sys

class HILWidget(QWidget):
    def __init__(self, num = None):
        super().__init__()
        if num is None: 
            self.HILnum = QLabel("NA")
        else:
            self.HILnum = QLabel(num)
        
        self.color = 'w'
        
        self.speed = QLabel("0")
        self.curDistance = QLabel("0")
        self.curTime = QLabel("0")
        self.lifeDistance = QLabel("0")
        self.lifeTime = QLabel("0")
        curQL = QLabel("session")
        lifeQL = QLabel("lifetime")
        dUnit = QLabel("miles")
        tUnit = QLabel("hours")
        sUnit = QLabel("mph")

        layout = QGridLayout()

        layout.addWidget(self.HILnum, 0, 0, 3, 0)
        layout.addWidget(curQL, 0, 1)
        layout.addWidget(lifeQL, 0, 2)
        layout.addWidget(self.curDistance, 1, 1)
        layout.addWidget(self.curTime, 2, 1)
        layout.addWidget(self.lifeDistance, 1, 2)
        layout.addWidget(self.lifeTime, 2, 2)
        layout.addWidget(self.speed, 3, 1)
        layout.addWidget(dUnit, 1, 3)
        layout.addWidget(tUnit, 2, 3)
        layout.addWidget(sUnit, 3, 3)
        self.setLayout(layout)

        #self.setStyleSheet("HILWidget{ border: 3px solid white; background-color: rgba(255, 255, 255, 95); } QLabel{ color: white; font: 18px }")
        #self.setStyleSheet("HILWidget{ background-color: rgba(255, 255, 255, 95); } QLabel{ color: white; font: 18px }")
        self.setBackground(self.color)

        self.HILnum.setStyleSheet("font: bold 50px") #70

        #self.initUI()

    # def initUI(self, num = None):

    #     # if num is None: 
    #     #     self.HILnum = QLabel("not initialized")
    #     # else:
    #     #     self.HILnum = QLabel(num)

    #     layout = QVBoxLayout()
    #     layout.addWidget(self.HILnum)
    #     self.setLayout(layout)

    #     # self.setGeometry(300, 300, 390, 210)
    #     # self.setWindowTitle('Burning widget')
    #     # self.show()

    def paintEvent(self, e):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def setBackground(self, color):
        if not color == self.color: 
            hilNumColor = "white"
            if color == 'r':
                styleColor = "252, 87, 45, 90"
            elif color == 'g':
                styleColor = "71, 156, 89, 90"
                hilNumColor = "white"
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
            else:
                return

            #self.setStyleSheet("HILWidget{ border: 3px solid white; background-color: rgba(" + styleColor + "); } QLabel{ color: white; font: 18px }")
            self.setStyleSheet("HILWidget{ background-color: rgba(" + styleColor + "); } QLabel{ color: " + hilNumColor + "; font: 18px }")
            self.color = color    
        
        # self.style().unpolish(self)
        # self.style().polish(self)
        # self.update()

        #print("check2")
        # self.c.updateBW.emit(value)
        # self.wid.repaint()

def main():
    app = QApplication(sys.argv)
    hw = HILWidget()
    hw.show()
    #hw.setBackground('r')
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

