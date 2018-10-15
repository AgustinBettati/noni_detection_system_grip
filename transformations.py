import math

import numpy as np


class Accel:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def module(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2


def generate_two_matrices(accel):
    y_mat = y_transform(accel.x, accel.z)

    accel_first_tr = np.array([accel.x, accel.y, accel.z]).dot(y_mat)
    # value of accelFirstTr in x is 0

    x_mat = x_transform(accel_first_tr[1], accel_first_tr[2])

    return [x_mat, y_mat]


def apply_first_transformation(accels, matrices):
    accel_first_tr = np.array([accels.x, accels.y, accels.z]).dot(matrices[1])
    accel_snd_tr = np.array([accel_first_tr[0], accel_first_tr[1], accel_first_tr[2]]).dot(matrices[0])
    return Accel(accel_snd_tr[0], accel_snd_tr[1], accel_snd_tr[2])


def apply_all_transformations(accels, matrices):
    accel_first_tr = np.array([accels.x, accels.y, accels.z]).dot(matrices[1])
    accel_snd_tr = np.array([accel_first_tr[0], accel_first_tr[1], accel_first_tr[2]]).dot(matrices[0])
    accel_third_tr = np.array([accel_snd_tr[0], accel_snd_tr[1], accel_snd_tr[2]]).dot(matrices[2])
    return Accel(accel_third_tr[0], accel_third_tr[1], accel_third_tr[2])


# receives the initial acceleration values of x and y
# returns Ry matrix for the first transformation
def y_transform(accel_x, accel_z):
    alpha = np.arctan2(accel_x, accel_z)
    return np.array([[np.cos(alpha), 0, np.sin(alpha)], [0, 1, 0], [-np.sin(alpha), 0, np.cos(alpha)]])


# receives the acceleration of y and z after first transformation, x is cero at this point
# returns Rx matrix for the second transformation
def x_transform(accel_y, accel_z):
    beta = np.arctan2(accel_y, accel_z)
    return np.array([[1, 0, 0], [0, np.cos(beta), np.sin(beta)], [0, -np.sin(beta), np.cos(beta)]])


# receives the accelerations of the two sensors after two rotations
# returns Rz matrix for the third transformation of the Accelerometer 1
# to make the last transform accel1 * Rz
def z_transform(first_sensor_values, second_sensor_values):
    alpha_values = []

    for i in range(len(first_sensor_values)):
        accel1 = first_sensor_values[i]
        accel2 = second_sensor_values[i]

        alpha = np.arctan2(accel1.x * accel2.y - accel2.x * accel1.y, accel1.x * accel2.x + accel1.y * accel2.y)
        alpha_values.append(alpha)

    alpha = sum(alpha_values) / len(alpha_values)
    return np.array([[np.cos(alpha), np.sin(alpha), 0], [-np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])

# print( zTransform( [Accel(5,7.6,20.5),Accel(30.5,1.6,56.5)], [Accel(39.5,2.6,0.5), Accel(22.5,88.6,54.5)]) )
