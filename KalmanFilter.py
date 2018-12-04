import numpy as np
from transformations import Measurement

# Variables Used by Kalman Filters
DT = 0.1  # [s/loop] loop period. 100ms
Q_angle = 0.01
Q_gyro = 0.0003
R_angle = 0.01
x_bias = 0
y_bias = 0
z_bias = 0
XP_00 = 0
XP_01 = 0
XP_10 = 0
XP_11 = 0
YP_00 = 0
YP_01 = 0
YP_10 = 0
YP_11 = 0
ZP_00 = 0
ZP_01 = 0
ZP_10 = 0
ZP_11 = 0
KFangleX = 0.0
KFangleY = 0.0
KFangleZ = 0.0


def kalmanFilterX(accAngle, gyroRate, DT):
    """
            Applies kalman filter using current acceleration angle and gyro rotation rate in X axis.
            :param accAngle: float
                The acceleration angle
            :param gyroRate: float
                The angular velocity measured by gyroscope
            :return: float[]
                An array of kalman results
    """

    x = 0.0
    S = 0.0

    global KFangleX
    global Q_angle
    global Q_gyro
    global R_angle
    global x_bias
    global XP_00
    global XP_01
    global XP_10
    global XP_11

    KFangleX = KFangleX + DT * (gyroRate - x_bias)

    XP_00 = XP_00 + (- DT * (XP_10 + XP_01) + Q_angle * DT)
    XP_01 = XP_01 + (- DT * XP_11)
    XP_10 = XP_10 + (- DT * XP_11)
    XP_11 = XP_11 + (+ Q_gyro * DT)

    x = accAngle - KFangleX
    S = XP_00 + R_angle
    K_0 = XP_00 / S
    K_1 = XP_10 / S

    KFangleX = KFangleX + (K_0 * x)
    x_bias = x_bias + (K_1 * x)

    XP_00 = XP_00 - (K_0 * XP_00)
    XP_01 = XP_01 - (K_0 * XP_01)
    XP_10 = XP_10 - (K_1 * XP_00)
    XP_11 = XP_11 - (K_1 * XP_01)

    return KFangleX


def kalmanFilterY(accAngle, gyroRate, DT):
    """
            Applies kalman filter using current acceleration angle and gyro rotation rate in Y axis.
            :param accAngle: float
                The acceleration angle
            :param gyroRate: float
                The angular velocity measured by gyroscope
            :return: float[]
                An array of kalman results
    """

    y = 0.0
    S = 0.0

    global KFangleY
    global Q_angle
    global Q_gyro
    global R_angle
    global y_bias
    global YP_00
    global YP_01
    global YP_10
    global YP_11

    KFangleY = KFangleY + DT * (gyroRate - y_bias)

    YP_00 = YP_00 + (- DT * (YP_10 + YP_01) + Q_angle * DT)
    YP_01 = YP_01 + (- DT * YP_11)
    YP_10 = YP_10 + (- DT * YP_11)
    YP_11 = YP_11 + (+ Q_gyro * DT)

    y = accAngle - KFangleY
    S = YP_00 + R_angle
    K_0 = YP_00 / S
    K_1 = YP_10 / S

    KFangleY = KFangleY + (K_0 * y)
    y_bias = y_bias + (K_1 * y)

    YP_00 = YP_00 - (K_0 * YP_00)
    YP_01 = YP_01 - (K_0 * YP_01)
    YP_10 = YP_10 - (K_1 * YP_00)
    YP_11 = YP_11 - (K_1 * YP_01)

    return KFangleY


def kalmanFilterZ(accAngle, gyroRate, DT):
    """
        Applies kalman filter using current acceleration angle and gyro rotation rate in Z axis.
        :param accAngle: float
            The acceleration angle
        :param gyroRate: float
            The angular velocity measured by gyroscope
        :return: float[]
            An array of kalman results
    """

    z = 0.0
    S = 0.0

    global KFangleZ
    global Q_angle
    global Q_gyro
    global R_angle
    global z_bias
    global ZP_00
    global ZP_01
    global ZP_10
    global ZP_11

    KFangleZ = KFangleZ + DT * (gyroRate - z_bias)

    ZP_00 = ZP_00 + (- DT * (ZP_10 + ZP_01) + Q_angle * DT)
    ZP_01 = ZP_01 + (- DT * ZP_11)
    ZP_10 = ZP_10 + (- DT * ZP_11)
    ZP_11 = ZP_11 + (+ Q_gyro * DT)

    z = accAngle - KFangleZ
    S = ZP_00 + R_angle
    K_0 = ZP_00 / S
    K_1 = ZP_10 / S

    KFangleZ = KFangleZ + (K_0 * z)
    z_bias = z_bias + (K_1 * z)

    ZP_00 = ZP_00 - (K_0 * ZP_00)
    ZP_01 = ZP_01 - (K_0 * ZP_01)
    ZP_10 = ZP_10 - (K_1 * ZP_00)
    ZP_11 = ZP_11 - (K_1 * ZP_01)

    return KFangleZ


def apply_kalman_filter(accelerations, gyros):
    """
    Applies kalman filter to array of accelerations and gyros.
    :param accelerations: Measurements[]
        The array of Measurements to be subtracted
    :param gyros:
        The array of Measurements to be subtracted
    :return:Measurement[]
        An array of kalman results
    """

    global DT

    result = []
    for i in range(len(accelerations)):
        x = kalmanFilterX(getXAccAngle(accelerations[i].x), gyros[i].x, DT)
        y = kalmanFilterY(getYAccAngle(accelerations[i].y), gyros[i].y, DT)
        z = kalmanFilterZ(getZAccAngle(accelerations[i].z), gyros[i].z, DT)

        from transformations import Measurement
        result.append(Measurement(x, y, z))
    return result

def apply_single_kalman_filter(acceleration, gyro):
    """
    Applies kalman filter to a measurement of acceleration and gyro.
    :param accelerations: Measurements
        The acceleration Measurement
    :param gyros:
        The gyro Measurement
    :return:Measurement
        Kalman filter result
    """

    global DT
    x = kalmanFilterX(acceleration.x, gyro.x, DT)
    y = kalmanFilterY(acceleration.y, gyro.y, DT)
    z = kalmanFilterZ(acceleration.z, gyro.z, DT)

    return Measurement(x, y, z)


def getXAccAngle(accel):
    return np.arctan2(accel.x, np.sqrt((np.power(accel.y, 2) + np.power(accel.z, 2))))


def getYAccAngle(accel):
    return np.arctan2(accel.y, np.sqrt((np.power(accel.x, 2) + np.power(accel.z, 2))))


def getZAccAngle(accel):
    return np.arctan2(accel.z, np.sqrt((np.power(accel.x, 2) + np.power(accel.y, 2))))