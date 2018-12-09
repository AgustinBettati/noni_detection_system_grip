from scipy.fftpack import fft
import numpy as np


def apply_fourier(accels):
    """
    Applies fourier to Acceleration

    :param accels: np.array()
        acceleration values to apply fourier to
    :return: python list
        A python list where:
        [0]: fourier of the x values of accels
        [1]: fourier of the y values of accels
        [2]: fourier of the z values of accels
    """
    x_values = []
    y_values = []
    z_values = []

    for accel in accels:
        x_values.append(accel.x)
        y_values.append(accel.y)
        z_values.append(accel.z)
    return [fft(x_values).tolist(), fft(y_values).tolist(), fft(z_values).tolist()]


def apply_fourier_x(accels):
    """
    Applies fourier to x values of Measurement

    :param accels: np.array()
    :return: np.array()
    """
    x_values = np.empty((0, len(accels)))
    for accel in accels:
        x_values = np.append(x_values, [accel.x])
    return fft(x_values)


def apply_fourier_y(accels):
    """
    Applies fourier to y values of Measurement

    :param accels:Measurement
    :return: np.array()
    """

    y_values = np.empty((0, len(accels)))
    for accel in accels:
        y_values = np.append(y_values, [accel.y])
    return fft(y_values)


def apply_fourier_z(accels):
    """
    Applies fourier to z values of Measurement

    :param accels: np.array()
    :return: np.array()
    """

    z_values = np.empty((0, len(accels)))
    for accel in accels:
        z_values = np.append(z_values, [accel.z])
    return fft(z_values)

# Cool Functional way of doing it. Could not make it work
# def apply_fourier_y(accels):
#     y_values = map(lambda acel: acel.y, accels)
#     return fft(y_values)
