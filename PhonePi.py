import sys
import csv
from flask import Flask
from flask_sockets import Sockets
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import thread
import datetime as dt


# xRotation;
# yRotation;
# zRotation;
fig = plt.figure()
subplot = fig.add_subplot(1, 1, 1)
ax = []
ay = []
az = []
time = []

app = Flask(__name__)
sockets = Sockets(app)

@sockets.route('/accelerometer')
def echo_socket(ws):
    while True:
        global xValues
        global yValues

        message = ws.receive()
        xyz = message.split(',')
        x = float(xyz[0])
        y = float(xyz[1])
        z = float(xyz[2])
        ax.append(x)
        ay.append(y)
        az.append(z)

        time.append(dt.datetime.now().strftime('%f'))

            # if(!xRotation || !yRotation)
            # 	calculateXRotation
            # 	calculateYRotation
        # print(message)
        ws.send(message)


@sockets.route('/gyroscope')
def echo_socket(ws):
    f=open("gyroscope.txt","a")
    while True:
        # if(!zRotation) calculateZRotation()
        message = ws.receive()
        # print(message)
        ws.send(message)
        print>>f,message
    f.close()
	
# This function is called periodically from FuncAnimation
def animate(x):
    global time
    global ax
    global ay
    global az

    if len(time) == 0:
        return
     # Add x and y to lists

    # Limit x and y lists to 20 items
    ax = ax[-100:]
    ay = ay[-100:]
    az = az[-100:]
    time = time[-100:]

    # Draw x and y lists
    subplot.clear()
    subplot.plot(time, ax)
    subplot.plot(time, ay)
    subplot.plot(time, az)

    # Format plot
    subplot.set_ylim([-20,20])
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('G force over Time')
    plt.ylabel('g')

@app.route('/')
def hello():
    return 'Hello World!'

def start_socket():
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    print("start socket")
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()

def main():
    thread.start_new_thread( start_socket, () )
    ani = animation.FuncAnimation(fig, animate, fargs=([]), interval=1000)
    plt.show()



main()


