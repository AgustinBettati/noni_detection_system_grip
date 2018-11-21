import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import thread
import datetime as datetime

from KalmanFilter import apply_kalman_filter
from MPU6050 import MPU6050
from time import sleep
import time
from transformations import apply_first_transformation, generate_two_matrices, \
    apply_all_transformations, z_transform, Measurments
from fourier import apply_fourier

sensor = MPU6050(0x68)
"""Creates a new instance of the MPU6050 class for the first sensor"""
sensor2 = MPU6050(0x69)
"""Creates a new instance of the MPU6050 class for the second sensor"""

fig = plt.figure()
"""Figure to plot fourier"""
subplot = fig.add_subplot(1, 1, 1)
"""Subplot where fourier will be plotted"""

fig2 = plt.figure()
"""Figure to plot accelerations"""
gs = gridspec.GridSpec(2, 2)
subplot2 = fig2.add_subplot(gs[0, 0])
"""Subplot where the accelerations of the first sensor will be plotted"""
subplot3 = fig2.add_subplot(gs[0, 1])
"""Subplot where the accelerations of the second sensor will be plotted"""
subplot4 = fig2.add_subplot(gs[1, :])
"""Subplot where the rotated accelerations of the two sensors will be plotted"""

x_mat = np.empty(0)
y_mat = np.empty(0)
z_mat = np.empty(0)
x_mat2 = np.empty(0)
y_mat2 = np.empty(0)
"""Matrices use for rotations"""

third_matrix_values = 500
"""Quantity of values to get before calculating the third matrix"""

third_matrix_interval = 0.05
"""Interval between two accelerations when calculating the third matrix"""

interval = 0.1
"""Interval between two accelerations in seconds"""

data_quantity = 60
"""Quantity of accelerations to get before doing fourier"""

fourier_values = np.empty(0)
"""Values for plotting fourier"""

raw_acceleration_values = np.empty(0)
"""Values for plotting raw accelerations"""

raw_acceleration_values2 = np.empty(0)
"""Values for plotting raw acceleration"""

subtracted_acceleration_values = np.empty(0)
"""Values for plotting subtracted accelerations"""

tolerance_of_recalibration = 10
"""minimum acceleration module to begin a recalibration"""

time_last_calibration = 0.0
time_limit_of_recalibration = 60 * 10
"""minimum amount of time until new calibration can be made (in seconds)"""


min_magnitude = 15
"""minimum module required to trigger the third matrix calculation"""


def get_data_accelerometers():
    """
    Generates the matrices, enters a loop and start getting the accelerometer values
    :return: void
    """
    global fourier_values, time_last_calibration, raw_acceleration_values, raw_acceleration_values2, subtracted_acceleration_values
    print ("start getting accelerations")
    quantity = 0
    acceleration_values1 = []
    acceleration_values2 = []
    gyro_values1 = []
    gyro_values2 = []

    try_calibration = False
    if time.time() - time_last_calibration > time_limit_of_recalibration:
        try_calibration = True

    while quantity < data_quantity:
        now = datetime.datetime.now()
        accel1 = get_data_accelerometer1()
        accel2 = get_data_accelerometer2()
        gyro1 = get_data_gyro1()
        gyro2 = get_data_gyro2()
        if try_calibration and accel1.module() > tolerance_of_recalibration:
            print("Starting recalibration of third matrix")
            get_third_matrix()
            get_data_accelerometers()
            time_last_calibration = time.time()
        acceleration_values1.append(accel1)
        acceleration_values2.append(accel2)
        gyro_values1.append(gyro1)
        gyro_values2.append(gyro2)
        sleep(interval - (datetime.datetime.now() - now).seconds)
        quantity += 1
    subtracted_accelerations = subtract_measurements(acceleration_values1, acceleration_values2)
    subtracted_gyros = subtract_measurements(gyro_values1, gyro_values2)
    kalman_results = apply_kalman_filter(subtracted_accelerations, subtracted_gyros)

    # For plotting
    raw_acceleration_values = measurements_to_array(acceleration_values1)
    raw_acceleration_values2 = measurements_to_array(acceleration_values2)

    subtracted_acceleration_values = measurements_to_array(subtracted_accelerations)
    subtracted_gyro_values = measurements_to_array(subtracted_gyros)
    kalman_results_values = measurements_to_array(kalman_results)


    print ("accelerations subtracted, making fourier")
    fourier_values = apply_fourier(subtracted_accelerations)
    print ("finish fourier")
    get_data_accelerometers()


