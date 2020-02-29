import numpy as np
import tflite_runtime.interpreter as tflite

interpreter = tflite.Interpreter('converted_model.tflite', experimental_delegates=[tflite.load_delegate('libedgetpu.so.1')])

interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

data = [1, 1, 1]
input_data = np.float32([data])
interpreter.set_tensor(input_details[0]['index'], input_data)

interpreter.invoke()

print(interpreter.get_tensor(output_details[0]['index']).tolist()[0])
