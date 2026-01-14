Final project of the IoT lab. This is a team project. Members: Ian Victor Souza Xavier dos Anjos (me), Rod Brautbar (nimrod325), Yongming Mai (MYM929) 

This project is a mix of: python (3.11), raspberry pi 5, cloud (AWS and Mosquitto, using MQTT protocol), machine learning (tensorflow, liteRT, Ollama for LLMs and agentic AI), physical computing (IMU - MPU9250, ultrasonic sensor, picamera, speaker, and LEDs), MIT app inventor for mobile app development, little bit of Linux, teamwork, and tons of research.

We did this project on a raspberry pi 5. Scripts with no authors at the top were written by me (IanVictorSXA)

**Video explaining the project: https://youtu.be/prIeIzTxbvk**. The slides in the video are included in this folder.

I forgot to mention in the video that the raspberry pi 5 sends data to both mosquitto broker and AWS. When it sends data to AWS, AWS sends them to lambda. Then, Lambda saves the data in a DynamoDB database, performs logic (controls the LED), and publishes it .



### Folders/file description: open each folder for more details and explanation on how it works and how to run it properly.
* train_tflite_model - shows how to collect raw data from IMU, save it, train a model with it, and convert it to a more lightweight version (tflite).
* project - all the files needed to run the project (except for facial recog model due to being very large)
* mpu9250.py - after installing imusensor package, replace author's mpu9250.py with the one in this repository


### Project is split in 2 parts:

* Part 1 - collect data, perform inference with tflite model, and send data to MQTT broker and AWS IoT. Control LEDs. Visualize data on phone.
* Part 2 - use ultrasonic sensor for checking for human presence, do facial recognition, control speaker, use LLM, and do agentic AI with LLM (to play music, control a different LED from part 1, and retrieve data from part one). `This part needs 2 raspberry pi 5s, but you can tweak the code to make it all work with a single one.`



### Project description:

Our project is to use a raspberry pi 5 to get raw data (in bits converted to decimal) from an IMU (electronic device which has a magnetometer, accelerometer, and gyroscope), use a lightweight neural network (a tflite model) to calculate the IMU's orientation accross all 3 dimensions (roll, pitch, yaw) and send it to cloud. The cloud will save result in a database, send it to a phone app and to another raspberry pi 5, and the cloud will control the LEDs representing each IMU. LED is on if IMU orientation is at least close to desired orientation, and off otherwise. 


<img width="1200" height="675" alt="image" src="https://github.com/user-attachments/assets/b2efa6d5-250b-419e-8e91-8720dcd4b4de" />


Then we have a LLM installed in the raspberry pi. The llm is agentic. We can chat with it like any other LLM plus we can ask it to turn on/off an LED (different from the ones used by the cloud), and to play music that is installed locally. The LLM both replies in text and through speech using the google translate API. To have access to the LLM, the user's face should be added to database. A distance sensor will check if someone is nearby and, if so, it will turn on camera on slave raspberry pi for facial recognition.

<img width="1200" height="675" alt="image" src="https://github.com/user-attachments/assets/18da472e-b52f-4ee7-8f76-111d97f5c4ed" />

