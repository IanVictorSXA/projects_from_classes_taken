# Tools given to LLM

from gpiozero import Device, LED
from gpiozero.pins.lgpio import LGPIOFactory
import player
import db2

db_path = "db2.json"
db2.set_up_db(db_path)

# Change pin_factory to updated one
Device.pin_factory = LGPIOFactory()
color = "blue"
led = LED(22) # blue led

def get_cam0_orientation():
    """ Get current orientation of camera 0 (Roll, pitch, yaw) with its timestamp
    
    Returns:
        timestamp of data. Roll, pitch, and yaw of camera"""
    data = db2.get_data()[0]
    timestamp = data["timestamp"]
    roll, pitch, yaw = data["roll"], data["pitch"], data["yaw"]

    return "Camera 0: data timestamp : {}; Roll: {}, Pitch: {}, Yaw: {}".format(timestamp, roll, pitch, yaw)


def control_LED(command : str) -> str:
    """Turn on or off LED.

    Args:
        command: what command is being given. Commands: on, off.

    Returns:
        A string showing the new state of the LED.
    """

    # Check if command is valid
    if (command != "off") and (command != "on"):
        return "Unknown command"
    elif command == "on":
        led.on()
    else:
        led.off()

    return f"{color} LED is now {command}"

functions = {"control_LED" : control_LED, "get_cam0_orientation": get_cam0_orientation, "control_player" : player.control_player}
tools = list(functions.values())

# For testing, test LLM's behavior. Same code as in "chat_w_tools.py"
if __name__ == "__main__":
    from ollama import chat
    model = "qwen3:0.6b"

    while True:
        prompt = input(">>> ")
        messages = [{"role": "user", "content": prompt}]
        response = chat(model=model, messages=messages, tools=tools, think=True)

        messages.append(response.message)

        if response.message.tool_calls:
            call = response.message.tool_calls[0]
            print(call.function.name, call.function.arguments)
            result = functions[call.function.name](**call.function.arguments)

            messages.append({"role": "tool", "tool_name": call.function.name, "content": result})

            final_response = chat(model=model, messages=messages, tools=tools, think=False)
        else:
            final_response = response

        print(final_response.message.content)


