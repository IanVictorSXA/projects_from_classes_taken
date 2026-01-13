# Load tfilte model and perform inference with get_orientation

from ai_edge_litert.interpreter import Interpreter
import numpy as np

# input name = input_layer, output name = output_0
interpreter = Interpreter("project2/model.tflite")
signature = interpreter.get_signature_runner()



def _rad_to_degree(rad : float):
    return np.degrees(rad)

def _get_degrees_with_atan2(cos : float, sin : float):
    return _rad_to_degree(np.arctan2(sin, cos))

def _get_output(raw_values: np.array):
    output = signature(input_layer=raw_values.astype(np.float32))
    return output["output_0"][0]

def get_orientation(raw_values : np.array):
    """ raw_values: 9 length array that contains 3 values for accel, gyro, and mag, in this order.
        rounds orientation angles to nearest integer"""
    output_cos_sin = _get_output(raw_values)
    orientation = np.zeros(shape=(3,)) # Roll, Pitch, Yaw

    for i in range(3):
        orientation[i] = _get_degrees_with_atan2(output_cos_sin[i], output_cos_sin[i + 3]).round()

    return orientation

if __name__ == "__main__":
    print(get_orientation(np.array([30,30,30,30,30,30,30,30,30])))