#!/usr/bin/env python

"""
Author: Ellen
Created: Sep. 20, 2020
Updated: Nov. 29, 2020

Classes to hold a package of data to update an entire SimWidget window
"""

from enum import Enum  # pip3 install enum

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
        self.newTestFlag = False

    def reset(self):
        self.hilCurMPH = 0
        self.hilCurDistance = 0
        self.hilCurTime = 0
        self.hilCurTest = 0
        self.status = Status.STANDBY
        self.NewTestFlag = False

    def copy(self, refHil):
        self.status = refHil.status
        self.hilCurMPH = refHil.hilCurMPH
        self.hilCurDistance = refHil.hilCurDistance
        self.hilCurTime = refHil.hilCurTime
        self.hilCurTest = refHil.hilCurTest
        self.hilLifeDistance = refHil.hilLifeDistance
        self.hilLifeTime = refHil.hilLifeTime
        self.hilLifeTest = refHil.hilLifeTest
        self.newTestFlag = refHil.newTestFlag


class simData():
    def __init__(self, seqNum=-1):
        self.totDistance = 0
        self.totTime = 0
        self.totTest = 0
        self.hilDataVec = []
        self.sequence = seqNum

        for i in range(numHILs):
            hData = hilData()
            self.hilDataVec.append(hData)

    def reset(self):
        for i in range(numHILs):
            self.hilDataVec[i].reset()

    def copy(self, refSim):
        self.totDistance = refSim.totDistance
        self.totTime = refSim.totTime
        self.totTest = refSim.totTest
        self.sequence = refSim.sequence

        for h in range(numHILs):
            self.hilDataVec[h].copy(refSim.hilDataVec[h])


class resetMsg():
    def __init__(self, resNum=-1, seqNum=-1):
        self.hil = resNum
        self.sequence = seqNum


class timerMsg():
    def __init__(self, seqNum=-1):
        self.sequence = seqNum
