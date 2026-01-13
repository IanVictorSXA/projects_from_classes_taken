# Control led based on the data received from AWS. If key "led" of data received is 1, turn on LED, else turn it off.

import paho.mqtt.client as mqtt
import ssl
import json
from gpiozero import LED, Device
from gpiozero.pins.lgpio import LGPIOFactory 

Device.pin_factory = LGPIOFactory()
led0 = LED(17)
led1 = LED(22)

def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to AWS IoT:" + str(reason_code))
    client.subscribe("raspi/led", qos=1)

def get_data(client, userdata, msg):
    print(f"Message received on {msg.topic}: {msg.payload.decode()}")
    msg = json.loads(msg.payload.decode())

    if msg["id"] == 0:
        if msg["led"]: 
            led0.on()
        else:
            led0.off()
    elif msg["id"] == 1:
        if msg["led"]:
            led1.on()
        else:
            led1.off()

ca = "./certs/rootCA.pem"
certfile ="./certs/device.pem.crt"
keyfile = "./certs/private.pem.key"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.message_callback_add("raspi/led", get_data)
client.tls_set(ca_certs=ca, certfile=certfile, keyfile=keyfile,
                tls_version=ssl.PROTOCOL_SSLv23)
client.tls_insecure_set(True)
client.connect("a3ot19o41mukgz-ats.iot.us-east-1.amazonaws.com", 8883, 60)

client.loop_forever()