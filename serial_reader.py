#!/usr/bin/env python3

import queue
import threading
import serial

# import guiData
q = queue.Queue()

class SerialReader:
    def __init__(self):
        self.HIL1_Q = queue.Queue()
        self.HIL2_Q = queue.Queue()
        self.HIL1_R = serial.Serial('dev/rfcomm1' 9600)
        self.HIL2_R = serial.Serial('dev/rfcomm2' 9600)
        self.HIL1_T = threading.Thread(target=sr.read_function, args=(self.HIL1_Q, self.HIL1_R), daemon=True)
        self.HIL2_T = threading.Thread(target=sr.read_function, args=(self.HIL2_Q, self.HIL2_R), daemon=True)
        self.run()
    def read_function(self, HIL_Q, HIL_R):
        while True:
            data = HIL_R.read(size = 1)
            HIL_Q.put(data)
    def run(self):
        self.HIL1_T.start()
        self.HIL2_T.start()
        while True:
            HIL1_D = self.HIL1_Q.get()
            HIL2_D = self.HIL2_Q.get()
            self.HIL1_Q.task_done()
            self.HIL2_Q.task_done()
            q.put([HIL1_D, HIL2_D])

if __name__ == '__main__':
    sr = SerialReader()
