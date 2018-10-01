import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import thread
import datetime as datetime
from MPU6050 import MPU6050
from time import sleep
from transformations import apply_first_transformation, generate_two_matrices, apply_all_transformations, zTransform, Accel


# Create a new instance of the MPU6050 class
sensor = MPU6050(0x68)
sensor2 = MPU6050(0x69)

# Variables for ploting
# fig = plt.figure()
# subplot = fig.add_subplot(2, 2, 1)
# subplot2 = fig.add_subplot(2, 2, 2)

# # X axis
# i = 0
# i2 = 0
# time = np.empty(1)
# time2 = np.empty(1)

# Matrices
x_mat = np.empty(0)
y_mat = np.empty(0)
z_mat = np.empty(0)
x_mat2 = np.empty(0)
y_mat2 = np.empty(0)

# Quantity of values to calculate the third matrix
third_matrix_values = 20

# Interval between two accelerations in seconds
frequency = 0.25

# Quantity of accelerations to get before doing fourier
data_quantity = 1000


# Main method. Generates the matrices and then enters a loop and start getting the accelerometer values
def get_data_accelerometers():
    print ("start accelerations")
    quantity = 0
    acceleration_values1 = []
    acceleration_values2 = []

    while quantity < data_quantity:
        now = datetime.datetime.now()
        acceleration_values1.append(get_data_accelerometer1())
        acceleration_values2.append(get_data_accelerometer2())
        print (frequency - (datetime.datetime.now() - now).seconds)
        sleep(frequency - (datetime.datetime.now() - now).seconds)
    accelerations = substract_accels(acceleration_values1, acceleration_values2)
    #     TODO do fourier
    print (accelerations)
    get_data_accelerometers()


def substract_accels(accel1, accel2):
    accel = []
    for i in range(len(accel1)):
        x = accel1[i].x - accel2[i].x
        y = accel1[i].y - accel2[i].y
        z = accel1[i].z - accel2[i].z

        accel.append(Accel(x, y, z))
    return accel


def initialization():
    print("initializing")
    get_first_matrices()
    get_third_matrix()
    get_data_accelerometers()


# defines the matrix z for the sensor 1 and sensor 2
def get_third_matrix():
    global z_mat
    quantity = 0
    data_accelerometer = []
    data_accelerometer2 = []
    while quantity < third_matrix_values:
        data_accelerometer.append(apply_first_transformation(get_accel(sensor), [x_mat, y_mat]))
        data_accelerometer2.append(apply_first_transformation(get_accel(sensor2), [x_mat2, y_mat2]))
        quantity += 1
        sleep(200)
    z_mat = zTransform(data_accelerometer, data_accelerometer2)
    print("Obtained third matrix")


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
    print("Obtained first two matrices")


# Rotate the acceleration values from the sensor 1 and appends them to the acceleration_values.
def get_data_accelerometer1():

    global x_mat, y_mat, z_mat

    accel = get_accel(sensor)

    values_rotated = apply_all_transformations(accel, [x_mat, y_mat, z_mat])

    return Accel(values_rotated.x, values_rotated.y, values_rotated.z)


# Rotate the acceleration values from the sensor 2 and appends them to the acceleration_values.
def get_data_accelerometer2():
    global x_mat2, y_mat2

    accel = get_accel(sensor2)

    values_rotated = apply_first_transformation(accel, [x_mat2, y_mat2])

    return Accel(values_rotated.x, values_rotated.y, values_rotated.z)


# Get the acceleration values from a specific sensor
def get_accel(custom_sensor):
    accel_data = custom_sensor.get_accel_data()
    return Accel(accel_data['x'], accel_data['y'], accel_data['z'])

#
# # Plot the acceleration values and x axis from the sensor 1
# def plot_acceleration(x):
#     global time, acceleration_values
#
#     if len(time) == 0:
#         return
#
#     # Limit x and y lists to 20 items
#     acceleration_values_copy = acceleration_values[-20]
#     acceleration_values = acceleration_values[-20]
#     time = time[-20:]
#     time_copy = time[-20:]
#
#     # Draw x and y lists
#     subplot.clear()
#     subplot.plot(time_copy, acceleration_values_copy.x, 'g')
#     subplot.plot(time_copy, acceleration_values_copy.y, 'b')
#     subplot.plot(time_copy, acceleration_values_copy.z, 'r')
#
#     # Format plot
#     subplot.set_ylim([-15, 15])
#     plt.xticks(rotation=45, ha='right')
#     plt.subplots_adjust(bottom=0.30)
#
#
# # Plot the acceleration values and x axis from the sensor 2
# def plot_acceleration2(x):
#     global time2, acceleration_values2
#
#     if len(time2) == 0:
#         return
#
#     # Limit x and y lists to 20 items
#     acceleration_values_copy = acceleration_values2[-20]
#     acceleration_values2 = acceleration_values2[-20]
#     time2 = time2[-20:]
#     time_copy = time2[-20:]
#
#     # Draw x and y lists
#     subplot2.clear()
#     subplot2.plot(time_copy, acceleration_values_copy.x, 'g')
#     subplot2.plot(time_copy, acceleration_values_copy.y, 'b')
#     subplot2.plot(time_copy, acceleration_values_copy.z, 'r')
#
#     # Format plot
#     subplot2.set_ylim([-15, 15])
#     plt.xticks(rotation=45, ha='right')
#     plt.subplots_adjust(bottom=0.30)


# Start the thread and the plotters
def main():
    # the function get_data_accelerometer start in a new thread
    thread.start_new_thread(initialization, ())

    # Start the plot animation, with an interval of 1000ms
    # ani = animation.FuncAnimation(fig, plot_acceleration, fargs=([]), interval=5000)
    # ani2 = animation.FuncAnimation(fig, plot_acceleration2, fargs=([]), interval=5000)
    # plt.show()


initialization()
