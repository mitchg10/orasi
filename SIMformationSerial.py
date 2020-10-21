import time # Time library
import serial # Serial connection library
import queue
import threading
import sys
from PyQt5.QtWidgets import (QWidget, QApplication)
from time import sleep
from enum import Enum
import csv

import sim_widget

q = queue.Queue()

# def set_bench_vars(sim_data, bench_number, new_mph, new_time):
# 	print("check1")
# 	sim_data.hilDataVec[bench_number].hilCurMPH = new_mph
# 	if sim_data.hilDataVec[bench_number].hilCurTime == 0.0:
# 		sim_data.hilDataVec[bench_number].hilCurTime = new_time
# 		sim_data.hilDataVec[bench_number].hilCurMPH = new_mph
# 	else:
# 		sim_data.hilDataVec[bench_number].hilCurTime = new_time - sim_data.hilDataVec[bench_number].hilCurTime # space between the last message and the current
# 		sim_data.hilDataVec[bench_number].hilLifeTime += sim_data.hilDataVec[bench_number].hilCurTime # adding the time_space to the total_time
# 		prev_mph = sim_data.hilDataVec[bench_number].hilCurMPH # storing the previous MPH
# 		sim_data.hilDataVec[bench_number].hilCurMPH = new_mph # getting the new MPH
# 		sim_data.hilDataVec[bench_number].hilCurDistance += (sim_data.hilDataVec[bench_number].hilCurTime*(prev_mph+new_mph)/2) # using trap rule to append to the total distanc

def set_bench_vars(sim_data, bench_number, new_mph, new_time):
	# Get previous data fields
	prev_mph = sim_data.hilDataVec[bench_number].hilCurMPH
	prev_time = sim_data.hilDataVec[bench_number].hilCurTime
	# Set new mph and times
	sim_data.hilDataVec[bench_number].hilCurMPH = new_mph
	sim_data.hilDataVec[bench_number].hilCurTime = new_time
	# Set new distances and append time
	sim_data.hilDataVec[bench_number].hilLifeTime += (new_time - prev_time)
	sim_data.hilDataVec[bench_number].hilCurDistance += ((new_time - prev_time)*(prev_mph + new_mph)/2)
	sim_data.hilDataVec[bench_number].hilLifeDistance += sim_data.hilDataVec[bench_number].hilCurDistance
	# Add to overall totals
	sim_data.totDistance += sim_data.hilDataVec[bench_number].hilCurDistance
	sim_data.totTime += (new_time - prev_time)

# This updates the respective bench based off the bench field
def find_bench(bench, abs_time, speed, sim_data, reset):
	print("check2")
	
	if reset:
		for i in range(1, sim_widget.guiData.numHILs + 1):
			sim_data.hilDataVec[i] = sim_widget.guiData.hilData()

	current_mph = float(speed)
	# current_mph = int(message, 16)/128 # Get the current MPH (change 16 to 0 if 0x is included in message string)
	current_time = float(abs_time) # Get the current time
	# Now, update based off the bench we passed in
	for i in range(1, sim_widget.guiData.numHILs + 1):
		bench_str = 'C{}'.format(i)
		if bench == bench_str:
			set_bench_vars(sim_data, i - 1, current_mph, current_time)

###################### FOR SENDING DATA TO THE QUEUE FROM A CSV FILE #################################

def csv_reader():
	print("check3")
	# Create a simData
	sim_data = sim_widget.guiData.simData()

	with open('sample_data.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			if line_count != 0:
				abs_time = row[1]
				bench = row[9]
				speed = row[23]
				reset = False
				try:
					sw.resetQueue.get(False)
					sw.resetQueue.task_done
					reset = True
					print("reset")
				except queue.Empty:
					pass
				find_bench(bench, abs_time, speed, sim_data, reset)
				q.put(sim_data) # Add to queue
			line_count += 1
			sleep(1)
			print("check csv" , row[0])

###################### FOR SENDING DATA TO THE QUEUE FROM A SERIAL CONNECTION #################################

def serialReader():

	# Create a simData
	sim_data = sim_widget.guiData.simData()

	# Now, we open the serial connection to the adapters
	ser = serial.Serial(port='/dev/ttyUSB0',
						baudrate=9600,
						parity=serial.PARITY_NONE,
						stopbits=serial.STOPBITS_ONE,
						bytesize=serial.EIGHTBITS,
						timeout=1)

	readText = ser.readline() # and begin by reading one line from the connection

	# From now on
	while True:
		stream = readText.decode('utf-8').split('\r') # split the serial messages by bench (they are separated by the '\r' character)
		print("stream: " , stream)
		for i in range(len(stream)): # for each message we've received since the last refresh
			single_msg = stream[i].split(';') # split up the message which looks like this [HIL;DATA_FIELD]
			if len(single_msg) > 1: # Now, if the length of the message is > 1, that means there's data in there we should look at
				bench = single_msg[0] # Find the bench number
				message = single_msg[1] # Find the data field
				print("message: %s" %message)
				print("bench: %s" %bench)
				find_bench(bench, message, sim_data) # Now, update the benches using the update_benches() function above
				q.put(sim_data) # Add to queue
		readText = ser.readline() # Once we've updated, read in the next line

	ser.close() # close the connection when we are completed

################## FOR RECEIVING DATA FROM THE QUEUE ############################

def dataReceiver():
	while True:
		data = q.get()
		sw.dataUpdate(data)
		q.task_done()

################## MAIN ######################

def main():
	app = QApplication(sys.argv)
	global sw
	sw = sim_widget.SIMWidget('H')
	sw.show()

	threading.Thread(target=csv_reader, daemon=True).start()
	# threading.Thread(target=serialReader, daemon=True).start()

	threading.Thread(target=dataReceiver, daemon=True).start()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
