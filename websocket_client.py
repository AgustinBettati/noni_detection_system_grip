
from websocket import create_connection
import json

def start_connection():
    global ws
    while True:
        try:
            ws = create_connection("ws://192.168.0.4:8000")
            break
        except :
            print "reconnecting"


def send_measurements(measurement, gyro1, gyro2, kalman):
    """
    TODO FIX COMMENT. PARAMETROS SON MEASUREMENTS
    Send measurements to websocket server
    :param measurement: np.array()
    :param gyro1: np.array()
    :param gyro2: np.array()
    :param kalman: np.array()
    :return: void
    """
    start_connection()
    ws.send(json.dumps([ "measurements",
                         [measurement_to_array(measurement),
                          measurement_to_array(gyro1),
                          measurement_to_array(gyro2),
                          measurement_to_array(kalman)]]))

def send_fourier(fourier, fourier_kalman, x_axis):
    #TODO ADD COMMENT
    start_connection()
    ws.send(json.dumps([ "fourier",
                        [serialize_fourier(fourier),
                         serialize_fourier(fourier_kalman),
                          x_axis]]))

def measurement_to_array(acceleration):
    #TODO ADD COMMENT
    return [acceleration.x, acceleration.y, acceleration.z]

def serialize_fourier(fourier):
    x = ','.join(str(e) for e in fourier[0])
    y = ','.join(str(e) for e in fourier[1])
    z = ','.join(str(e) for e in fourier[2])
    return [x, y, z]

print "Sent"