def print_accelerations(accels):
    """
    Prints accelerations, just for testing purposes
    :param accels: Accel[]
        The list of accelerations to be printed
    :return:void
    """
    for i in range(len(accels)):
        print ("x: ")
        print(accels[i].x)
        print (", y: ")
        print (accels[i].y)
        print (", z: ")
        print (accels[i].z)
        print ("\n")


def subtract_measurements(measurements1, measurements2):
    """
    Subtracts one array of accelerations with another one
    :param measurements1: Measurements[]
        The array of Measurements to be subtracted
    :param measurements2:
        The array of Measurements to be subtracted
    :return:Measurements[]
        An array of Measurements
    """
    accel = []
    for i in range(len(measurements1)):
        x = measurements1[i].x - measurements2[i].x
        y = measurements1[i].y - measurements2[i].y
        z = measurements1[i].z - measurements2[i].z

        accel.append(Measurments(x, y, z))
    return accel


def get_third_matrix():
    """
    Defines the matrix z for the sensor 1 and sensor 2
    :return: void
    """
    global z_mat, min_magnitude

    print("please move the accelerometers")

    # Test magnitude of acceleration is bigger than a pre-established value
    b1 = True
    while b1:
        acel_raw = get_accel(sensor)
        magnitude = np.sqrt(np.power(acel_raw.x, 2) + np.power(acel_raw.y, 2) + np.power(acel_raw.z, 2))
        b1 = magnitude < min_magnitude

    print("getting third matrix")
    quantity = 0
    data_accelerometer = []
    data_accelerometer2 = []
    while quantity < third_matrix_values:
        data_accelerometer.append(apply_first_transformation(get_accel(sensor), [x_mat, y_mat]))
        data_accelerometer2.append(apply_first_transformation(get_accel(sensor2), [x_mat2, y_mat2]))
        print("{}%".format(int((1 - ((third_matrix_values - quantity) / float(third_matrix_values))) * 100)))
        quantity += 1
        sleep(third_matrix_interval)
    z_mat = z_transform(data_accelerometer, data_accelerometer2)
    print("Obtained third matrix")


def get_first_matrices():
    """
    Defines matrix and matrix y for the sensor 1 and 2
    :return: void
    """
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


def get_data_accelerometer1():
    """
    Rotates the acceleration values from the sensor 1 and appends them to the acceleration_values.
    :return: Accel
        The acceleration rotated
    """
    global x_mat, y_mat, z_mat

    accel = get_accel(sensor)

    values_rotated = apply_all_transformations(accel, [x_mat, y_mat, z_mat])

    return Measurments(values_rotated.x, values_rotated.y, values_rotated.z)


def get_data_accelerometer2():
    """
    Rotates the acceleration values from the sensor 2 and appends them to the acceleration_values.
    :return: Accel
        The acceleration rotated
    """
    global x_mat2, y_mat2

    accel = get_accel(sensor2)

    values_rotated = apply_first_transformation(accel, [x_mat2, y_mat2])

    return Measurments(values_rotated.x, values_rotated.y, values_rotated.z)


def get_data_gyro1():
    """
    Rotates the gyro values from the sensor 1.
    :return: Measurements
        The gyro values rotated
    """
    global x_mat, y_mat, z_mat

    gyro = get_gyro(sensor)

    values_rotated = apply_all_transformations(gyro, [x_mat, y_mat, z_mat])

    return Measurments(values_rotated.x, values_rotated.y, values_rotated.z)


def get_data_gyro2():
    """
    Rotates the gyro values from the sensor 2.
    :return: Measurements
        The gyro values rotated
    """
    global x_mat2, y_mat2

    gyro = get_gyro(sensor2)

    values_rotated = apply_first_transformation(gyro, [x_mat2, y_mat2])

    return Measurments(values_rotated.x, values_rotated.y, values_rotated.z)


