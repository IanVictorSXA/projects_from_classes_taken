In this folder, I show how to run this project. 

`Take a look at each python file as it may have some folder path or pin number that may not work for you`

`The model used for facial recognition is too big to include in the repository. We have it in google drive, but it may be deleted in the future: https://drive.google.com/file/d/1a-7sW_ps4DitTZmxFJFuazlZeI5DYj13/view

### Part 0: set up AWS IoT, Lambda, and DynamoDB. Set up MIT app inventor app. Download Ollama and LLM. Install mosquitto.

Mosquitto:
1. set up mosquitto: https://randomnerdtutorials.com/how-to-install-mosquitto-broker-on-raspberry-pi/
2. test if it is working: https://randomnerdtutorials.com/testing-mosquitto-broker-and-client-on-raspbbery-pi/

`We used mosquitto too and not just AWS because this project is a combination of previous ones done throughout the course.`

AWS:
1. Set up AWS IoT core: https://www.youtube.com/watch?v=XcqVgGXcp4M
2. Set up AWS DynamoDB and lambda: https://www.youtube.com/watch?v=0RcVwTKSbSA
3. Replace lambda_function.py in lambda with the file (same name) provided here. This code creates one row in the database for each IMU. We created simples IDs to differentiate each IMU

Phone app:
1. Go to https://ai2.appinventor.mit.edu/ and sign in (or create account)
2. Load the file provided here with name "Orientation_Checker.aia" by clicking "import project (.aia) from my computer" ADD PICTURE HERE
3. Click UrsPahoMqttClient1 and a small tab (named UrsPahoMqttClient1) should show on the right ADD PICTURE HERE
4. Scroll all the way down and you will see "Username" and "Userpassword".
5. Fill these fields.
6. Download "MIT AI2 companion" on your phone (on playstore)
7. Build app and scan QR code with MIT companion
8. Download app

`This app only works if the mosquitto broker and the phone are in the same network and you have to enter the mosquitto broker's IP address every time you open the app.`

set up LLM:

1. Install ollama:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
2. Download LLM (we used qwen3:0.6b):
```bash
ollama pull qwen3:0.6b
```

### Part 1: collect data, perform inference, send data to AWS, control LEDs

1. Run "main1.py" - This collects, performs inference and send result to AWS and mosquitto. The IMU must be connected to the raspberry pi and it should have a tflite model.
2. Run "main1_control_led.py" - This receives commands from AWS to turn on/off the LED. You just need LEDs (one for each IMU and adjust code as needed) to run this. In the video, we had this code running on 2 raspberry pi's.

### Part 2: LLM with tools (for agentic AI) and face recognition. (Needs 2 raspberry pi 5s)

One raspberry pi (master) will have the LED, speaker, and distance sensor (ultrasonic sensor). A second raspberry pi (slave) will have a camera connected to it.

Slave only needs 3 files: Facial_recognition.py (for testing), Facial_recognition_onnx_slave_device.py, and facial recognition model

1. Add a new face. On slave device, run Facial_recogntion_onnx_slave_device.py. On master, run save_new_person.py. On slave, enter your anme and face camera to register. The camera will take 30 samples.
2. Run project. On slave device, run Facial_recogntion_onnx_slave_device.py. On master, run main2_chat_w_tools.
3. Approach distance sensor and wait for speaker to speak. Face camera for facial recognition. The camera will take 30 samples.
4. If you are in the database, the raspberry pi will say "welcome, your name" and you are granted access to the LLM. Else, raspberry pi says "access denied"
5. You can chat with it normally (and it will reply in text and speak) and you can ask it to do actions (that are implemented in tools.py). The actions implemented are: play song (must be downloaded on raspberry pi and you can play, pause, change volume, stop), control LED (on/off), retrieve data from database (which is stored locally using tinyDB).

`You have to say something like "get orientation of camera 0" to get IMU's orientation because our original idea was to use the IMU on cameras.`

Files description:
* Facial_recognition.py - to test if slave device works properly. This script works without use of AWS or the master device.
* Facial_recognition_onnx_slave_device.py - to use on the slave device when running the project.
* Orientation_Checker.aia - File to build the phone app. Import this on MIT app inventor website.
* access_manager.py - script that handles distance sensor and speaks "access denied" or "welcome, name" depending on message received from slave device
* calib.json - calibrations of IMU. We only use this file to get temperature. We do not use this for calibrating gyroscope, magnetometer, or accelerometer.
* client_aws.py - script for creating a client object to use AWS
* db2.json - local database that is updated or created when running main1.py (necessary for retrieving data using LLM)
* db2.py - script for creating and updating local database
* main1.py - main script for sending data to AWS and doing inference
* main1_control_led.py - main script for controlling the LEDs (1 LED for each IMU). Adjust it as necessary if you have more or less IMUs.
* main2_chat_w_tools.py - main script for using LLM with tools
* model.tflite - model used to compute orientation of IMU from raw data
* player.py - LLM's tool for playing music
* run_tflite.py - script for doing inference with tflite model
* save_new_person.py - script for adding new face to database. Master device should run this.
* speak.py - script for making the raspberry pi speak.
* tools.py - script with all tools provided to the LLM. Add or remove as needed. It is important to comment all the functions (tools) as the LLM use this info to determine if it should call the tool or not.

