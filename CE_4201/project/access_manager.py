# Controls access to LLM, it uses a distance sensor to keep checking for a presence nearby
# If there is someone, program says "face camera" and sends a message via AWS to another computer (raspberry pi) with a camera
# this slave commputer performs face recognition. If person is in the database, it gives access. Otherwise, main pc says "access denied"

from gpiozero import Device, DistanceSensor
from gpiozero.pins.lgpio import LGPIOFactory 
from time import sleep
from speak import speak
import client_aws as aws

Device.pin_factory = LGPIOFactory()
sensor = DistanceSensor(echo=24, trigger=25, max_distance=4)

waiting = 0
name = ""
client = aws.get_a_client("main")

def on_message(client, userdata, msg):
    global waiting
    # print(msg.payload.decode())
    if waiting:
        waiting = 0
        global name
        name = msg.payload.decode().replace(" ", "")
        # print("Received")


client.on_message = on_message
aws.connect(client)
client.subscribe("raspi/face_recog/send_from_slave")

def send_msg():
    client.publish("raspi/face_recog/send_from_master", "recognition")

def someone_here(distance=0.5):
    if sensor.distance <= distance:
        return 1
    return 0

def denied():
    while someone_here():
        sleep(2)

client.loop_start()

def detect_person(volume):
    global waiting
    while True:
        if someone_here():
            speak("face_camera", volume)
            print("I see you with my ears")
            waiting = 1
            send_msg()
            while waiting == 1:
                sleep(0.5)
            speak(name, volume)
            if name != "Unknown":
                sensor.close()
                break
            else:
                denied()
        else:
            print("don't see anything")
        sleep(0.5)