import boto3
import json


def lambda_handler(event, context):
    iot_client = boto3.client("iot-data", region_name="us-east-1")
    client = boto3.client("dynamodb")
    response = client.get_item(TableName="pi5_4201_A1", Key={"id": {"N": str(event["id"])}})
    if "Item" not in response:
        response = client.put_item(
            TableName="pi5_4201_A1",
            Item={
                "id": {"N": str(event["id"])},
                "led": {"N": "1"},
                "diff_roll": {"N": "0"},
                "diff_pitch": {"N": "0"},
                "diff_yaw": {"N": "0"},
                "ref_roll": {"N": str(event["roll"])},
                "ref_pitch": {"N": str(event["pitch"])},
                "ref_yaw": {"N": str(event["yaw"])},
                "temperature": {"N": str(event["temperature"])},
                "timestamp": {"S" : event["timestamp"]}}
        )
        iot_client.publish(topic="raspi/led", qos=1, payload=json.dumps({"id": event["id"], "led": 1, "timestamp": event["timestamp"]}))
    elif event["set_ref"]:
        response = client.update_item(
            TableName="pi5_4201_A1",
            Key={"id": {"N": str(event["id"])}},
            AttributeUpdates={
                "led": {"Value": {"N": "1"}},
                "diff_roll": {"Value": {"N": "0"}},
                "diff_pitch": {"Value": {"N": "0"}},
                "diff_yaw": {"Value": {"N": "0"}},
                "ref_roll": {"Value": {"N": str(event["roll"])}},
                "ref_pitch": {"Value": {"N": str(event["pitch"])}},
                "ref_yaw": {"Value": {"N": str(event["yaw"])}},
                "temperature": {"Value": {"N": str(event["temperature"])}},
                "timestamp": {"Value": {"S" : event["timestamp"]}}}
        )
        iot_client.publish(topic="raspi/led", qos=1, payload=json.dumps({"id": event["id"], "led": 1, "timestamp": event["timestamp"]}))
    else:
        diff_roll = abs(event["roll"] - float(response["Item"]["ref_roll"]["N"]))
        diff_pitch = abs(event["pitch"] - float(response["Item"]["ref_pitch"]["N"]))
        diff_yaw = abs(event["yaw"] - float(response["Item"]["ref_yaw"]["N"]))
        angle = event["angle"]
        global led
        led = "1"
        if (diff_roll > angle) or (diff_pitch > angle) or (diff_yaw > angle):
            led = "0"

        if response["Item"]["led"]["N"] != led:
            iot_client.publish(topic="raspi/led", qos=1, 
            payload=json.dumps({"id": event["id"], "led": int(led), "timestamp": event["timestamp"]}))
        
        response = client.update_item(
            TableName="pi5_4201_A1",
            Key={"id": {"N": str(event["id"])}},
            AttributeUpdates={
                "led": {"Value": {"N": led}},
                "diff_roll": {"Value": {"N": str(diff_roll)}},
                "diff_pitch": {"Value": {"N": str(diff_pitch)}},
                "diff_yaw": {"Value": {"N": str(diff_yaw)}},
                "temperature": {"Value": {"N": str(event["temperature"])}},
                "timestamp": {"Value": {"S" : event["timestamp"]}}
            }
        )
    return 0
