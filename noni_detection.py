import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import thread
import datetime as datetime
from MPU6050 import MPU6050
from time import sleep
from transformations import apply_first_transformation, generate_two_matrices, \
    apply_all_transformations, z_transform, Accel
from fourier import apply_fourier

# Create a new instance of the MPU6050 class
sensor = MPU6050(0x68)
sensor2 = MPU6050(0x69)

# Variables for ploting
fig = plt.figure()
subplot = fig.add_subplot(1, 1, 1)

# Matrices
x_mat = np.empty(0)
y_mat = np.empty(0)
z_mat = np.empty(0)
x_mat2 = np.empty(0)
y_mat2 = np.empty(0)

# Quantity of values to calculate the third matrix
third_matrix_values = 100
# Interval between two accelerations when calculating the third matrix
third_matrix_interval = 0.2

# Interval between two accelerations in seconds
frequency = 0.25

# Quantity of accelerations to get before doing fourier
data_quantity = 100

# Values after Fourier
fourier_values = np.empty(0)


# Main method. Generates the matrices and then enters a loop and start getting the accelerometer values
def get_data_accelerometers():
    global fourier_values
    print ("start getting accelerations")
    quantity = 0
    acceleration_values1 = []
    acceleration_values2 = []

    while quantity < data_quantity:
        now = datetime.datetime.now()
        acceleration_values1.append(get_data_accelerometer1())
        acceleration_values2.append(get_data_accelerometer2())
        sleep(frequency - (datetime.datetime.now() - now).seconds)
        quantity += 1
    accelerations = subtract_accels(acceleration_values1, acceleration_values2)
    print ("accelerations subtracted, making fourier")
    fourier = apply_fourier(accelerations)
    fourier_values = fourier[0]
    print ("finish fourier")
    get_data_accelerometers()


# print accelerations, just for testing purposes
def print_accelerations(accels):
    for i in range(len(accels)):
        print ("x: ")
        print(accels[i].x)
        print (", y: ")
        print (accels[i].y)
        print (", z: ")
        print (accels[i].z)
        print ("\n")


# Subtract one array of acceleration with another one
def subtract_accels(accel1, accel2):
    accel = []
    for i in range(len(accel1)):
        x = accel1[i].x - accel2[i].x
        y = accel1[i].y - accel2[i].y
        z = accel1[i].z - accel2[i].z

        accel.append(Accel(x, y, z))
    return accel


# defines the matrix z for the sensor 1 and sensor 2
def get_third_matrix():
    global z_mat
    print("getting third matrix, please move the accelerometers")
    quantity = 0
    data_accelerometer = []
    data_accelerometer2 = []
    while quantity < third_matrix_values:
        data_accelerometer.append(apply_first_transformation(get_accel(sensor), [x_mat, y_mat]))
        data_accelerometer2.append(apply_first_transformation(get_accel(sensor2), [x_mat2, y_mat2]))
        quantity += 1
        sleep(third_matrix_interval)
    print(quantity)
    z_mat = z_transform(data_accelerometer, data_accelerometer2)
    print("Obtained third matrix")


# defines matrix x and matrix y for the sensor 1 and 2
def get_first_matrices():
    global x_mat, y_mat, x_mat2, y_mat2

    accel = get_accel(sensor)
    accel2 = get_accel(sensor2)

    matrices = generate_two_matrices(accel)
    x_mat = matrices[0]
    y_mat = matrices[1]

    matrices2 = generate_two_matrices(accel2)
    x_mat2 = matrices2[0]
    y_mat2 = matrices2[1]
    print("Obtained first two matrices")


# Rotate the acceleration values from the sensor 1 and appends them to the acceleration_values.
def get_data_accelerometer1():

    global x_mat, y_mat, z_mat

    accel = get_accel(sensor)

    values_rotated = apply_all_transformations(accel, [x_mat, y_mat, z_mat])

    return Accel(values_rotated.x, values_rotated.y, values_rotated.z)


# Rotate the acceleration values from the sensor 2 and appends them to the acceleration_values.
def get_data_accelerometer2():
    global x_mat2, y_mat2

    accel = get_accel(sensor2)

    values_rotated = apply_first_transformation(accel, [x_mat2, y_mat2])

    return Accel(values_rotated.x, values_rotated.y, values_rotated.z)


# Get the acceleration values from a specific sensor
def get_accel(custom_sensor):
    accel_data = custom_sensor.get_accel_data()
    return Accel(accel_data['x'], accel_data['y'], accel_data['z'])


# Plot fourier of segment of data
def plot_fourier(unused_param):
    global fourier_values

    if len(fourier_values) == 0 :
        return

    # Number of sample points
    n = fourier_values.size
    # or N = fourier_segment_length, ie N = 600

    # sample spacing
    t = 1.0 / frequency

    # returns evenly spaced numbers from 0 to N, with n*t increments. (try instead of xf)
    x = np.linspace(0.0, n * t, n)

    # no idea what this does, why not use x?
    xf = np.linspace(0.0, 1.0 / (2.0 * t), n // 2)
    
    subplot.clear()
    subplot.plot(xf, 2.0/n * np.abs(fourier_values[0:n//2]), 'g')
    subplot.grid()

    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Fourier')
    plt.ylabel('g')


# Get the matrices and start the data collection loop
def initialization():
    print("initializing")
    get_first_matrices()
    get_third_matrix()
    get_data_accelerometers()


# Start the thread and the plotters
def main():
    # the function initialization start in a new thread
    thread.start_new_thread(initialization, ())

    # refresh time for the animation plotter. Extra 10 ms to ensure the update of the data.
    interval = 5000

    # start the plot animation
    ani = animation.FuncAnimation(fig, plot_fourier, fargs=([]), interval=interval)
    plt.show()


main()
