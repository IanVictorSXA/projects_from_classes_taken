# This script will print roll, pitch, yaw and start collecting data (raw sensor values + roll, pitch, yaw) from IMU connected to raspberry pi after button press
# NUM_SAMPLES controls how many samples it will take after button press

import time
import smbus
import numpy as np
from gpiozero import Device, Button
from gpiozero.pins.lgpio import LGPIOFactory
from imusensor.MPU9250 import MPU9250
from imusensor.filters import kalman 

file_path = "./project2/project/data.npy"

Device.pin_factory = LGPIOFactory()
button = Button(17)
pressed = False
def press():
	global pressed
	pressed = True
	
button.when_pressed = press

address = 0x68
bus = smbus.SMBus(1)
imu = MPU9250.MPU9250(bus, address)
imu.begin()

imu.loadCalibDataFromFile("/home/ianvictor/Desktop/4201_projects/project2/project/calib.json")

sensorfusion = kalman.Kalman()

imu.myReadSensor()
imu.computeOrientation()
sensorfusion.roll = imu.roll
sensorfusion.pitch = imu.pitch
sensorfusion.yaw = imu.yaw

NUM_SAMPLES = 60_000
to_save = np.empty((NUM_SAMPLES, 12), dtype=int)
i = 0
currTime = time.time()
while True:
	imu.myReadSensor()
	imu.computeOrientation()
	newTime = time.time()
	dt = newTime - currTime
	currTime = newTime

	sensorfusion.computeAndUpdateRollPitchYaw(imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2], 
										      imu.GyroVals[0], imu.GyroVals[1], imu.GyroVals[2],
											  imu.MagVals[0], imu.MagVals[1], imu.MagVals[2], dt)
	orientation = np.array((sensorfusion.roll + 180, sensorfusion.pitch + 180, sensorfusion.yaw + 180))

	if pressed: 
		to_save[i, :] = np.concatenate((imu.RawAccelVals, imu.RawGyroVals, imu.RawMagVals, orientation.round()))
		print(i, end=" ")
		i += 1

	print("Roll:{0} Pitch:{1} Yaw:{2} ".format(*orientation))
	
	if i == NUM_SAMPLES: 
		break

	time.sleep(0.01)

np.save(file_path, to_save)
print(f"Data saved! ({i} samples)")