import math

import numpy as np


def generateTransformationMatrices(accelX, accelY, accelZ, gyroX, gyroY, gyroZ):
    yMat = yTransform(accelX, accelZ)

    accelFirstTr = yMat.dot(np.array([accelX,accelY,accelZ]))
    #value of accelFirstTr in y must be 0

    xMat = xTransform(accelFirstTr[1], accelFirstTr[2])

    accelSndTr = xMat.dot(np.array([accelFirstTr[0], accelFirstTr[1], accelFirstTr[2] ]))
    #value of accelSndTr in x and y should be 0

    gyroFirstTr = yMat.dot( np.array([gyroX,gyroY,gyroZ ]))
    gyroSndTr = xMat.dot( np.array([gyroFirstTr[0],gyroFirstTr[1],gyroFirstTr[2] ]))

    zMat = zTransform(gyroSndTr[0], gyroSndTr[1])




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

