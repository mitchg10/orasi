#!/usr/bin/python

"""
Author: Ellen Sawitzki
"""

from PyQt5.QtWidgets import (QWidget, QLineEdit, QApplication, QLabel,
                             QPushButton,
                             QHBoxLayout, QVBoxLayout, QGridLayout,
                             QStyleOption, QStyle)
from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QPixmap, QPalette, QBrush
import sys
import queue
import threading
from time import sleep

import hil_widget
import guiData

class SIMWidget(QWidget):
    def __init__(self, orientation):
        super().__init__()

        self.resetQueue = queue.Queue()

        if orientation == 'V':

            self.resize(400, 550) #change to 800ish

            layout = QVBoxLayout()
            topLayout = QGridLayout()

            self.distance = QLabel("0 miles")
            self.time = QLabel("0 hours")

            topLayout.addWidget(self.distance, 0, 0)
            topLayout.addWidget(self.time, 0, 1)
            layout.addLayout(topLayout)

            self.hilVec = []

            for i in range (1, guiData.numHILs + 1):
                hil = hil_widget.HILWidget(str(i))
                self.hilVec.append(hil)
                layout.addWidget(hil)

            self.userInput = QLineEdit()
            layout.addWidget(self.userInput)

            self.resetButton = QPushButton("reset")

            self.setLayout(layout)
            self.setWindowTitle("SIMformation Widget")

            self.distance.setStyleSheet("color: white; font: bold 35px")
            self.time.setStyleSheet("color: white; font: bold 35px")

        elif orientation == 'H':

            self.resize(900, 600) #change to 800ish

            layout = QGridLayout()
            topLayout = QGridLayout()

            self.distance = QLabel("0 miles")
            self.time = QLabel("0 hours")
            self.resetButton = QPushButton("RESET")

            topLayout.addWidget(self.distance, 0, 0)
            topLayout.addWidget(self.time, 0, 1)
            topLayout.addWidget(self.resetButton, 0, 2)
            layout.addLayout(topLayout, 0, 0, 1, 0)

            if guiData.numHILs % 3 == 0: totalRows = int(guiData.numHILs / 3)
            else: totalRows = int(guiData.numHILs / 3) + 1

            self.hilVec = []

            n = 1
            for i in range (0, totalRows):
                for j in range (0, 3):
                    if n <= guiData.numHILs:
                        hil = hil_widget.HILWidget(str(n))
                        self.hilVec.append(hil)
                        layout.addWidget(hil, i + 1, j)
                    n = n + 1

            self.userInput = QLineEdit()
            #layout.addWidget(self.userInput, totalRows + 1, 0, totalRows + 1, 2)

            self.setLayout(layout)
            self.setWindowTitle("SIMformation Widget")

            self.distance.setStyleSheet("color: white; font: bold 35px")
            self.time.setStyleSheet("color: white; font: bold 35px")

        background = QPixmap("/home/pi/Documents/Orasi/matteo-bernardis-QpIayO5KIRE-unsplash.jpg")
        background = background.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.FastTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

        #self.initUI()

        self.userInput.returnPressed.connect(self.changeColor)
        self.resetButton.pressed.connect(self.resetHandler)

    def paintEvent(self, e):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def dataUpdate(self, data):
        self.distance.setText(('%.2f'%data.totDistance) + " miles")
        self.time.setText(('%.2f'%data.totTime) + " hours")

        for i in range(0, guiData.numHILs):
            self.hilVec[i].speed.setText(('%.2f'%data.hilDataVec[i].hilCurMPH))
            self.hilVec[i].curDistance.setText(('%.2f'%data.hilDataVec[i].hilCurDistance))
            self.hilVec[i].curTime.setText(('%.2f'%data.hilDataVec[i].hilCurTime))
            self.hilVec[i].lifeDistance.setText(('%.2f'%data.hilDataVec[i].hilLifeDistance))
            self.hilVec[i].lifeTime.setText(('%.2f'%data.hilDataVec[i].hilLifeTime))
            if data.hilDataVec[i].status == guiData.Status.STANDBY:
                self.hilVec[i].setBackground('t')
            elif data.hilDataVec[i].status == guiData.Status.RUNNING:
                self.hilVec[i].setBackground('g')

    def changeColor(self):
        t = self.userInput.text()
        self.userInput.setText("")

        hilNumCheck = ""

        for i in range(1, guiData.numHILs + 1):
            hilNumCheck = hilNumCheck + str(i)

        chars = set(hilNumCheck)

        if (len(t) == 2) and any((c in chars) for c in t[0]):
            self.hilVec[int(t[0]) - 1].setBackground(t[1])

    def resetHandler(self):
        self.resetQueue.put(True) #doesn't matter what you put, just put something

#     def initUI(self):

#         self.setMinimumSize(1, 30)
#         self.value = 75
#         self.num = [75, 150, 225, 300, 375, 450, 525, 600, 675]


def main():
    app = QApplication(sys.argv)
    q = queue.Queue()
    sw = SIMWidget(q)
    sw.show()
    sys.exit(app.exec_())
    # while 1:
    #     sleep(1)
    #     countGet = countGet + 1
    #     getData = q.get()
    #     guiData = getData
    #     print(f'data get {countGet}: {getData}')
    #     q.task_done()



if __name__ == '__main__':
    main()
