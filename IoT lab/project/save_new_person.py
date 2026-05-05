#  Add new person by creating a file with the person's name. File is a sound file saying "welcome, name"

from gtts import gTTS
import client_aws as aws

topic = "raspi/face_recog/send_from_slave"

file_path = "./audios/" # .mp3

def on_message(client, userdata, msg):
    print(msg.payload.decode())
    # print(client)
    name = msg.payload.decode()
    tts = gTTS("Welcome, " + name)
    tts.save(file_path  + name.replace(" ", "") + ".mp3")
    print(f"Saved welcome for {name}")
    client.disconnect()

client = aws.get_a_client("get_id")
client.on_message = on_message
aws.connect(client)
client.subscribe(topic)
client.publish("raspi/face_recog/send_from_master", "register")

# print(client)
client.loop_forever()
