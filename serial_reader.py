#!/usr/bin/env python3

import queue
import threading
import serial

# import guiData
q = queue.Queue()

class DOESNTMATTERCLASS:
    def __init__(self):
        self.queue_arr = []
        for i in range(1, guiData.numHILs + 1):
            queue_arr.append(queue.Queue())
            threading.Thread(target=self.read_function, args=(i), daemon=True).start()
        self.run()
    def read_function(self, hil_index):
        reader = serial.Serial('dev/rfcomm' + (hil_index + 1), 9600) # THIS IS THE SETUP SERIAL READER LINE
        while True:
            data = reader.read(size = 1) # THIS IS THE BLOCKING READ
            self.reader_queue[hil_index].put(data)
    def run(self):
        data = []
        while True:
            for i in range(1, guiData.numHILs + 1):
                data.append(self.queue_arr[i].get())
                self.queue_arr[i].task_done()
        q.put(data)

if __name__ == '__main__':
    sr = SerialReader()
