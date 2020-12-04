#!/usr/bin/env python3

import queue
import threading
import serial

PORTS = ['dev/rfcomm0', 'dev/rfcomm1', 'dev/rfcomm2',
         'dev/rfcomm3', 'dev/rfcomm4', 'dev/rfcomm5']

CONNECTED_ADAPTERS = 1

class HILReader:
    def __init__(self, port):
        self.hilQueue = queue.Queue()
        self.port = port

    def read_function(self):
        reader = serial.Serial(self.port, 9600)
        while True:
            data = reader.read(size = 1)  # revisit
            self.hilQueue.put(data)

class SIMReader:
    def __init__(self):
        self.HILReaders = []
        for i in range(CONNECTED_ADAPTERS):
            self.HILReaders.append(HILReader(PORTS[i]))
        self.read_all()

    def read_all(self):
        for i in range(CONNECTED_ADAPTERS):
            threading.Thread(target=self.HILReaders[i].read_function, daemon=True).start()
        while True:
            for i in range(CONNECTED_ADAPTERS):
                try:
                    data = str(self.HILReaders[i].hilQueue.get(False))
                    self.HILReaders[i].hilQueue.task_done()
                    print('HIL %d: %s' %(i, data))
                except queue.Empty:
                    pass

if __name__ == '__main__':
    sr = SIMReader()
