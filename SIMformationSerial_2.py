#!/usr/bin/env python3

"""
Author: Ellen, Mitch, Norm
Created: Oct. 20, 2020
Updated: Nov. 8, 2020

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


class SerialReceiver:
    def __init__(self):
        self.sim_data = sim_widget.guiData.simData()
        self.simSeqNum = 0

    def csv_reader(self):
        print("CSV_READER")
        with open('sample_data.csv') as csv_file:
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
                time.sleep(0.01)

    def find_bench(self, bench, abs_time, speed, status):
        # print("FINDING BENCH")

        # = int(message, 16)/128 # Get the current MPH (change 16 to 0 if 0x is included in message string)
        self.current_mph = float(speed)
        self.current_time = float(abs_time)
        for i in range(1, sim_widget.guiData.numHILs + 1):
            bench_str = 'C{}'.format(i)
            if bench == bench_str:
                self.set_bench_vars(i - 1)
                # set status
                if status == 'F':
                    self.sim_data.hilDataVec[i -
                                             1].status = sim_widget.guiData.Status.RUNNING
                else:
                    self.sim_data.hilDataVec[i -
                                             1].status = sim_widget.guiData.Status.STANDBY

    def set_bench_vars(self, bench_number):
        # Get previous data fields
        prev_mph = self.sim_data.hilDataVec[bench_number].hilCurMPH
        prev_time = self.sim_data.hilDataVec[bench_number].hilCurTime
        # Set new mph and times
        self.sim_data.hilDataVec[bench_number].hilCurMPH = self.current_mph
        self.sim_data.hilDataVec[bench_number].hilCurTime = self.current_time
        # Set new distances and append time
        self.sim_data.hilDataVec[bench_number].hilLifeTime += (
            self.current_time - prev_time)
        self.sim_data.hilDataVec[bench_number].hilCurDistance += (
            (self.current_time - prev_time)*(prev_mph + self.current_mph)/2)
        self.sim_data.hilDataVec[bench_number].hilLifeDistance += self.sim_data.hilDataVec[bench_number].hilCurDistance
        # Add to overall totals
        self.sim_data.totDistance += self.sim_data.hilDataVec[bench_number].hilCurDistance
        self.sim_data.totTime += (self.current_time - prev_time)

    def serial_reader(self):

        # Now, we open the serial connection to the adapters
        ser = serial.Serial(port='/dev/ttyUSB0',
                            baudrate=9600,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS,
                            timeout=1)

        readText = ser.readline()  # and begin by reading one line from the connection

        while True:
            # split the serial messages by bench (they are separated by the '\r' character)
            stream = readText.decode('utf-8').split('\r')
            print("STREAM: ", stream)
            # for each message we've received since the last refresh
            for i in range(len(stream)):
                # split up the message which looks like this [HIL;DATA_FIELD]
                single_msg = stream[i].split(';')
                # Now, if the length of the message is > 1, that means there's data in there we should look at
                if len(single_msg) > 1:
                    bench = single_msg[0]  # Find the bench number
                    # need a for loop to read all possible data fields
                    message = single_msg[1]  # Find the data field
                    print("message: %s" % message)
                    print("bench: %s" % bench)
                    try:
                        resMsg = sw.resetQueue.get(False)
                        sw.resetQueue.task_done()
                        if resMsg.hil == -1:
                            self.sim_data.reset()
                        else:
                            self.sim_data.hilDataVec[resMsg.hil].reset()
                        print("RESET RECEIVED: ", resMsg.hil)
                    except queue.Empty:
                        pass
                    # no using find_bench funcio right, should put in all valueS
                    # Now, update the benches using the update_benches() function above
                    self.find_bench(bench, message)
                    simQueue.put(self.sim_data)  # Add to queue
            readText = ser.readline()  # Once we've updated, read in the next line

        # should put in a try-except or finally block for when the program ends (maybe just except keyboard interrupt or sy failure)

        ser.close()  # close the connection when we are completed

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
