import math

import numpy as np


def generate_two_matrices(accelX, accelY, accelZ):
    yMat = yTransform(accelX, accelZ)

    accelFirstTr = np.array([accelX,accelY,accelZ]).dot(yMat)
    #value of accelFirstTr in x is 0

    xMat = xTransform(accelFirstTr[1], accelFirstTr[2])

    return [xMat,yMat]


def applyTransformations(accels, matrices):
    accelFirstTr = np.array([accels[0], accels[1], accels[2]]).dot(matrices[1])
    accelSndTr = np.array([accelFirstTr[0], accelFirstTr[1], accelFirstTr[2]]).dot(matrices[0])
    accelThirdTr = np.array([accelSndTr[0], accelSndTr[1], accelSndTr[2]]).dot(matrices[2])
    return accelThirdTr

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


# receives the acceleration of the two sensors after two rotations
# returns Rz matrix for the third transformation of the Accelerometer 1
# to make the last transform accel1 * Rz
def zTransform(acelX1, acelY1, acelX2, acelY2):
    alpha = np.arctan2(acelX1*acelY2 - acelX2*acelY1, acelX1*acelX2 + acelY1*acelY2)
    return np.array([[np.cos(alpha), np.sin(alpha), 0], [-np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])


# generateTransformationMatrices(-2.2, 4.4, 8.5, 0,0,0)
