import math

import numpy as np


def generateTransformationMatrices(accelX, accelY, accelZ, gyroX, gyroY, gyroZ):
    yMat = yTransform(accelX, accelZ)

    accelFirstTr = np.array([accelX,accelY,accelZ]).dot(yMat)
    #value of accelFirstTr in x is 0

    xMat = xTransform(accelFirstTr[1], accelFirstTr[2])

    accelSndTr = np.array([accelFirstTr[0], accelFirstTr[1], accelFirstTr[2]]).dot(xMat)
    #value of accelSndTr in x and y are 0

    gyroFirstTr = np.array([gyroX,gyroY,gyroZ ]).dot(yMat)
    gyroSndTr = np.array([gyroFirstTr[0],gyroFirstTr[1],gyroFirstTr[2]]).dot(xMat)

    zMat = zTransform(gyroSndTr[0], gyroSndTr[1])

    return [xMat,yMat,zMat]


def applyTransformations(accels, matrices):
    accelFirstTr = np.array([accels[0], accels[1], accels[2]]).dot(matrices[1])
    accelSndTr = np.array([accelFirstTr[0], accelFirstTr[1], accelFirstTr[2]]).dot(matrices[0])
    return accelSndTr

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


# receives the angular velocity components of x and y after two rotations
# returns Rz matrix for the third transformation
def zTransform(gyroX, gyroY):
    alpha = np.arctan2(gyroX, gyroY)
    return np.array([[np.cos(alpha), np.sin(alpha), 0], [-np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])


# generateTransformationMatrices(-2.2, 4.4, 8.5, 0,0,0)
