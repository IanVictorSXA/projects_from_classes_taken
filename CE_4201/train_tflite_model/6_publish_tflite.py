# collect raw data from IMU, gives it to tflite model, and sends its output to mosquitto broker (which is localhost). Press button to set current orientation to reference orientation
# Used for testing

# Enter "sudo systemctl start mosquitto" on the terminal first
import time
import paho.mqtt.client as mqtt
import smbus
import numpy as np
from imusensor.MPU9250 import MPU9250
from run_tflite import get_orientation

address = 0x68
bus = smbus.SMBus(1)
imu = MPU9250.MPU9250(bus, address)
imu.begin()

imu.loadCalibDataFromFile("../project/calib.json")

imu.myReadSensor()
imu.computeOrientation()
currTime = time.time()
broker = "localhost"
topic = "sensor/data"

def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to mqtt broker:", reason_code)

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect

with open("cred.txt", "r") as creds:
    username = creds.readline().strip()
    password = creds.readline().strip()
    client.username_pw_set(username, password)
client.connect(broker, 1883, 60)

while True:
    imu.myReadSensor()
    newTime = time.time()
    dt = newTime - currTime
    currTime = newTime
    raw = np.concatenate((imu.RawAccelVals, imu.RawGyroVals, imu.RawMagVals))
    orientation = get_orientation(raw)

    print("raw accel:{0} raw gyro:{1} raw mag:{2} ".format(imu.RawAccelVals, imu.RawGyroVals, imu.RawMagVals), end=" ")
    payload = "{}, {}, {}".format(*orientation)
    client.publish(topic, payload)
    print("Sent:", payload)
    time.sleep(0.1)