def get_accel(custom_sensor):
    """
    Gets the acceleration values from a specific sensor
    :param custom_sensor: MPU6050
        The sensor from where the accelerations will be taken.
    :return: Accel
        The acceleration sensed
    """
    accel_data = custom_sensor.get_accel_data()
    return Measurments(accel_data['x'], accel_data['y'], accel_data['z'])

def get_gyro(custom_sensor):
    """
    Gets the acceleration values from a specific sensor
    :param custom_sensor: MPU6050
        The sensor from where the accelerations will be taken.
    :return: Accel
        The acceleration sensed
    """
    gyro_data = custom_sensor.get_gyro_data()
    return Measurments(gyro_data['x'], gyro_data['y'], gyro_data['z'])


def plot_fourier(unused_param):
    """
    Plot fourier of segment of data.

    :param unused_param:
        parameter that is not used, needed in order to comply with matplotlib.animation interface
    :return:
    """

    global fourier_values
    """The values after applying fourier transform"""

    if len(fourier_values) == 0:
        return

    n = fourier_values[0].size
    """Number of sample points"""

    t = interval
    """Sample spacing"""

    xf = np.linspace(0.0, 1.0 / (2.0 * t), n // 2)
    """Equally distributed frequency values"""

    subplot.clear()
    subplot.plot(xf, 2.0/n * np.abs(fourier_values[0][0:n//2]), 'g')
    subplot.plot(xf, 2.0/n * np.abs(fourier_values[1][0:n//2]), 'r')
    subplot.plot(xf, 2.0/n * np.abs(fourier_values[2][0:n//2]), 'b')
    subplot.grid()
    subplot.set_title('Fourier')

    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)


#
def plot_accelerations(unused_param):
    """
    Plot raw acceleration values and subtracted accleration values

    :param unused_param:
        parameter that is not used, needed in order to comply with matplotlib.animation interface
    :return:
    """

    if len(raw_acceleration_values) == 0 | len(subtracted_acceleration_values) == 0:
        return

    x_axis = np.linspace(1, data_quantity, data_quantity)

    subplot2.clear()
    subplot2.plot(x_axis, raw_acceleration_values[0], 'g')
    subplot2.plot(x_axis, raw_acceleration_values[1], 'r')
    subplot2.plot(x_axis, raw_acceleration_values[2], 'b')
    subplot2.grid()
    subplot2.set_ylim(-15, 15)

    subplot3.clear()
    subplot3.plot(x_axis, raw_acceleration_values2[0], 'g')
    subplot3.plot(x_axis, raw_acceleration_values2[1], 'r')
    subplot3.plot(x_axis, raw_acceleration_values2[2], 'b')
    subplot3.grid()
    subplot3.set_ylim(-15, 15)

    subplot4.clear()
    subplot4.plot(x_axis, subtracted_acceleration_values[0], 'g')
    subplot4.plot(x_axis, subtracted_acceleration_values[1], 'r')
    subplot4.plot(x_axis, subtracted_acceleration_values[2], 'b')
    subplot4.grid()
    subplot4.set_ylim(-15, 15)


def measurements_to_array(measurements):
    """
    Converts np.array() of Accel to np.array() of float values
    :param measurements:
    :return: np.array()
        the np.array() of float values
    """
    x = np.empty(0)
    y = np.empty(0)
    z = np.empty(0)
    for i in range(len(measurements)):
        x = np.append(x, measurements[i].x)
        y = np.append(y, measurements[i].y)
        z = np.append(z, measurements[i].z)
    return [x, y, z]


def initialization():
    """
    Get the matrices and start the data collection loop

    :return:
    """
    global time_last_calibration

    print("initializing")
    get_first_matrices()
    get_third_matrix()
    time_last_calibration = time.time()
    get_data_accelerometers()


def main():
    """
    Start the thread and the plotters

    :return:
    """
    thread.start_new_thread(initialization, ())
    """The function initialization starts in a new thread"""

    interval = 5000
    """Refresh time for the animation plotter. Extra 10 ms to ensure the update of the data."""

    ani = animation.FuncAnimation(fig, plot_fourier, fargs=([]), interval=interval)
    """Start the 1st plot animation"""

    ani2 = animation.FuncAnimation(fig2, plot_accelerations, fargs=([]), interval=interval)
    """Start the 2nd plot animation"""

    plt.show()


main()
