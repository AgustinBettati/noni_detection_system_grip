import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import thread
import datetime as dt
from MPU6050 import MPU6050
from time import sleep
from transformations import xTransform, yTransform, zTransform, applyTransformations, generate_two_matrices


# Create a new instance of the MPU6050 class
sensor = MPU6050(0x68)
sensor2 = MPU6050(0x69)

# Variables for ploting
fig = plt.figure()
subplot = fig.add_subplot(2, 2, 1)
subplot2 = fig.add_subplot(2, 2, 2)

# Acceleration from sensor
acceleration_values = np.empty(0)

# Acceleration from sensor2
acceleration_values2 = np.empty(0)
# X axis
i = 0
i2 = 0
time = np.empty(1)
time2 = np.empty(1)

# Matrices
x_mat = np.empty(0)
y_mat = np.empty(0)
z_mat = np.empty(0)
x_mat2 = np.empty(0)
y_mat2 = np.empty(0)
z_mat2 = np.empty(0)

class Accel:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

def get_data_accelerometers():
    while True:
        get_data_accelerometer1()
        get_data_accelerometer2()

# Get acceleration data
def get_data_accelerometer1():

    global acceleration_values, time, i, x_mat, y_mat, z_mat

    accel_data = sensor.get_accel_data()

    # Need to be multiplied by the matrix
    ax = accel_data['x']
    ay = accel_data['y']
    az = accel_data['z']

    if x_mat.size == 0 | y_mat.size == 0 | z_mat.size == 0:
        matrices = generate_two_matrices(Accel(ax, ay,az))
        x_mat = matrices[0]
        y_mat = matrices[1]
        z_mat = matrices[2]

   #  time = np.append(time, dt.datetime.now().strftime('%f'))
    values_rotated = applyTransformations(Accel(ax, ay, az),[x_mat, y_mat, z_mat])
    time = np.append(time, i)
    i += 1

    acceleration_values = np.append(Accel(values_rotated.x, values_rotated.y, values_rotated.z), acceleration_values)

    get_data_accelerometer2()

    sleep(0.5)

# Get acceleration data
def get_data_accelerometer2():
    global time2, i2, acceleration_values2, x_mat2, y_mat2, z_mat2

    accel_data2 = sensor2.get_accel_data()

    ax = accel_data2['x']
    ay = accel_data2['y']
    az = accel_data2['z']


    if x_mat2.size == 0 | y_mat2.size == 0 | z_mat2.size == 0:
        matrices = generate_two_matrices(Accel(ax, ay, az))

        x_mat2 = matrices[0]
        y_mat2 = matrices[1]
        z_mat2 = matrices[2]


    # time2 = np.append(time2, dt.datetime.now().strftime('%f'))
    values_rotated = applyTransformations([ax, ay, az], [x_mat2, y_mat2, z_mat2])
    time2 = np.append(time2, i2)
    i2 +=1

    acceleration_values2 = np.append(Accel(values_rotated.x, values_rotated.y, values_rotated.z), acceleration_values2)


# This function is called periodically from FuncAnimation
def plot_acceleration(x):
    global time, acceleration_values

    if len(time) == 0:
        return

    # Limit x and y lists to 20 items
    acceleration_values_copy = acceleration_values[-20]
    acceleration_values = acceleration_values[-20]

    time = time[-20:]
    time_copy = time[-20:]

    # Draw x and y lists
    subplot.clear()
    subplot.plot(time_copy, acceleration_values_copy.x, 'g')
    subplot.plot(time_copy, acceleration_values_copy.y, 'b')
    subplot.plot(time_copy, acceleration_values_copy.z, 'r')

    # Format plot
    subplot.set_ylim([-15,15])
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)

def plot_acceleration2(x):
    global time2,acceleration_values2

    if len(time2) == 0:
        return
    # Add x and y to lists

    # Limit x and y lists to 20 items
    acceleration_values_copy = acceleration_values2[-20]
    acceleration_values2 = acceleration_values2[-20]
    time2 = time2[-20:]
    time_copy = time2[-20:]

    # Draw x and y lists
    subplot2.clear()
    subplot2.plot(time_copy, acceleration_values_copy.x, 'g')
    subplot2.plot(time_copy, acceleration_values_copy.y, 'b')
    subplot2.plot(time_copy, acceleration_values_copy.z, 'r')

    # Format plot
    subplot2.set_ylim([-15,15])
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)

def main():
    # the function get_data_accelerometer start in a new thread
    thread.start_new_thread( get_data_accelerometers, () )

    # Start the plot animation, with an interval of 1000ms
    ani = animation.FuncAnimation(fig, plot_acceleration, fargs=([]), interval=5000)
    ani2 = animation.FuncAnimation(fig, plot_acceleration2, fargs=([]), interval=5000)
    plt.show()

main()
