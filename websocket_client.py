
from websocket import create_connection
import json

ip = "192.168.0.4"

def set_ip(new_ip):
    """
    Set the ip of the server.
    :param new_ip: string
    :return: void
    """
    global ip
    ip = new_ip

def start_connection():
    """
    Creates a connection with the server for single use, then disconnect.
    :return: void
    """
    global ws
    while True:
        try:
            ws = create_connection("ws://" + ip + ":8000")
            break
        except :
            print "not connected to the server"
            break


def send_measurements(measurement, gyro1, gyro2, kalman):
    """
    Send measurements to websocket server
    :param measurement: Measurement
    :param gyro1: Measurement
    :param gyro2: Measurement
    :param kalman: Measurement
    :return: void
    """
    start_connection()
    ws.send(json.dumps([ "measurements",
                         [measurement_to_array(measurement),
                          measurement_to_array(gyro1),
                          measurement_to_array(gyro2),
                          measurement_to_array(kalman)]]))

def send_fourier(fourier, fourier_kalman, x_axis):
    """
    Send fourier, fourier with kalman and the x axis for both of them to websocket server.
    :param fourier: python list
    :param fourier_kalman: python list
    :param x_axis: python list
    :return: void
    """
    start_connection()
    ws.send(json.dumps([ "fourier",
                        [serialize_fourier(fourier),
                         serialize_fourier(fourier_kalman),
                          x_axis]]))

def measurement_to_array(measurement):
    """
    Converts a measurement to an array
    :param measurement: Measurement
    :return: python list
        The python list has the following format:
        [0] = measurement.x
        [1] = measurement.y
        [3] = measurement.z
    """
    return [measurement.x, measurement.y, measurement.z]

def serialize_fourier(fourier):
    """
    Transform the values of fourier to string
    :param fourier: [[Complex]]
    :return: [[String]]
    """
    x = ','.join(str(e) for e in fourier[0])
    y = ','.join(str(e) for e in fourier[1])
    z = ','.join(str(e) for e in fourier[2])
    return [x, y, z]

print "Sent"

