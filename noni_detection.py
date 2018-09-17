import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import thread
import datetime as dt
from MPU6050 import MPU6050
from time import sleep
from transformations import xTransform, yTransform, zTransform, applyTransformations, generateTransformationMatrices


# Create a new instance of the MPU6050 class
sensor = MPU6050(0x68)
sensor2 = MPU6050(0x69)

# Variables for ploting
fig = plt.figure()
subplot = fig.add_subplot(2, 2, 1)
subplot2 = fig.add_subplot(2, 2, 2)
subplot3 = fig.add_subplot(2, 2, 3)
subplot4 = fig.add_subplot(2, 2, 4)

# Acceleration from sensor
ax_values = np.empty(1)
ay_values = np.empty(1)
az_values = np.empty(1)

# Acceleration from sensor2
ax_values2 = np.empty(1)
ay_values2 = np.empty(1)
az_values2 = np.empty(1)

# Acceleration rotated from sensor
ax_rot_values = np.empty(1)
ay_rot_values = np.empty(1)
az_rot_values = np.empty(1)

# Acceleration rotated from sensor2
ax_rot_values2 = np.empty(1)
ay_rot_values2 = np.empty(1)
az_rot_values2 = np.empty(1)

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

# Get acceleration data
def get_data_accelerometer():

    global ax_values, ay_values, az_values, ax_rot_values, ay_rot_values, az_rot_values, time, i, x_mat, y_mat, z_mat

    while True:
        accel_data = sensor.get_accel_data()

        # Need to be multiplied by the matrix
        ax = accel_data['x']
        ay = accel_data['y']
        az = accel_data['z']

        gyro_data = sensor.get_gyro_data()
        gx = gyro_data['x']
        gy = gyro_data['y']
        gz = gyro_data['z']
        if x_mat.size == 0 | y_mat.size == 0 | z_mat.size == 0:

            matrices = generateTransformationMatrices(ax, ay,az, gx, gy, gz)

            x_mat = matrices[0]
            y_mat = matrices[1]
            z_mat = matrices[2]

       #  time = np.append(time, dt.datetime.now().strftime('%f'))
        values_rotated = applyTransformations([ax, ay, az],[x_mat, y_mat, z_mat])
        time = np.append(time, i)
        i += 1

        ax_values = np.append(ax_values, ax)
        ay_values = np.append(ay_values, ay)
        az_values = np.append(az_values, az)


        ax_rot_values = np.append(ax_rot_values, values_rotated[0])
        ay_rot_values = np.append(ay_rot_values, values_rotated[1])
        az_rot_values = np.append(az_rot_values, values_rotated[2])

        get_data_accelerometer2()
        sleep(0.5)

# Get acceleration data
def get_data_accelerometer2():
    global ax_values2, ay_values2, az_values2, time2, i2, ax_rot_values2, ay_rot_values2, az_rot_values2, x_mat2, y_mat2, z_mat2


    accel_data2 = sensor2.get_accel_data()

    ax = accel_data2['x']
    ay = accel_data2['y']
    az = accel_data2['z']

    if x_mat2.size == 0 | y_mat2.size == 0 | z_mat2.size == 0:
        gyro_data = sensor2.get_gyro_data()
        gx = gyro_data['x']
        gy = gyro_data['y']
        gz = gyro_data['z']

        matrices = generateTransformationMatrices(ax, ay, az, gx, gy, gz)

        x_mat2 = matrices[0]
        y_mat2 = matrices[1]
        z_mat2 = matrices[2]


    # time2 = np.append(time2, dt.datetime.now().strftime('%f'))
    values_rotated = applyTransformations([ax, ay, az], [x_mat2, y_mat2, z_mat2])
    time2 = np.append(time2, i2)
    i2 +=1

    ax_values2 = np.append(ax_values2, ax)
    ay_values2 = np.append(ay_values2, ay)
    az_values2 = np.append(az_values2, az)

    ax_rot_values2 = np.append(ax_rot_values2, values_rotated[0])
    ay_rot_values2 = np.append(ay_rot_values2, values_rotated[1])
    az_rot_values2 = np.append(az_rot_values2, values_rotated[2])


# This function is called periodically from FuncAnimation
def plot_acceleration(x):
    global time, ax_values, ay_values, az_values, ax_rot_values, ay_rot_values, az_rot_values

    if len(time) == 0:
        return

    # Limit x and y lists to 20 items
    ax_values = ax_values[-20:]
    ay_values = ay_values[-20:]
    az_values = az_values[-20:]
    ax_rot_values = ax_rot_values[-20:]
    ay_rot_values = ay_rot_values[-20:]
    az_rot_values = az_rot_values[-20:]
    time = time[-20:]

    # Draw x and y lists
    subplot.clear()
    subplot.plot(time, ax_values, 'g')
    subplot.plot(time, ay_values, 'b')
    subplot.plot(time, az_values, 'r')
    subplot3.clear()
    subplot3.plot(time, ax_rot_values, 'g')
    subplot3.plot(time, ay_rot_values, 'b')
    subplot3.plot(time, az_rot_values, 'r')

    # Format plot
    subplot.set_ylim([-15,15])
    subplot3.set_ylim([-15, 15])
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)

def plot_acceleration2(x):
    global time2,ax_values2, ay_values2, az_values2, ax_rot_values2, ay_rot_values2, az_rot_values2


    if len(time2) == 0:
        return
    # Add x and y to lists

    # Limit x and y lists to 20 items
    ax_values2 = ax_values2[-20:]
    ax_copy = ax_values2[-20:]
    ay_values2 = ay_values2[-20:]
    ay_copy = ay_values2[-20:]
    az_values2 = az_values2[-20:]
    az_copy = az_values2[-20:]
    ax_rot_values2 = ax_rot_values2[-20:]
    ax_rot_copy = ax_rot_values2[-20:]
    ay_rot_values2 = ay_rot_values2[-20:]
    ay_rot_copy = ay_rot_values2[-20:]
    az_rot_values2 = az_rot_values2[-20:]
    az_rot_copy = az_rot_values2[-20:]



    time2 = time2[-20:]
    time_copy = time2[-20:]

    # Draw x and y lists
    subplot2.clear()
    subplot2.plot(time_copy, ax_copy, 'g')
    subplot2.plot(time_copy, ay_copy, 'b')
    subplot2.plot(time_copy, az_copy, 'r')
    subplot4.clear()
    subplot4.plot(time_copy, ax_rot_copy, 'g')
    subplot4.plot(time_copy, ay_rot_copy, 'b')
    subplot4.plot(time_copy, az_rot_copy, 'r')

    # Format plot
    subplot2.set_ylim([-15,15])
    subplot4.set_ylim([-15,15])
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)

def main():
    # the function get_data_accelerometer start in a new thread
    thread.start_new_thread( get_data_accelerometer, () )

    # Start the plot animation, with an interval of 1000ms
    ani = animation.FuncAnimation(fig, plot_acceleration, fargs=([]), interval=5000)
    ani2 = animation.FuncAnimation(fig, plot_acceleration2, fargs=([]), interval=5000)
    plt.show()

main()
