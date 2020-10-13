import queue
import threading
import random
import sys
from PyQt5.QtWidgets import (QWidget, QApplication)
from time import sleep
from enum import Enum

import sim_widget


q = queue.Queue()
random.seed()

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

        for i in range (1, sim_widget.numHILs + 1):
            hData = hilData()
            self.hilDataVec.append(hData)

def sensorRead():
    count = 0
    while True:
        count = count + 1
        sleep(1/60)
        data = random.random()
        q.put(data)
        #print(f'Working on {count}: {data}')
        #print(f'Finished {data}')
        #q.task_done()

def dataSend():
    countGet = 0
    while 1:
        sleep(1)
        countGet = countGet + 1
        global simData
        data = simData()
        getData = q.get()
        data.test = getData
        sw.dataUpdate(data)
        print(f'data get {countGet}: {getData}')
        q.task_done()


threading.Thread(target=sensorRead, daemon=True).start()
countGet = 0
#data = guiData()
app = QApplication(sys.argv)
q = queue.Queue()
sw = sim_widget.SIMWidget('H')
sw.show()
threading.Thread(target=dataSend, daemon=True).start()
sys.exit(app.exec_())
