#!/usr/bin/env python3

"""
Author: Ellen
Created: May 15, 2020
Updated: Nov. 6, 2020

PyQt class for individual HIL objects
"""

# import time
# import queue
# import threading
from datetime import timedelta, datetime

from PyQt5.QtWidgets import (QLabel, QWidget, QSlider, QApplication,
                             QHBoxLayout, QVBoxLayout, QGridLayout,
                             QStyleOption, QStyle, QPushButton, QSizePolicy)
from PyQt5.QtCore import QObject, Qt, QSize, QEvent
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QIcon
import sys


class RQLabel(QLabel):
    def __init__(self, text, size=15, minWidth=60, minHeight=30):
        super().__init__(text)

        self.ratioSet = False
        self.initRatio = self.size()
        self.initFont = size

        self.installEventFilter(self)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        print("minWidth: ", minWidth)
        self.setMinimumSize(minWidth, minHeight)

        print("RQLabel size init: ", self.size().width(),
              " ", self.size().height())

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.Resize):
            if not self.ratioSet:
                self.initRatio = self.size()
                print("label ratioSize: ", self.initRatio)
                self.ratioSet = True
        return super().eventFilter(obj, event)


class RQPushButton(QPushButton):
    def __init__(self, text=None, size=60):
        if text == None:
            super().__init__()
        else:
            super().__init__(text)

        self.ratioSet = False
        self.initRatio = self.size()
        self.initSize = size  # revisit for reset all

        self.installEventFilter(self)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setMinimumSize(40, 40)

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.Resize):
            if not self.ratioSet:
                self.initRatio = self.size()
                print("pushbutton ratioSize: ", self.initRatio)
                self.ratioSet = True
        return super().eventFilter(obj, event)


class HILWidget(QWidget):
    def __init__(self, num=None):
        super().__init__()
        if num is None:
            self.HILnum = RQLabel("0", 50, 30, 60)
        else:
            self.HILnum = RQLabel(num, 50, 30, 60)

        self.color = 't'
        self.fontRatio = 1

        self.curDistance = RQLabel("0")
        self.curTime = RQLabel("0")
        self.curTest = RQLabel("0")
        self.lifeDistance = RQLabel("0")
        self.lifeTime = RQLabel("0")
        self.lifeTest = RQLabel("0")
        curQL = RQLabel("session")
        lifeQL = RQLabel("lifetime")
        dUnit = RQLabel("miles")
        tUnit = RQLabel("hours")
        testUnit = RQLabel("tests")

        self.resetButton = RQPushButton()

        layout = QGridLayout()

        layout.addWidget(self.HILnum, 0, 0)
        layout.addWidget(curQL, 0, 1)
        layout.addWidget(lifeQL, 0, 2)
        layout.addWidget(self.curDistance, 1, 1)
        layout.addWidget(self.curTime, 2, 1)
        layout.addWidget(self.curTest, 3, 1)
        layout.addWidget(self.lifeDistance, 1, 2)
        layout.addWidget(self.lifeTime, 2, 2)
        layout.addWidget(self.lifeTest, 3, 2)
        layout.addWidget(dUnit, 1, 3)
        layout.addWidget(tUnit, 2, 3)
        layout.addWidget(testUnit, 3, 3)
        layout.addWidget(self.resetButton, 0, 3)
        self.setLayout(layout)

        self.ratioSet = False
        self.initRatio = self.size()

        self.setBackground(force=True)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.Resize):
            if not self.ratioSet:
                self.initRatio = self.size()
                print("initRatio: ", self.initRatio)
                self.ratioSet = True
            else:
                ratio = (self.size().width() /
                         self.initRatio.width())
                print("new width: ", self.size().width())
                print("ratio: ", ratio)
                print("height ratio: ", self.size().height() /
                      self.initRatio.height())
                self.setBackground(ratio=ratio)
        return super().eventFilter(obj, event)

    def paintEvent(self, e):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def setBackground(self, color=None, ratio=None, force=False):
        if color == None:
            color = self.color
        if ratio == None:
            ratio = self.fontRatio
        if (force or ratio > self.fontRatio + .1 or ratio < self.fontRatio - .1
                or not color == self.color):
            print("new ratio: ", ratio)
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
                styleColor = "255, 255, 255, 0"
                hilNumColor = "black"
                icon = QIcon('reset_black.png')
            else:
                return

            self.HILnum.setStyleSheet(
                "font: bold " + str(round(ratio*self.HILnum.initFont)) + "px")

            iconSize = ratio*self.resetButton.initSize
            self.resetButton.setIconSize(QSize(iconSize, iconSize))
            self.resetButton.setStyleSheet(
                "background-color: rgba(255, 255, 255, 0); border: 0px; outline: 0px")
            self.resetButton.setIcon(icon)

            self.setStyleSheet("HILWidget{ background-color: rgba(" + styleColor +
                               "); } QLabel{ color: " + hilNumColor + "; font: " +
                               str(round(ratio*self.curDistance.initFont)) + "px }")  # bold

            self.color = color
            self.fontRatio = ratio


def main():
    app = QApplication(sys.argv)
    hw = HILWidget()
    hw.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
