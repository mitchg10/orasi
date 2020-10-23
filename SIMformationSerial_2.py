import time # Time library
import serial # Serial connection library
import queue
import threading
import sys
import time
from timeloop import Timeloop # pip3 install timeloop
from datetime import timedelta
from PyQt5.QtWidgets import (QWidget, QApplication)
from enum import Enum
import csv

import sim_widget

GUI_UPDATE_INTERVAL = 1 # how often the gui is updated (seconds)

q = queue.Queue()
loop = Timeloop()

class SerialReceiver:
	def __init__(self):
		self.sim_data = sim_widget.guiData.simData()

	def csv_reader(self):
		print("CSV_READER")
		with open('sample_data.csv') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			line_count = 0
			for row in csv_reader:
				if line_count != 0:
					abs_time = row[1]
					bench = row[9]
					speed = row[23]
					status = row[4]
					try:
						sw.resetQueue.get(False)
						sw.resetQueue.task_done
						self.sim_data.reset()
						print("RESET RECEIVED")
					except queue.Empty:
						pass
					self.find_bench(bench, abs_time, speed, status)
					q.put(self.sim_data) # Add to queue
				line_count += 1
				time.sleep(0.01)

	def find_bench(self, bench, abs_time, speed, status):
		print("FINDING BENCH")

		self.current_mph = float(speed) # = int(message, 16)/128 # Get the current MPH (change 16 to 0 if 0x is included in message string)
		self.current_time = float(abs_time)
		for i in range(1, sim_widget.guiData.numHILs + 1):
			bench_str = 'C{}'.format(i)
			if bench == bench_str:
				self.set_bench_vars(i - 1)
				# set status
				if status == 'F':
					self.sim_data.hilDataVec[i-1].status = sim_widget.guiData.Status.RUNNING
				else:
					self.sim_data.hilDataVec[i-1].status = sim_widget.guiData.Status.STANDBY

	def set_bench_vars(self, bench_number):
		# Get previous data fields
		prev_mph = self.sim_data.hilDataVec[bench_number].hilCurMPH
		prev_time = self.sim_data.hilDataVec[bench_number].hilCurTime
		# Set new mph and times
		self.sim_data.hilDataVec[bench_number].hilCurMPH = self.current_mph
		self.sim_data.hilDataVec[bench_number].hilCurTime = self.current_time
		# Set new distances and append time
		self.sim_data.hilDataVec[bench_number].hilLifeTime += (self.current_time - prev_time)
		self.sim_data.hilDataVec[bench_number].hilCurDistance += ((self.current_time - prev_time)*(prev_mph + self.current_mph)/2)
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

		readText = ser.readline() # and begin by reading one line from the connection

		while True:
			stream = readText.decode('utf-8').split('\r') # split the serial messages by bench (they are separated by the '\r' character)
			print("STREAM: " , stream)
			for i in range(len(stream)): # for each message we've received since the last refresh
				single_msg = stream[i].split(';') # split up the message which looks like this [HIL;DATA_FIELD]
				if len(single_msg) > 1: # Now, if the length of the message is > 1, that means there's data in there we should look at
					bench = single_msg[0] # Find the bench number
					message = single_msg[1] # Find the data field
					print("message: %s" %message)
					print("bench: %s" %bench)
					self.find_bench(bench, message) # Now, update the benches using the update_benches() function above
					q.put(self.sim_data) # Add to queue
			readText = ser.readline() # Once we've updated, read in the next line

		ser.close() # close the connection when we are completed

################## FOR RECEIVING DATA FROM THE QUEUE ############################

def dataReceiver():
	timerPrime = False
	while True:
		print("queue length: " , q.qsize())
		data = q.get()
		if data.totTime == -1:
			timerPrime = True
		elif timerPrime:
			sw.dataUpdate(data)
			timerPrime = False
		q.task_done()


################## TIMER CALLBACK TO SEND UPDATE MESSAGE TO GUI DATA QUEUE ######################

@loop.job(interval=timedelta(seconds=GUI_UPDATE_INTERVAL))
def timerCallback():
	timerMsg = sim_widget.guiData.simData()
	timerMsg.totTime = -1 # signify a timer message
	q.put(timerMsg, False)

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
