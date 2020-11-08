#!/usr/bin/env python

"""
Author: Ellen
Created: Sep. 20, 2020
Updated: Nov. 6, 2020

Classes to hold a package of data to update an entire SimWidget window
"""

from enum import Enum

import sim_widget

numHILs = 6


class Status(Enum):
    RUNNING = 0
    STANDBY = 1
    FAILED = 2


class hilData():
    def __init__(self):
        self.status = Status.STANDBY
        self.hilCurMPH = 0
        self.hilCurDistance = 0
        self.hilCurTime = 0
        self.hilCurTest = 0
        self.hilLifeDistance = 0
        self.hilLifeTime = 0
        self.hilLifeTest = 0

    def reset(self):
        self.hilCurMPH = 0
        self.hilCurDistance = 0
        self.hilCurTime = 0


class simData():
    def __init__(self):
        self.totDistance = 0
        self.totTime = 0
        self.totTest = 0
        self.hilDataVec = []
        self.sequence = 0

        for i in range(numHILs):
            hData = hilData()
            self.hilDataVec.append(hData)

    def reset(self):
        for i in range(numHILs):
            self.hilDataVec[i].reset()
