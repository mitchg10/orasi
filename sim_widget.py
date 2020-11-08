#!/usr/bin/env python3

"""
Author: Ellen
Created: May 15, 2020
Updated: Nov. 6, 2020

PyQt class for main window of SIMformation widget, holding all HIL objects 
"""

from functools import partial
import sys
import queue
from PyQt5.QtWidgets import (QWidget, QLineEdit, QApplication, QLabel,
                             QPushButton,
                             QHBoxLayout, QVBoxLayout, QGridLayout,
                             QStyleOption, QStyle)
from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QPixmap, QPalette, QBrush

import hil_widget
import guiData


def formatSigs(data):
    if data > 10000000:
        return ('%.2E' % data)
    else:
        return ('%i' % round(data))


class SIMWidget(QWidget):
    def __init__(self, orientation):
        super().__init__()

        self.resetQueue = queue.Queue()
        self.seqNum = 1

        if orientation == 'V':

            self.resize(400, 550)  # change to 800ish

            layout = QVBoxLayout()
            topLayout = QGridLayout()

            self.distance = QLabel("0 miles")
            self.time = QLabel("0 hours")

            topLayout.addWidget(self.distance, 0, 0)
            topLayout.addWidget(self.time, 0, 1)
            layout.addLayout(topLayout)

            self.hilVec = []

            for i in range(1, guiData.numHILs + 1):
                hil = hil_widget.HILWidget(str(i))
                self.hilVec.append(hil)
                layout.addWidget(hil)

            self.userInput = QLineEdit()
            layout.addWidget(self.userInput)

            self.resetButton = QPushButton("RESET ALL")

            self.setLayout(layout)
            self.setWindowTitle("SIMformation Widget")

            self.distance.setStyleSheet("color: white; font: bold 35px")
            self.time.setStyleSheet("color: white; font: bold 35px")

        elif orientation == 'H':

            self.resize(900, 600)  # change to 800ish

            layout = QGridLayout()
            topLayout = QGridLayout()

            self.distance = QLabel("0 miles")
            self.time = QLabel("0 hours")
            self.test = QLabel("0 tests")
            self.resetButton = QPushButton("RESET ALL")

            topLayout.addWidget(self.distance, 0, 0)
            topLayout.addWidget(self.time, 0, 1)
            topLayout.addWidget(self.test, 0, 2)
            topLayout.addWidget(self.resetButton, 0, 3)
            layout.addLayout(topLayout, 0, 0, 1, 0)

            if guiData.numHILs % 3 == 0:
                totalRows = int(guiData.numHILs / 3)
            else:
                totalRows = int(guiData.numHILs / 3) + 1

            self.hilVec = []

            n = 1
            for i in range(0, totalRows):
                for j in range(0, 3):
                    if n <= guiData.numHILs:
                        hil = hil_widget.HILWidget(str(n))
                        self.hilVec.append(hil)
                        layout.addWidget(hil, i + 1, j)
                    n = n + 1

            self.userInput = QLineEdit()
            # layout.addWidget(self.userInput, totalRows + 1, 0, totalRows + 1, 2)

            self.setLayout(layout)
            self.setWindowTitle("SIMformation Widget")

            self.distance.setStyleSheet("color: white; font: bold 35px")
            self.time.setStyleSheet("color: white; font: bold 35px")
            self.test.setStyleSheet("color: white; font: bold 35px")
            self.resetButton.setStyleSheet(
                "font: bold 20px; color: white; background-color: rgba(255, 255, 255, 0); border: 0px; outline: 0px")

        background = QPixmap("paul-gilmore-mqO0Rf-PUMs-unsplash.jpg")
        # background = QPixmap("/home/pi/Documents/Orasi/matteo-bernardis-QpIayO5KIRE-unsplash.jpg")
        background = background.scaled(
            self.size(), Qt.IgnoreAspectRatio, Qt.FastTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

        self.userInput.returnPressed.connect(self.changeColor)
        self.resetButton.pressed.connect(self.resetHandler)
        for i in range(guiData.numHILs):
            self.hilVec[i].resetButton.pressed.connect(
                partial(self.resetHandler, i))

    def paintEvent(self, e):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def dataUpdate(self, data):
        self.distance.setText(formatSigs(data.totDistance) + " miles")
        self.time.setText(formatSigs(data.totTime) + " hours")
        self.test.setText(formatSigs(data.totTest) + " tests")

        for i in range(0, guiData.numHILs):
            self.hilVec[i].curDistance.setText(
                formatSigs(data.hilDataVec[i].hilCurDistance))
            self.hilVec[i].curTime.setText(
                formatSigs(data.hilDataVec[i].hilCurTime))
            self.hilVec[i].curTest.setText(
                formatSigs(data.hilDataVec[i].hilCurTest))
            self.hilVec[i].lifeDistance.setText(
                formatSigs(data.hilDataVec[i].hilLifeDistance))
            self.hilVec[i].lifeTime.setText(
                formatSigs(data.hilDataVec[i].hilLifeTime))
            self.hilVec[i].lifeTest.setText(
                formatSigs(data.hilDataVec[i].hilLifeTest))
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

    def resetHandler(self, num=-1):
        self.resetQueue.put(num)
        self.seqNum += 1


def main():
    app = QApplication(sys.argv)
    sw = SIMWidget('H')
    sw.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
