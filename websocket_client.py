
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


def send(acceleration1, acceleration2, acceleration_subtracted):
    start_connection()
    ws.send(json.dumps(
        [acceleration_to_array(acceleration1),
         acceleration_to_array(acceleration2),
         acceleration_to_array(acceleration_subtracted)]))

def acceleration_to_array(acceleration):
    return [acceleration.x, acceleration.y, acceleration.z]

print "Sent"

