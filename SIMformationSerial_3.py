#!/usr/bin/env python3

"""
Author: Ellen, Mitch, Norm
Created: Oct. 20, 2020
Updated: Nov. 18, 2020

Main program; runs SimWidget GUI alongside threads for the data read and
	parsing unit and queued communications
"""

import time  # Time library
import queue
import threading
import sys
import csv
from datetime import timedelta, datetime
import serial  # Serial connection library - pip3 install pyserial
from timeloop import Timeloop  # pip3 install timeloop
# sudo apt-get install python3-pyqt5
from PyQt5.QtWidgets import (QWidget, QApplication)


import sim_widget

GUI_UPDATE_INTERVAL = 1  # how often the gui is updated (seconds)

simQueue = queue.Queue()
# global timerSeqNum
# timerSeqNum = 0
loop = Timeloop()

ports = ['dev/rfcomm0', 'dev/rfcomm1', 'dev/rfcomm2', 'dev/rfcomm3', 'dev/rfcomm4', 'dev/rfcomm5']

class HILReader:
    def __init__(self, port):
        self.hilQueue = queue.Queue()
        self.port = port

    def read_function(self):
        reader = serial.Serial(self.port, 9600)
        while True:
            data = reader.read(size=1)  # revisit
            self.hilQueue.put(data)

class SerialReceiver:
    def __init__(self):
        self.sim_data = sim_widget.guiData.simData()
        self.simSeqNum = 0

    def csv_reader(self):
        print("CSV_READER")
        with open('sample_data2.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            simSeqNum = 0
            for row in csv_reader:
                if line_count != 0:
                    abs_time = row[1]
                    bench = row[9]
                    speed = row[23]
                    status = row[4]
                    try:
                        resMsg = sw.resetQueue.get(False)
                        sw.resetQueue.task_done()
                        if resMsg.hil == -1:
                            self.sim_data.reset()
                        else:
                            self.sim_data.hilDataVec[resMsg.hil].reset()
                        print("RESET RECEIVED: ", resMsg.hil)
                        print("\tsequence number: ", resMsg.sequence)
                    except queue.Empty:
                        pass
                    self.find_bench(bench, abs_time, speed, status)
                    self.sim_data.sequence = simSeqNum
                    simQueue.put(self.sim_data)  # Add to queue
                    simSeqNum += 1
                line_count += 1
                time.sleep(0.01) # This needs to change

    def find_bench(self, bench, abs_time, speed, status):
        self.current_mph = float(speed)
        self.current_time = float(abs_time)/3600
        for i in range(1, sim_widget.guiData.numHILs + 1):
            bench_str = 'C{}'.format(i)
            if bench == bench_str:
                self.set_bench_vars(i - 1)
                # set status
                if status == 'F':
                    self.sim_data.hilDataVec[i - 1].status = sim_widget.guiData.Status.RUNNING
                else:
                    self.sim_data.hilDataVec[i - 1].status = sim_widget.guiData.Status.STANDBY

    def set_bench_vars(self, bench_number):
        # Get previous data fields
        prev_mph = self.sim_data.hilDataVec[bench_number].hilCurMPH
        prev_time = self.sim_data.hilDataVec[bench_number].hilCurTime
        # Set new mph
        self.sim_data.hilDataVec[bench_number].hilCurMPH = self.current_mph
        # Test 2 second delay
        if (self.current_time - self.sim_data.hilDataVec[bench_number].hilCurTime >= (2/3600)) and (self.sim_data.hilDataVec[bench_number].hilCurDistance > 0):
            print('NEW TEST FOR BENCH %f'%bench_number)
            # Reset bench values
            self.sim_data.hilDataVec[bench_number].reset()
            # Increment tests
            self.sim_data.hilDataVec[bench_number].hilCurTest += 1
            self.sim_data.hilDataVec[bench_number].hilLifeTest += 1
            self.sim_data.totTest += 1
        else:
            # Set new time
            self.sim_data.hilDataVec[bench_number].hilCurTime = self.current_time
            # Append time
            self.sim_data.hilDataVec[bench_number].hilLifeTime += (self.current_time - prev_time)
            # Calculate new distances
            distance_traveled = ((self.current_time - prev_time)*(prev_mph + self.current_mph)/2)
            self.sim_data.hilDataVec[bench_number].hilCurDistance += distance_traveled
            self.sim_data.hilDataVec[bench_number].hilLifeDistance += distance_traveled
            # Add to overall totals
            self.sim_data.totDistance += distance_traveled
            self.sim_data.totTime += (self.current_time - prev_time)

    def serial_reader(self):
        # Setup serial connections
        self.HILReaders = []
        for i in range(2):  # range(guiData.numHILs)
            self.HILReaders.append(HILReader(ports[i]))
            threading.Thread(target=self.HILReaders[i].read_function, daemon=True).start()
        # Get new messages from each connection
        while True:
            for i in range(2):
                try:
                    data = str(self.HILReaders[i].hilQueue.get(False))
                    self.HILReaders[i].hilQueue.task_done()
                    self.serial_translator(data)
                    simQueue.put(self.sim_data)
                except queue.Empty:
                    pass

    def serial_translator(self, msg):
        stream = msg.decode('utf-8').split('\r')
        print("STREAM: ", stream)
        for i in range(len(stream)):
            single_msg = stream[i].split(',')
            if len(single_msg) > 1:
                abs_time = single_msg[1]
                bench = single_msg[9]
                speed = single_msg[23]
                status = single_msg[4]
                print("message: %s" % message)
                print("bench: %s" % bench)
                self.find_bench(bench, message)

################## FOR RECEIVING DATA FROM THE QUEUE ############################

def dataReceiver():
    timerPrime = False
    while True:
        # ***REVISIT - weird stuff from this debug (next 3 lines)
        # m = simQueue.qsize()
        # if (m > 0):
        #     print("queue length (m): ", m)  # DEBUG TEST

        # print("queue length: ", simQueue.qsize()) # DEBUG TEST
        data = simQueue.get()
        msgType = "data parsing"
        if type(data) is sim_widget.guiData.timerMsg:  # data.totTime == -1:
            timerPrime = True
            msgType = "timer"
            # print("timer sequence number: ", data.sequence)  # DEBUG TEST
        elif timerPrime:
            sw.dataUpdate(data)
            timerPrime = False
            # print(msgType, "simData sequence number: ", data.sequence) # DEBUG TEST
        simQueue.task_done()


################## TIMER CALLBACK TO SEND UPDATE MESSAGE TO GUI DATA QUEUE ######################

@ loop.job(interval=timedelta(seconds=GUI_UPDATE_INTERVAL))
def timerCallback():
    # print("time: ", datetime.now().strftime("%H:%M:%S")) # DEBUG TEST
    timerMsg = sim_widget.guiData.timerMsg()
    global timerSeqNum
    try:
        timerSeqNum += 1
    except Exception:
        timerSeqNum = 0
    timerMsg = sim_widget.guiData.timerMsg(timerSeqNum)
    simQueue.put(timerMsg, False)


################## MAIN ######################

def main():

    app = QApplication(sys.argv)
    global sw
    sw = sim_widget.SIMWidget('H')
    sw.show()

    sr = SerialReceiver()

    threading.Thread(target=sr.csv_reader, daemon=True).start()
    # threading.Thread(target=sr.serialReader, daemon=True).start()

    loop.start(block=False)

    threading.Thread(target=dataReceiver, daemon=True).start()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
