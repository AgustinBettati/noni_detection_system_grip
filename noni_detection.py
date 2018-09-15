import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import thread
import datetime as dt
from MPU6050 import MPU6050
from time import sleep


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
axValues = np.empty(1)
ayValues = np.empty(1)
azValues = np.empty(1)

# Acceleration from sensor2
axValues2 = np.empty(1)
ayValues2 = np.empty(1)
azValues2 = np.empty(1)

# X axis
i = 0
i2 = 0
time = np.empty(1)
time2 = np.empty(1)

# Get acceleration data
def get_data_accelerometer():
    while True:
        global axValues
        global ayValues
        global azValues
        global time
	global i

        accel_data = sensor.get_accel_data()

        # If the matrix are not yet calculated, calculate them and get gyro data
        # gyro_data = sensor.get_gyro_data()
        # gyro_data2 = sensor2.get_gyro_data()
        # gx = gyro_data['x']
        # gy = gyro_data['y']
        # gz = gyro_data['z']

        # Need to be multiplied by the matrix
        ax = accel_data['x']
        ay = accel_data['y']
        az = accel_data['z']

       #  time = np.append(time, dt.datetime.now().strftime('%f'))
	time = np.append(time, i)
	i += 1

        axValues = np.append(axValues, ax)
        ayValues = np.append(ayValues, ay)
        azValues = np.append(azValues, az)

	sleep(0.5)

# Get acceleration data
def get_data_accelerometer2():
    while True:
        global axValues2
        global ayValues2
        global azValues2
        global time2
	global i2

        accel_data2 = sensor2.get_accel_data()

        # If the matrix are not yet calculated, calculate them and get gyro data
        # gyro_data = sensor.get_gyro_data()
        # gyro_data2 = sensor2.get_gyro_data()
        # gx = gyro_data['x']
        # gy = gyro_data['y']
        # gz = gyro_data['z']

        # Need to be multiplied by the matrix
        ax2 = accel_data2['x']
        ay2 = accel_data2['y']
        az2 = accel_data2['z']

        # time2 = np.append(time2, dt.datetime.now().strftime('%f'))
	time2 = np.append(time2, i2)
	i2 +=1

        axValues2 = np.append(axValues2, ax2)
        ayValues2 = np.append(ayValues2, ay2)
        azValues2 = np.append(azValues2, az2)

	sleep(0.5)

# This function is called periodically from FuncAnimation
def plot_acceleration(x):
    global time
    global axValues
    global ayValues
    global azValues

    if len(time) == 0:
        return

    # Limit x and y lists to 20 items
    axValues = axValues[-20:]
    ayValues = ayValues[-20:]
    azValues = azValues[-20:]
    time = time[-20:]

    # Draw x and y lists
    subplot.clear()
    subplot.plot(time, axValues, 'g')
    subplot.plot(time, ayValues, 'b')
    subplot.plot(time, azValues, 'r')

    # Format plot
    subplot.set_ylim([-15,15])
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)

def plot_acceleration2(x):
    global time2
    global axValues2
    global ayValues2
    global azValues2

    if len(time2) == 0:
        return
    # Add x and y to lists

    # Limit x and y lists to 20 items
    axValues2 = axValues2[-20:]
    ayValues2 = ayValues2[-20:]
    azValues2 = azValues2[-20:]
    time2 = time2[-20:]

    # Draw x and y lists
    subplot2.clear()
    subplot2.plot(time2, axValues2, 'g')
    subplot2.plot(time2, ayValues2, 'b')
    subplot2.plot(time2, azValues2, 'r')

    # Format plot
    subplot2.set_ylim([-15,15])
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)

def main():
    # the function get_data_accelerometer start in a new thread
    thread.start_new_thread( get_data_accelerometer, () )
    thread.start_new_thread( get_data_accelerometer2, () )

    # Start the plot animation, with an interval of 1000ms
    ani = animation.FuncAnimation(fig, plot_acceleration, fargs=([]), interval=3000)
    ani2 = animation.FuncAnimation(fig, plot_acceleration2, fargs=([]), interval=3000)
    plt.show()

main()
