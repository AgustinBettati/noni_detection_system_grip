from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import thread

fig_fourier = plt.figure()
"""Figure to plot fourier"""
gs_fourier = gridspec.GridSpec(2,1)
subplot_fourier = fig_fourier.add_subplot(gs_fourier[0, :])
"""Subplot where fourier will be plotted"""
subplot_fourier_kalman = fig_fourier.add_subplot(gs_fourier[1, :])
"""Subplot where fourier with kalman will be plotted"""

fig = plt.figure()
"""Figure to plot measurements"""
gs = gridspec.GridSpec(3, 2)
subplot_measurements = fig.add_subplot(gs[0, :])
"""Subplot where the rotated measurements will be plotted"""
subplot_gyro_1 = fig.add_subplot(gs[1, 0])
subplot_gyro_2 = fig.add_subplot(gs[1, 1])
"""Subplots where the raw values of the gyroscope will be plotted"""
subplot_kalman = fig.add_subplot(gs[2, :])
"""Subplot where the rotated measurements and the gyro values, combined with kalman, will be plotted"""

fourier_values = np.empty(0)
fourier_kalman_values = np.empty(0)
"""Values for plotting fourier"""

fourier_x_axis = []
"""X axis values for plotting fourier"""

acceleration_values = [[0], [0], [0]]
"""Values for plotting rotated measurements"""
gyro_values1 = [[0], [0], [0]]
gyro_values2 = [[0], [0], [0]]
"""Values for plotting raw gyro values"""

kalman_values = [[0], [0], [0]]
"""Values for plotting kalman values"""


data_quantity = 100
"""Quantity of measurements before start plotting"""

x_axis = np.linspace(1, data_quantity, data_quantity)
"""x_axis for both of the fourier plotters"""

class SimpleEcho(WebSocket):

    def handleMessage(self):
        """
        Receive messages sent by the websocket client
        The format of the message is as follow:
        result[0]: type of message (measurements or fourier)
        result[1]: body of the message
        :return:
        """

        result = json.loads(self.data)
        if result[0] == "measurements":
            handle_measurements(result[1])
        else:
            handle_fourier(result[1])



def handle_measurements(result):
    """
    Reciver a result and assign each element to a variable
    :param result:
        the format of the result is the following:
        result[0]: [[double]]
            acceleration values rotated
        result[1]: [[double]]
            raw gyro value from the sensor 1
        result[2]: [[double]]
            raw gyro value from the sensor 2
        result[3]: [[double]]
            kalman values of the measurements with the gyro values
    :return:
    """

    global acceleration_values, gyro_values1, kalman_values, fourier_values, gyro_values2

    acceleration_values = append_acceleration(acceleration_values, result[0])
    gyro_values1 = append_acceleration(gyro_values1, result[1])
    gyro_values2 = append_acceleration(gyro_values2, result[2])
    kalman_values = append_acceleration(kalman_values, result[3])


def handle_fourier(result):
    """
    Receive a result and assign each element to a variable
    :param result:
        the format of the result is the following:
        result[0]: [[string]]
            fourier values
        result[1]: [[string]]
            fourier values with kalman
        result[2]: [[double]]
            x_axis used to plot both fourier
    :return: void
    """

    global fourier_values, fourier_kalman_values, fourier_x_axis

    fourier_values = deserialize_fourier(result[0])

    fourier_kalman_values = deserialize_fourier(result[1])
    fourier_x_axis = result[2]


def deserialize_fourier(fourier):
    """
    Transform the strings of fourier to complex numbers
    :param fourier: [[string]]
    :return: [[complex]]
    """
    new_fourier = []
    for i in range (3):
        new_fourier.append([])
        for j in fourier[i].split(","):
            new_fourier[i].append(complex(j))
    return new_fourier


