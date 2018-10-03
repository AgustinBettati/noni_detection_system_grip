from scipy.fftpack import fft
import numpy as np


def apply_fourier_x(accels):
    x_values = np.empty((0, len(accels)))
    for acel in accels:
        x_values = np.append(x_values, [acel.x])
    return fft(x_values)


def apply_fourier_y(accels):
    y_values = np.empty((0, len(accels)))
    for acel in accels:
        y_values = np.append(y_values, [acel.y])
    return fft(y_values)


def apply_fourier_z(accels):
    z_values = np.empty((0, len(accels)))
    for acel in accels:
        z_values = np.append(z_values, [acel.z])
    return fft(z_values)

# Cool Functional way of doing it. Could not make it work
# def apply_fourier_y(accels):
#     y_values = map(lambda acel: acel.y, accels)
#     return fft(y_values)