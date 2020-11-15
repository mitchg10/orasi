#!/usr/bin/env python3

import queue
import threading
import serial

import guiData
# q = queue.Queue()
ports = ['dev/rfcomm0', 'dev/rfcomm1', 'dev/rfcomm2',
         'dev/rfcomm3', 'dev/rfcomm4', 'dev/rfcomm5']


class HILReader:
    def __init__(self, port):
        self.hilQueue = queue.Queue()
        self.port = port

    def read_function(self):
        reader = serial.Serial(self.port, 9600)
        while True:
            data = reader.read(size=1)  # revisit
            self.hilQueue.put(data)


class SIMReader:
    def __init__(self):
        self.simQueue = queue.Queue()
        self.sim_data = guiData.simData()
        self.HILReaders = []
        for i in range(2):  # range(guiData.numHILs)
            self.HILReaders.append(HILReader(ports[i]))

    def read_all(self):
        for i in range(2):
            threading.Thread(
                target=self.HILReaders[i].run, daemon=True).start()
        while True:
            for i in range(1, guiData.numHILs + 1):
                try:
                    self.HILReaders[i].hilQueue.get(False)
                    self.HILReaders[i].hilQueue.task_done()
                    # MATH?
                except queue.Empty:
                    pass
            # put parsed infor in sim_data
            simQueue.put(sim_data)


if __name__ == '__main__':
    sr = SIMReader()
