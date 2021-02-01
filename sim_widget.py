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
                             QStyleOption, QStyle, QDesktopWidget)
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QPixmap, QPalette, QBrush

import hil_widget
import guiData


def formatSigs(data):
    if data > 1000000:
        return ('%.2E' % data)
    elif data > 0.01:
        return ('%.3g' % data)
    elif data == 0:
        return '0'
    else:
        return ('%.2E' % data)


class SIMWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.resetQueue = queue.Queue()
        self.resSeqNum = 0

        self.screenSize = QDesktopWidget().screenGeometry(-1)
        print("screen size: ", str(self.screenSize.height()),
              " ", str(self.screenSize.width()))

        self.resize(800, 450)

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

        self.setLayout(layout)
        self.setWindowTitle("SIMformation Widget")

        self.distance.setStyleSheet("color: white; font: bold 35px")
        self.time.setStyleSheet("color: white; font: bold 35px")
        self.test.setStyleSheet("color: white; font: bold 35px")
        self.resetButton.setStyleSheet(
            "font: bold 20px; color: white; background-color: rgba(255, 255, 255, 0); border: 0px; outline: 0px")

        background = QPixmap("paul-gilmore-mqO0Rf-PUMs-unsplash.jpg")
        self.background = background.scaled(
            self.size(), Qt.IgnoreAspectRatio, Qt.FastTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

        self.resetButton.pressed.connect(self.resetHandler)
        for i in range(guiData.numHILs):
            self.hilVec[i].resetButton.pressed.connect(
                partial(self.resetHandler, i))

        self.installEventFilter(self)
        self.lastSize = self.size()

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.Resize):

            size = self.size()
            print("newSize: ", size)
            print("width: ", size.width())
            if size.width() > self.screenSize.width():
                width = self.screenSize.width()
                print("fixed too large width to: ", size.width())
            height = size.width()*(guiData.guiRatio[1]/guiData.guiRatio[0])
            print("height: ", height)
            self.resize(size.width(), height)
            print("lastSize: ", self.lastSize)
            self.lastSize = self.size()

            self.background = self.background.scaled(
                self.size(), Qt.IgnoreAspectRatio, Qt.FastTransformation)
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(self.background))
            self.setPalette(palette)

        return super().eventFilter(obj, event)

    def paintEvent(self, e):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def dataUpdate(self, data):
        self.distance.setText(formatSigs(data.totDistance) + " miles")
        self.time.setText(formatSigs(data.totTime) + " hours")
        self.test.setText(formatSigs(data.totTest) + " tests")

        for i in range(guiData.numHILs):
            print("hil number: ", i)
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

    def resetHandler(self, num=-1):
        self.resetQueue.put(guiData.resetMsg(num, self.resSeqNum))
        self.resSeqNum += 1


def main():
    app = QApplication(sys.argv)
    sw = SIMWidget()
    sw.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