def plot_fourier(unused_param):
    """
    Plot fourier values and fourier values with kalman.

    :param unused_param:
        parameter that is not used, needed in order to comply with matplotlib.animation interface
    :return: void
    """

    global fourier_values, fourier_x_axis
    """The values after applying fourier transform"""

    if len(fourier_values) == 0:
        return

    n = len(fourier_values[0])
    """Number of sample points"""

    subplot_fourier.clear()
    subplot_fourier.plot(fourier_x_axis, 2.0 / n * np.abs(fourier_values[0][0:n // 2]), 'g')
    subplot_fourier.plot(fourier_x_axis, 2.0 / n * np.abs(fourier_values[1][0:n // 2]), 'r')
    subplot_fourier.plot(fourier_x_axis, 2.0 / n * np.abs(fourier_values[2][0:n // 2]), 'b')
    subplot_fourier.grid()
    subplot_fourier.set_title('Fourier')

    subplot_fourier_kalman.clear()
    subplot_fourier_kalman.plot(fourier_x_axis, 2.0 / n * np.abs(fourier_kalman_values[0][0:n // 2]), 'g')
    subplot_fourier_kalman.plot(fourier_x_axis, 2.0 / n * np.abs(fourier_kalman_values[1][0:n // 2]), 'r')
    subplot_fourier_kalman.plot(fourier_x_axis, 2.0 / n * np.abs(fourier_kalman_values[2][0:n // 2]), 'b')
    subplot_fourier_kalman.grid()
    subplot_fourier_kalman.set_title('Fourier with kalman')

    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)


def plot_gyro(unused_param):
    """
    Plot gyroscope values.

     :param unused_param:
        parameter that is not used, needed in order to comply with matplotlib.animation interface
    :return: void
    """
    if len(gyro_values2[0]) < data_quantity:
        return

    try:
        subplot_gyro_1.clear()
        subplot_gyro_1.plot(x_axis, gyro_values1[0], 'g')
        subplot_gyro_1.plot(x_axis, gyro_values1[1], 'r')
        subplot_gyro_1.plot(x_axis, gyro_values1[2], 'b')
        subplot_gyro_1.grid()
        subplot_gyro_1.set_ylim(-15, 15)

        subplot_gyro_2.clear()
        subplot_gyro_2.plot(x_axis, gyro_values2[0], 'g')
        subplot_gyro_2.plot(x_axis, gyro_values2[1], 'r')
        subplot_gyro_2.plot(x_axis, gyro_values2[2], 'b')
        subplot_gyro_2.grid()
        subplot_gyro_2.set_ylim(-15, 15)
    except ValueError:
        print "Value error"
        start_animations()


def plot_accelerations(unused_param):
    """
     Plot acceleration values.

      :param unused_param:
         parameter that is not used, needed in order to comply with matplotlib.animation interface
     :return: void
     """
    if len(acceleration_values[0]) < data_quantity:
        return
    try:
        subplot_measurements.clear()
        subplot_measurements.plot(x_axis, acceleration_values[0], 'g')
        subplot_measurements.plot(x_axis, acceleration_values[1], 'r')
        subplot_measurements.plot(x_axis, acceleration_values[2], 'b')
        subplot_measurements.grid()
        subplot_measurements.set_ylim(-15, 15)
    except ValueError:
        print "Value error"
        start_animations()

def plot_kalman(unused_param):
    """
      Plot kalman values.
      :param unused_param:
         parameter that is not used, needed in order to comply with matplotlib.animation interface
     :return: void
     """
    if len(kalman_values[0]) < data_quantity:
        return
    try:
        subplot_kalman.clear()
        subplot_kalman.plot(x_axis, kalman_values[0], 'g')
        subplot_kalman.plot(x_axis, kalman_values[1], 'r')
        subplot_kalman.plot(x_axis, kalman_values[2], 'b')
        subplot_kalman.grid()
        subplot_kalman.set_ylim(-15, 15)
    except ValueError:
        print "Value error"
        start_animations()

def append_acceleration(accelerations, new_acceleration):
    """
    Add a new acceleration to the last position of accelerations
    :param accelerations: [[Double]]
    :param new_acceleration: [[Double]]
    :return: [[Double]]
        A new array with the acceleration appended.
    """
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
    """
    Start the server in localhost with port 8000
    :return: void
    """
    server = SimpleWebSocketServer('', 8000, SimpleEcho)
    server.serveforever()

def start_animations():
    """
    Start the animations for all the plotters.
    :return: void
    """

    animation_interval = 500
    """Refresh time for the animation plotter. Extra 10 ms to ensure the update of the data."""

    ani = animation.FuncAnimation(fig_fourier, plot_fourier, interval=animation_interval)

    ani2 = animation.FuncAnimation(fig, plot_accelerations, interval=animation_interval)

    ani3 = animation.FuncAnimation(fig, plot_gyro, interval=animation_interval)

    ani4 = animation.FuncAnimation(fig, plot_kalman, interval=animation_interval)

    plt.show()

def main():
    """
    Start the thread and the plotters

    :return:
    """
    thread.start_new_thread(start_server, ())
    """The function initialization starts in a new thread"""

    start_animations()

main()

