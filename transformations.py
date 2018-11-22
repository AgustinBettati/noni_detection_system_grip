import math

import numpy as np


class Measurments:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def module(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def subtract(self, accel):
        return Accel(self.x - accel.x, self.y - accel.y, self.z - accel.z)


def generate_two_matrices(accel):
    """
    generates matrices y and x. these acceleration must be obtained when no movement is present.
    :param accel: Accel
        initial accelerations
    :return: array of multi arrays
    """
    y_mat = y_transform(accel.x, accel.z)

    accel_first_tr = np.array([accel.x, accel.y, accel.z]).dot(y_mat)
    # value of accelFirstTr in x is 0

    x_mat = x_transform(accel_first_tr[1], accel_first_tr[2])

    return [x_mat, y_mat]


def apply_first_transformation(accels, matrices):
    """
    applies transformation using only the first two matrices(y and x)
    :param accels: Accel
        initial acceleration of sensor
    :param matrices: np.array()
        contains all three matrices
    :return:
        returns acceleration after applying y and x transformations
    """
    accel_first_tr = np.array([accels.x, accels.y, accels.z]).dot(matrices[1])
    accel_snd_tr = np.array([accel_first_tr[0], accel_first_tr[1], accel_first_tr[2]]).dot(matrices[0])
    return Measurments(accel_snd_tr[0], accel_snd_tr[1], accel_snd_tr[2])


def apply_all_transformations(accels, matrices):
    """
    applies transformations to acceleration using the 3 matrices
    :param accels: Accel
        initial accelerations of sensor
    :param matrices: np.array()
        contains all three matrices
    :return: Accel
        returns the acceleration after 3 rotations
    """
    accel_first_tr = np.array([accels.x, accels.y, accels.z]).dot(matrices[1])
    accel_snd_tr = np.array([accel_first_tr[0], accel_first_tr[1], accel_first_tr[2]]).dot(matrices[0])
    accel_third_tr = np.array([accel_snd_tr[0], accel_snd_tr[1], accel_snd_tr[2]]).dot(matrices[2])
    return Measurments(accel_third_tr[0], accel_third_tr[1], accel_third_tr[2])


def y_transform(accel_x, accel_z):
    """
    generates the y matrix, these acceleration must be obtained when no movement is present.
    this matrix is used to make the first transformation to both sensors.
    :param accel_x: Float
        initial acceleration in x
    :param accel_z: Float
        initial acceleration in z
    :return: np.array()
        a multiarray that contains the y matrix
    """
    alpha = np.arctan2(accel_x, accel_z)
    return np.array([[np.cos(alpha), 0, np.sin(alpha)], [0, 1, 0], [-np.sin(alpha), 0, np.cos(alpha)]])


def x_transform(accel_y, accel_z):
    """
    generates the x matrix from acceleration values after first transformation.
    this matrix is used to make the second transformation to both sensors.
    :param accel_y: Float
        acceleration in y after first transformation
    :param accel_z: Float
        acceleration in z after first transformation
    :return: np.array()
        a multiarray that contains the x matrix
    """
    beta = np.arctan2(accel_y, accel_z)
    return np.array([[1, 0, 0], [0, np.cos(beta), np.sin(beta)], [0, -np.sin(beta), np.cos(beta)]])


def z_transform(first_sensor_values, second_sensor_values):
    """
    generates the z matrix from a list of the first and second sensor values after the have been in x and y.
    this matrix is used to make the third transformation to one of the sensors in order to adjust orientation.
    :param first_sensor_values: Accel[]
        accelerations of the first sensor after two rotations
    :param second_sensor_values: Accel[]
        accelerations of the second sensor after two rotations
    :return: np.array()
        a multiarray that contains the z matrix
    """
    alpha_values = []

    for i in range(len(first_sensor_values)):
        accel1 = first_sensor_values[i]
        accel2 = second_sensor_values[i]

        alpha = np.arctan2(accel1.x * accel2.y - accel2.x * accel1.y, accel1.x * accel2.x + accel1.y * accel2.y)
        alpha_values.append(alpha)

    alpha = sum(alpha_values) / len(alpha_values)
    return np.array([[np.cos(alpha), np.sin(alpha), 0], [-np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])
