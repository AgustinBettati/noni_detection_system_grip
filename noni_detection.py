import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import thread
import datetime as datetime
from MPU6050 import MPU6050
from time import sleep
import time
from transformations import apply_first_transformation, generate_two_matrices, \
    apply_all_transformations, z_transform, Accel
from fourier import apply_fourier

# Create a new instance of the MPU6050 class
sensor = MPU6050(0x68)
sensor2 = MPU6050(0x69)

# Variables for plotting
fig = plt.figure()
subplot = fig.add_subplot(2, 2, 1)
subplot2 = fig.add_subplot(2, 2, 1)
subplot3 = fig.add_subplot(2, 2, 1)

# Matrices
x_mat = np.empty(0)
y_mat = np.empty(0)
z_mat = np.empty(0)
x_mat2 = np.empty(0)
y_mat2 = np.empty(0)

# Quantity of values to calculate the third matrix
third_matrix_values = 100
# Interval between two accelerations when calculating the third matrix
third_matrix_interval = 0.2

# Interval between two accelerations in seconds
frequency = 0.25

# Quantity of accelerations to get before doing fourier
data_quantity = 100

# Values for plotting: fourier, raw accelerations and accelerations subtracted
fourier_values = np.empty(0)
raw_acceleration_values = np.empty(0)
subtracted_acceleration_values = np.empty(0)

# min value of module of acceleration to begin a recalibration
tolerance_of_recalibration = 500

# min amount of time until new calibration can be made (seconds)
time_limit_of_recalibration = 120

time_last_calibration = 0.0

# min magnitude value of acceleration to calculate 3rd matrix
min_magnitude = 15


# Main method. Generates the matrices and then enters a loop and start getting the accelerometer values
def get_data_accelerometers():
    global fourier_values, time_last_calibration, raw_acceleration_values, subtracted_acceleration_values
    print ("start getting accelerations")
    quantity = 0
    acceleration_values1 = []
    acceleration_values2 = []

    try_calibration = False
    if time.time() - time_last_calibration > time_limit_of_recalibration:
        try_calibration = True

    while quantity < data_quantity:
        now = datetime.datetime.now()
        accel1 = get_data_accelerometer1()
        accel2 = get_data_accelerometer2()
        if try_calibration and accel1.module() > tolerance_of_recalibration:
            print("Starting recalibration of third matrix")
            get_third_matrix()
            get_data_accelerometers()
            time_last_calibration = time.time()
        acceleration_values1.append(accel1)
        acceleration_values2.append(accel2)
        sleep(frequency - (datetime.datetime.now() - now).seconds)
        quantity += 1
    raw_acceleration_values = acceleration_values1
    subtracted_acceleration_values = subtract_accels(acceleration_values1, acceleration_values2)
    print ("accelerations subtracted, making fourier")
    fourier_values = apply_fourier(subtracted_acceleration_values)
    print ("finish fourier")
    get_data_accelerometers()


# print accelerations, just for testing purposes
def print_accelerations(accels):
    for i in range(len(accels)):
        print ("x: ")
        print(accels[i].x)
        print (", y: ")
        print (accels[i].y)
        print (", z: ")
        print (accels[i].z)
        print ("\n")


# Subtract one array of acceleration with another one
def subtract_accels(accel1, accel2):
    accel = []
    for i in range(len(accel1)):
        x = accel1[i].x - accel2[i].x
        y = accel1[i].y - accel2[i].y
        z = accel1[i].z - accel2[i].z

        accel.append(Accel(x, y, z))
    return accel


# defines the matrix z for the sensor 1 and sensor 2
def get_third_matrix():
    global z_mat, min_magnitude

    print("getting third matrix, please move the accelerometers")

    # Test magnitude of acceleration is bigger than a pre-established value
    b1 = True
    while b1:
        acel_raw = get_accel(sensor)
        magnitude = np.sqrt(np.power(acel_raw.x, 2) + np.power(acel_raw.y, 2) + np.power(acel_raw.z, 2))
        b1 = magnitude < min_magnitude

    quantity = 0
    data_accelerometer = []
    data_accelerometer2 = []
    while quantity < third_matrix_values:
        data_accelerometer.append(apply_first_transformation(get_accel(sensor), [x_mat, y_mat]))
        data_accelerometer2.append(apply_first_transformation(get_accel(sensor2), [x_mat2, y_mat2]))
        quantity += 1
        sleep(third_matrix_interval)
    print(quantity)
    z_mat = z_transform(data_accelerometer, data_accelerometer2)
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


# Plot fourier of segment of data
def plot_fourier(unused_param):
    global fourier_values

    if len(fourier_values) == 0:
        return

    # Number of sample points
    n = fourier_values.size
    # or N = fourier_segment_length, ie N = 600

    # sample spacing
    t = 1.0 / frequency

    # returns evenly spaced numbers from 0 to N, with n*t increments. (try instead of xf)
    x = np.linspace(0.0, n * t, n)

    # no idea what this does, why not use x?
    xf = np.linspace(0.0, 1.0 / (2.0 * t), n // 2)
    
    subplot.clear()
    subplot.plot(xf, 2.0/n * np.abs(fourier_values[0][0:n//2]), 'g')
    subplot.plot(xf, 2.0/n * np.abs(fourier_values[1][0:n//2]), 'r')
    subplot.plot(xf, 2.0/n * np.abs(fourier_values[2][0:n//2]), 'b')
    subplot.grid()
    subplot.title('Fourier')

    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)


# Plot raw acceleration values and subtracted accleration values
def plot_accelerations(x):
    if len(raw_acceleration_values) == 0 | len(subtracted_acceleration_values) == 0:
        return

    x_axis = np.linspace(1, data_quantity, data_quantity)

    subplot2.clear()
    subplot2.plot(raw_acceleration_values[0], x_axis, 'g')
    subplot2.plot(raw_acceleration_values[1], x_axis, 'r')
    subplot2.plot(raw_acceleration_values[2], x_axis, 'b')
    subplot2.grid()
    subplot2.title('Raw accelerations')

    subplot3.clear()
    subplot3.plot(subtracted_acceleration_values[0], x_axis, 'g')
    subplot3.plot(subtracted_acceleration_values[1], x_axis, 'r')
    subplot3.plot(subtracted_acceleration_values[2], x_axis, 'b')
    subplot3.grid()
    subplot3.title('Subtracted accelerations')


# Get the matrices and start the data collection loop
def initialization():
    global time_last_calibration

    print("initializing")
    get_first_matrices()
    get_third_matrix()
    time_last_calibration = time.time()
    get_data_accelerometers()


# Start the thread and the plotters
def main():
    # the function initialization start in a new thread
    thread.start_new_thread(initialization, ())

    # refresh time for the animation plotter. Extra 10 ms to ensure the update of the data.
    interval = 5000

    # start the plot animation
    ani = animation.FuncAnimation(fig, plot_fourier, fargs=([]), interval=interval)
    ani = animation.FuncAnimation(fig, plot_accelerations, fargs=([]), interval=interval)
    plt.show()


main()
