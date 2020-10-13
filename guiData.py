from enum import Enum

import sim_widget

class Status(Enum):
    RUNNING = 0
    STANDBY = 1
    FAILED = 2

class hilData():
    def __init__(self):
        self.status = Status.STANDBY
        self.hilCurDistance = 0
        self.hilCurTime = 0
        self.hilLifeDistance = 0
        self.hilLifeTime = 0
        #self.test = 0

class simData():
    def __init__(self):
        self.test = 0   #ignore test
        self.totDistance = 0
        self.totTime = 0
        self.hilDataVec = []

        #dw about numHILs, assume it's set to 6 if you need
        for i in range (1, sim_widget.numHILs + 1): 
            hData = hilData()
            self.hilDataVec.append(hData)