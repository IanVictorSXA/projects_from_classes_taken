# collect raw data from IMU, gives it to tflite model, and sends its output to AWS IoT and mosquitto broker. Press button to set current orientation to reference orientation

# Enter "sudo systemctl start mosquitto" on the terminal first
import time
import paho.mqtt.client as mqtt
import json
import _thread
from db2 import update_row, set_up_db
from gpiozero import Button, Device
from gpiozero.pins.lgpio import LGPIOFactory
from imusensor.MPU9250 import MPU9250
from run_tflite import get_orientation 
import smbus
import numpy as np
import client_aws as aws

address = 0x68
bus = smbus.SMBus(1)
imu = MPU9250.MPU9250(bus, address)
imu.begin()

imu.loadCalibDataFromFile("/home/ianvictor/Desktop/code/4201_projects/project5/calib.json")

imu.myReadSensor()
imu.computeOrientation()

path_db = "project5/db2.json"
set_up_db(path_db)

client = aws.get_a_client("Ian")
aws.connect(client)

def on_connect2(client, userdata, flags, reason_code,properties):
    print("Connected to mosquitto MQTT broker: " + str(reason_code))

client2 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Ian", protocol=mqtt.MQTTv5)
broker = "localhost"
topic2 = "sensor/data"

client2.on_connect = on_connect2

with open("project2/project/cred.txt", "r") as creds:
    username = creds.readline().strip()
    password = creds.readline().strip()
    client2.username_pw_set(username, password)
client2.connect(broker, 1883, 60)

lock = _thread.allocate_lock()
roll, pitch, yaw, temp, ref_set = [0,0,0,0,1]
ANGLE = 10

def change_ref():
    global ref_set
    with lock:
        ref_set = 1

Device.pin_factory = LGPIOFactory()
button = Button(23)
button.when_pressed = change_ref

def update():
    global roll, pitch, yaw, temp
    while True:
        imu.myReadSensor()
        raw = np.concatenate((imu.RawAccelVals, imu.RawGyroVals, imu.RawMagVals))
        orientation = get_orientation(raw)
        with lock:
            roll, pitch, yaw = orientation
            temp = imu.Temp
        time.sleep(0.1)

def publishData():
    global ref_set
    while True:
        with lock:
            r, p, y, t = roll, pitch, yaw, temp

        print(r, p, y, t, ref_set, ANGLE)
        data = update_row(r,p,y,t,ref_set, ANGLE)
        client.publish("raspi/data", payload=json.dumps(data),
                       qos=0, retain=False)
        client2.publish(topic2, payload="{}, {}, {}".format(r,p,y))

        with lock:
            if ref_set:
                ref_set = 0

        time.sleep(1)

_thread.start_new_thread(update, ())
_thread.start_new_thread(publishData, ())

client.loop_forever()