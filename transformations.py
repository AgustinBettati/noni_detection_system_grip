import math

import numpy as np
from noni_detection import Accel


def generate_two_matrices(accel):
    yMat = yTransform(accel.x, accel.z)

    accelFirstTr = np.array([accel.x,accel.y,accel.z]).dot(yMat)
    #value of accelFirstTr in x is 0

    xMat = xTransform(accelFirstTr[1], accelFirstTr[2])

    return [xMat, yMat]


def apply_first_transformation(accels, matrices):
    accel_first_tr = np.array([accels.x, accels.y, accels.z]).dot(matrices[1])
    accel_snd_tr = np.array([accel_first_tr[0], accel_first_tr[1], accel_first_tr[2]]).dot(matrices[0])
    return Accel(accel_snd_tr[0], accel_snd_tr[1], accel_snd_tr[2])


def apply_all_transformations(accels, matrices):
    accel_first_tr = np.array([accels.x, accels.y, accels.z]).dot(matrices[1])
    accel_snd_tr = np.array([accel_first_tr[0], accel_first_tr[1], accel_first_tr[2]]).dot(matrices[0])
    accel_third_tr = np.array([accel_snd_tr[0], accel_snd_tr[1], accel_snd_tr[2]]).dot(matrices[2])
    return Accel(accel_third_tr[0], accel_third_tr[1], accel_third_tr[2])


# recieves the initial acceleration values of x and y
# returns Ry matrix for the first transformation
def yTransform(acelX, acelZ):
    alpha = np.arctan2(acelX, acelZ)
    return np.array([[np.cos(alpha), 0, np.sin(alpha)], [0, 1, 0], [-np.sin(alpha), 0, np.cos(alpha)]])


# recieves the acceleration of y and z after first transformation, x is cero at this point
# returns Rx matrix for the second transformation
def xTransform(acelY, acelZ):
    beta = np.arctan2(acelY, acelZ)
    return np.array([[1, 0, 0], [0, np.cos(beta), np.sin(beta)], [0, -np.sin(beta), np.cos(beta)]])


# receives the accelerations of the two sensors after two rotations
# returns Rz matrix for the third transformation of the Accelerometer 1
# to make the last transform accel1 * Rz
def zTransform(firstSensorValues, secondSensorValues):
    alphaValues = []

    for i in range (len(firstSensorValues)):
        accel1 = firstSensorValues[i]
        accel2 = secondSensorValues[i]

        alpha = np.arctan2(accel1.x * accel2.y - accel2.x * accel1.y, accel1.x * accel2.x + accel1.y * accel2.y)
        alphaValues.append(alpha)

    alpha = sum(alphaValues) / len(alphaValues)
    return np.array([[np.cos(alpha), np.sin(alpha), 0], [-np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])


# print( zTransform( [Accel(5,7.6,20.5),Accel(30.5,1.6,56.5)], [Accel(39.5,2.6,0.5), Accel(22.5,88.6,54.5)]) )