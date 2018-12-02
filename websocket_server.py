from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import thread

fig = plt.figure()
"""Figure to plot fourier"""
subplot = fig.add_subplot(1, 1, 1)
"""Subplot where fourier will be plotted"""

fig2 = plt.figure()
"""Figure to plot accelerations"""
gs = gridspec.GridSpec(3, 2)
subplot2 = fig2.add_subplot(gs[0, :])
"""Subplot where the accelerations of the first sensor will be plotted"""
subplot3 = fig2.add_subplot(gs[1, 0])
subplot4 = fig2.add_subplot(gs[1, 1])
"""Subplot where the accelerations of the second sensor will be plotted"""
subplot5 = fig2.add_subplot(gs[2, :])
"""Subplot where the rotated accelerations of the two sensors will be plotted"""

interval = 0.1
"""Interval between two accelerations in seconds"""

fourier_values = np.empty(0)
"""Values for plotting fourier"""
fourier_x_axis = []
"""X axis values for plotting fourier"""

acceleration_values = [[0], [0], [0]]
"""Values for plotting raw accelerations"""

gyro_values1 = [[0], [0], [0]]
gyro_values2 = [[0], [0], [0]]
"""Values for plotting raw acceleration"""

kalman_values = [[0], [0], [0]]
"""Values for plotting subtracted accelerations"""


data_quantity = 500


x_axis = np.linspace(1, data_quantity, data_quantity)


class SimpleEcho(WebSocket):

    def handleMessage(self):
        global acceleration_values, gyro_values1, kalman_values, fourier_values, gyro_values2

        # echo message back to client
        # self.sendMessage(self.data)
        result = json.loads(self.data)
        acceleration_values = append_acceleration(acceleration_values, result[0])
        gyro_values1 = append_acceleration(gyro_values1, result[1])
        gyro_values2 = append_acceleration(gyro_values2, result[2])
        kalman_values = append_acceleration(kalman_values, result[3])



def plot_fourier(unused_param):
    """
    Plot fourier of segment of data.

    :param unused_param:
        parameter that is not used, needed in order to comply with matplotlib.animation interface
    :return:
    """

    global fourier_values, fourier_x_axis
    """The values after applying fourier transform"""

    if len(fourier_values) == 0:
        return

    n = fourier_values[0].size
    """Number of sample points"""

    subplot.clear()
    subplot.plot(fourier_x_axis, 2.0/n * np.abs(fourier_values[0][0:n//2]), 'g')
    subplot.plot(fourier_x_axis, 2.0/n * np.abs(fourier_values[1][0:n//2]), 'r')
    subplot.plot(fourier_x_axis, 2.0/n * np.abs(fourier_values[2][0:n//2]), 'b')
    subplot.grid()
    subplot.set_title('Fourier')

    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)


def plot_gyro(x):
    if len(gyro_values2[0]) < data_quantity:
        return

    try:
        subplot3.clear()
        subplot3.plot(x_axis, gyro_values1[0], 'g')
        subplot3.plot(x_axis, gyro_values1[1], 'r')
        subplot3.plot(x_axis, gyro_values1[2], 'b')
        subplot3.grid()
        subplot3.set_ylim(-15, 15)

        subplot4.clear()
        subplot4.plot(x_axis, gyro_values2[0], 'g')
        subplot4.plot(x_axis, gyro_values2[1], 'r')
        subplot4.plot(x_axis, gyro_values2[2], 'b')
        subplot4.grid()
        subplot4.set_ylim(-15, 15)
    except ValueError:
        print "Value error"


def plot_accelerations(x):
    if len(acceleration_values[0]) < data_quantity:
        return
    try:
        subplot2.clear()
        subplot2.plot(x_axis, acceleration_values[0], 'g')
        subplot2.plot(x_axis, acceleration_values[1], 'r')
        subplot2.plot(x_axis, acceleration_values[2], 'b')
        subplot2.grid()
        subplot2.set_ylim(-15, 15)
    except ValueError:
        print "Value error"

def plot_kalman(x):
    if len(kalman_values[0]) < data_quantity:
        return
    try:
        subplot5.clear()
        subplot5.plot(x_axis, kalman_values[0], 'g')
        subplot5.plot(x_axis, kalman_values[1], 'r')
        subplot5.plot(x_axis, kalman_values[2], 'b')
        subplot5.grid()
        subplot5.set_ylim(-15, 15)
    except ValueError:
        print "Value error"

def append_acceleration(accelerations, new_acceleration):
    temp = accelerations[:]
    temp[0].append(new_acceleration[0])
    temp[1].append(new_acceleration[1])
    temp[2].append(new_acceleration[2])
    return [
        temp[0][-data_quantity:],
        temp[1][-data_quantity:],
        temp[2][-data_quantity:]
    ]


def start_server():
    server = SimpleWebSocketServer('', 8000, SimpleEcho)
    server.serveforever()



def main():
    """
    Start the thread and the plotters

    :return:
    """
    thread.start_new_thread(start_server, ())
    """The function initialization starts in a new thread"""

    animation_interval = 100
    """Refresh time for the animation plotter. Extra 10 ms to ensure the update of the data."""

    ani = animation.FuncAnimation(fig, plot_fourier, interval=animation_interval)
    """Start the 1st plot animation"""

    ani2 = animation.FuncAnimation(fig2, plot_accelerations, interval=animation_interval)
    """Start the 2nd plot animation"""

    ani3 = animation.FuncAnimation(fig2, plot_gyro, interval=animation_interval)

    ani4 = animation.FuncAnimation(fig2, plot_kalman, interval=animation_interval)

    plt.show()

main()

