import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import thread
import datetime as datetime

from KalmanFilter import apply_kalman_filter, apply_single_kalman_filter
from MPU6050 import MPU6050
from time import sleep
import time
from transformations import apply_first_transformation, generate_two_matrices, \
    apply_all_transformations, z_transform, Measurement
from fourier import apply_fourier
from websocket_client import send_measurements, send_fourier

sensor = MPU6050(0x68)
"""Creates a new instance of the MPU6050 class for the first sensor"""
sensor2 = MPU6050(0x69)
"""Creates a new instance of the MPU6050 class for the second sensor"""

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

data_quantity = 150
"""Quantity of accelerations to get before doing fourier"""

fourier_values = np.empty(0)
"""Values for plotting fourier"""

fourier_x_axis = []
"""X axis values for plotting fourier"""

fourier_values_kalman = np.empty(0)
"""Kalman values for plotting fourier"""

acceleration_values = np.empty(0)
"""Values for plotting raw accelerations"""

gyro_values1 = np.empty(0)
"""Values for plotting raw acceleration"""

kalman_values = np.empty(0)  # kalman_values is never used
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
    global fourier_values, fourier_values_kalman, time_last_calibration, acceleration_values, gyro_values1, kalman_values  # kalman_values is never used
    print("start getting accelerations")
    quantity = 0
    subtracted_accelerations = []
    subtracted_gyros = []
    kalman_results = []

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
            time_last_calibration = time.time()
            get_data_accelerometers()
        sleep(interval - (datetime.datetime.now() - now).seconds)
        quantity += 1

        subtracted_acceleration = accel1.subtract(accel2)
        subtracted_accelerations.append(subtracted_acceleration)
        subtracted_gyro = gyro1.subtract(gyro2)
        subtracted_gyros.append(subtracted_gyro)
        kalman_result = apply_single_kalman_filter(subtracted_acceleration, subtracted_gyro)
        kalman_results.append(kalman_result)

        send_measurements(subtracted_acceleration, gyro1, gyro2, kalman_result)

    print("accelerations subtracted, making fourier")
    fourier_values = apply_fourier(subtracted_accelerations)
    fourier_values_kalman = apply_fourier(kalman_results)
    fourier_x_axis = get_fourier_x_axis()
    send_fourier(fourier_values, fourier_values_kalman, fourier_x_axis)
    print("finish fourier")
    get_data_accelerometers()


def get_fourier_x_axis():
    """
        Get fourier x axis based on size and interval.

        :param
        :return: void
    """

    global fourier_x_axis

    n = data_quantity
    """Number of sample points"""

    t = interval
    """Sample spacing"""

    fourier_x_axis = np.linspace(0.0, 1.0 / (2.0 * t), n // 2).tolist()
    """Equally distributed frequency values"""



def print_accelerations(accels):
    """
    Prints accelerations, just for testing purposes
    :param accels: Measurement[]
        The list of accelerations to be printed
    :return:void
    """
    for i in range(len(accels)):
        print("x: ")
        print(accels[i].x)
        print(", y: ")
        print(accels[i].y)
        print(", z: ")
        print(accels[i].z)
        print("\n")


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
    :return: Measurement
        The acceleration rotated
    """
    global x_mat, y_mat, z_mat

    accel = get_accel(sensor)

    values_rotated = apply_all_transformations(accel, [x_mat, y_mat, z_mat])

    return Measurement(values_rotated.x, values_rotated.y, values_rotated.z)


def get_data_accelerometer2():
    """
    Rotates the acceleration values from the sensor 2 and appends them to the acceleration_values.
    :return: Measurement
        The acceleration rotated
    """
    global x_mat2, y_mat2

    accel = get_accel(sensor2)

    values_rotated = apply_first_transformation(accel, [x_mat2, y_mat2])

    return Measurement(values_rotated.x, values_rotated.y, values_rotated.z)


def get_data_gyro1():
    """
    Rotates the gyro values from the sensor 1.
    :return: Measurement
        The gyro values rotated
    """
    global x_mat, y_mat, z_mat

    gyro = get_gyro(sensor)

    values_rotated = apply_all_transformations(gyro, [x_mat, y_mat, z_mat])

    return Measurement(values_rotated.x, values_rotated.y, values_rotated.z)


def get_data_gyro2():
    """
    Rotates the gyro values from the sensor 2.
    :return: Measurement
        The gyro values rotated
    """
    global x_mat2, y_mat2

    gyro = get_gyro(sensor2)

    values_rotated = apply_first_transformation(gyro, [x_mat2, y_mat2])

    return Measurement(values_rotated.x, values_rotated.y, values_rotated.z)


def get_accel(custom_sensor):
    """
    Gets the acceleration values from a specific sensor
    :param custom_sensor: MPU6050
        The sensor from where the accelerations will be taken.
    :return: Measurement
        The acceleration sensed
    """
    accel_data = custom_sensor.get_accel_data()
    return Measurement(accel_data['x'], accel_data['y'], accel_data['z'])


def get_gyro(custom_sensor):
    """
    Gets the acceleration values from a specific sensor
    :param custom_sensor: MPU6050
        The sensor from where the accelerations will be taken.
    :return: Measurement
        The Gyroscope sensed
    """
    gyro_data = custom_sensor.get_gyro_data()
    return Measurement(gyro_data['x'], gyro_data['y'], gyro_data['z'])


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
    get_fourier_x_axis()
    get_data_accelerometers()


initialization()
