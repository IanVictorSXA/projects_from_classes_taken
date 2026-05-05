# script for connecting to AWS

from time import sleep
import paho.mqtt.client as mqtt
import ssl

with open("hostname.txt", "r") as file:
    hostname = file.readline().strip()

ca = "certs/rootCA.pem"
certfile ="certs/device.pem.crt"
keyfile = "certs/private.pem.key"

def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to AWS IoT:", reason_code)

def get_a_client(id=""):
    client = mqtt.Client(client_id=id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
    client.tls_set(ca_certs=ca, certfile=certfile, keyfile=keyfile, tls_version=ssl.PROTOCOL_SSLv23)
    client.tls_insecure_set(True)
    client.on_connect = on_connect

    return client

def connect(client):
    client.connect(hostname, 8883)
    sleep(1)