# Calibrate IMU and save results. Author: niru-5 (Niranjan Reddy)
# niru-5 is the author of the imusensor package as well. I believe I got this code from the imusensor repository.
# There are very small changes (if any)

import smbus
from imusensor.MPU9250 import MPU9250

address = 0x68
bus = smbus.SMBus(1)
imu = MPU9250.MPU9250(bus, address)
imu.begin()
imu.caliberateAccelerometer()
print ("Acceleration calib successful")
imu.caliberateMagPrecise()
print ("Mag calib successful")

accelscale = imu.Accels
accelBias = imu.AccelBias
gyroBias = imu.GyroBias
mags = imu.Mags 
magBias = imu.MagBias

imu.saveCalibDataToFile("../project/calib.json")
print ("calib data saved")

print(accelscale, accelBias)
print(gyroBias)
print(mags, magBias)
