from scipy.fftpack import fft
import numpy as np


def apply_fourier(accels):
    """
    Applies fourier to Acceleration

    :param accels: np.array()
        acceleration values to apply fourier to
    :return: np.array()
        numpy array of the transformed acceleration values
    """
    x_values = np.empty((0, len(accels)))
    y_values = np.empty((0, len(accels)))
    z_values = np.empty((0, len(accels)))

    for accel in accels:
        x_values = np.append(x_values, [accel.x])
        y_values = np.append(y_values, [accel.y])
        z_values = np.append(z_values, [accel.z])
    return [fft(x_values), fft(y_values), fft(z_values)]


def apply_fourier_x(accels):
    """
    Applies fourier to x values of Accel

    :param accels:
    :return:
    """
    x_values = np.empty((0, len(accels)))
    for accel in accels:
        x_values = np.append(x_values, [accel.x])
    return fft(x_values)


def apply_fourier_y(accels):
    y_values = np.empty((0, len(accels)))
    for accel in accels:
        y_values = np.append(y_values, [accel.y])
    return fft(y_values)


def apply_fourier_z(accels):
    z_values = np.empty((0, len(accels)))
    for accel in accels:
        z_values = np.append(z_values, [accel.z])
    return fft(z_values)

# Cool Functional way of doing it. Could not make it work
# def apply_fourier_y(accels):
#     y_values = map(lambda acel: acel.y, accels)
#     return fft(y_values)
