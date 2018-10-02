from scipy.fftpack import fft


def apply_fourier_x(accels):
    x_values = map(lambda acel : acel.x, accels)
    return fft(x_values)


def apply_fourier_y(accels):
    y_values = map(lambda acel: acel.y, accels)
    return fft(y_values)


def apply_fourier_z(accels):
    z_values = map(lambda acel: acel.z, accels)
    return fft(z_values)