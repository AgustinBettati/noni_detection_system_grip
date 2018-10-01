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
acceleration_values = []

# Acceleration from sensor2
acceleration_values2 = []

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

# Quantity of values to calculate the third matrix
third_matrix_values = 10


class Accel:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


# Main method. Generates the matrices and then enters a loop and start getting the accelerometer values
def get_data_accelerometers():
    get_first_matrices()
    get_third_matrix()
    while True:
        get_data_accelerometer1()
        get_data_accelerometer2()
        sleep(0.5)


# defines the matrix z for the sensor 1 and sensor 2
def get_third_matrix():
    quantity = 0
    data_accelerometer = []
    data_accelerometer2 = []
    while quantity < third_matrix_values:
        data_accelerometer.append(applyTransformations(get_accel(sensor), [x_mat, y_mat]))
        data_accelerometer2.append(applyTransformations(get_accel(sensor2), [x_mat2, y_mat2]))
        quantity += 1


# defines matrix x and matrix y for the sensor 1 and 2
def get_first_matrices():
    global x_mat, y_mat, x_mat2, y_mat2

    accel = get_accel(sensor)
    accel2 = get_accel(sensor2)

    matrices = generate_two_matrices(accel)
    x_mat = matrices[0]
    y_mat = matrices[1]

    matrices2 = generate_two_matrices(accel2)
    x_mat2 = matrices2[0]
    y_mat2 = matrices2[1]


# Rotate the acceleration values from the sensor 1 and appends them to the acceleration_values.
def get_data_accelerometer1():

    global acceleration_values, time, i, x_mat, y_mat, z_mat

    accel = get_accel(sensor)

    values_rotated = applyTransformations(accel, [x_mat, y_mat, z_mat])
    time = np.append(time, i)
    i += 1

    acceleration_values.append(Accel(values_rotated.x, values_rotated.y, values_rotated.z))


# Rotate the acceleration values from the sensor 2 and appends them to the acceleration_values.
def get_data_accelerometer2():
    global time2, i2, acceleration_values2, x_mat2, y_mat2, z_mat2

    accel = get_accel(sensor2)

    values_rotated = applyTransformations(accel, [x_mat2, y_mat2, z_mat2])
    time2 = np.append(time2, i2)
    i2 += 1

    acceleration_values2.append(Accel(values_rotated.x, values_rotated.y, values_rotated.z))


# Get the acceleration values from a specific sensor
def get_accel(custom_sensor):
    accel_data = custom_sensor.get_accel_data()
    return Accel(accel_data['x'], accel_data['y'], accel_data['z'])


# Plot the acceleration values and x axis from the sensor 1
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
    subplot.set_ylim([-15, 15])
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)


# Plot the acceleration values and x axis from the sensor 2
def plot_acceleration2(x):
    global time2, acceleration_values2

    if len(time2) == 0:
        return

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
    subplot2.set_ylim([-15, 15])
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)


# Start the thread and the plotters
def main():
    # the function get_data_accelerometer start in a new thread
    thread.start_new_thread(get_data_accelerometers, ())

    # Start the plot animation, with an interval of 1000ms
    ani = animation.FuncAnimation(fig, plot_acceleration, fargs=([]), interval=5000)
    ani2 = animation.FuncAnimation(fig, plot_acceleration2, fargs=([]), interval=5000)
    plt.show()


main()
