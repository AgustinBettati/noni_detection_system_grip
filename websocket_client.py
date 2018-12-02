
from websocket import create_connection
import json

def start_connection():
    global ws
    while True:
        try:
            ws = create_connection("ws://192.168.0.4:8000")
            print "connection made"
            break
        except :
            print "reconnecting"


def send_measurements(acceleration, gyro1, gyro2, kalman):
    start_connection()
    ws.send(json.dumps([ "measurements",
                        [acceleration_to_array(acceleration),
                         acceleration_to_array(gyro1),
                         acceleration_to_array(gyro2),
                         acceleration_to_array(kalman)]]))

def send_fourier(fourier, fourier_kalman, x_axis):
    start_connection()
    ws.send(json.dumps([ "fourier",
                         [acceleration_to_array(fourier),
                          acceleration_to_array(fourier_kalman),
                          acceleration_to_array(x_axis)]]))

def acceleration_to_array(acceleration):
    return [acceleration.x, acceleration.y, acceleration.z]

print "Sent"

