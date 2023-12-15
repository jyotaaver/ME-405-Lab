from pyb import I2C
import time
from pyb import *

class BNO055:
    '''!@brief A driver class for to interface with a BNO055 sensor.
    @details Objects of this class can be used to configure the BNO055 sensor
    and retrieve data from it.
    '''
    def __init__(self, bus):
        self.address = 0x28
        self.opr_address = 0x3D
        self.calibration_address = 0x35
        self.config_mode = 0x00
        self.ndof_mode = 0x0C
        self.i2c = I2C(bus, I2C.CONTROLLER)
        self.buf = bytearray(1)
        self.buf2 = bytearray(1)
        self.sys = bytearray(2)
        self.data = bytearray(1)

        # Calibration true/false booleans
        self.sys_cal = 0
        self.gyr_cal = 0
        self.acc_cal = 0
        self.mag_cal = 0

        self.calibration_coefficients = []
        self.euler_angles = [0, 0, 0]
        self.angular_velocities = [0, 0, 0]

        # temp variables
        self.a = bytearray(1)
        self.b = bytearray(1)

        self.set_mode(self.config_mode)
        time.sleep(1)
        self.write_coeffs()
        time.sleep(1)
        self.set_mode(self.ndof_mode)
        time.sleep(1)

    def set_mode(self, addr):
        # method to change the operating mode of the IMU to one of the many
        # “fusion” modes available from the BNO055.
        self.i2c.mem_write(addr, self.address, self.opr_address)
        # use 0x08 for imu mode

    def calibrate(self):
        # method to retrieve the calibration status byte from the IMU and parse
        # it into its individual statuses.
        while True:
            self.read_calibration()

            if self.mag_cal == 3:
                if self.acc_cal == 3:
                    if self.gyr_cal == 3:
                        if self.sys_cal == 3:
                            print("Calibrated")
                            break

            print("\n\n\n\n\n\n")
            print("Not Calibrated")
            print("Mag_Cal: " + str(self.mag_cal))
            print("Acc_Cal: " + str(self.acc_cal))
            print("Gyr_Cal: " + str(self.gyr_cal))
            print("Sys_Cal: " + str(self.sys_cal))

            time.sleep(0.5)

        # read all values not just first for each calibration status.

    def read_calibration(self):
        self.i2c.mem_read(self.data, self.address, 0x35)
        for x in range(4):
            value = self.data[0] & (0b00000011 << x * 2)
            if x == 0:
                self.mag_cal = value >> x * 2
            elif x == 1:
                self.acc_cal = value >> x * 2
            elif x == 2:
                self.gyr_cal = value >> x * 2
            elif x == 3:
                self.sys_cal = value >> x * 2

    def read_coeffs(self):
        for i in range(0x55, 0x6B):
            self.i2c.mem_read(self.data, self.address, i)
            self.calibration_coefficients.append(self.data[0])

        with open("IMU_cal_coeffs.txt", "w") as file:
            coefficients_string = ""
            for byte in self.calibration_coefficients:
                coefficients_string += str(byte) + ", "
            file.write(coefficients_string)
            file.close()

        print("Coefficients: " + coefficients_string)
        self.calibration_coefficients = []

    def write_coeffs(self):
        with open("IMU_cal_coeffs.txt", "r") as file:
            self.calibration_coefficients = file.readline().split()
            file.close()

        print("Coefficients: " + str(self.calibration_coefficients))

        for i in range(0x55, 0x6B):
            self.i2c.mem_write(self.calibration_coefficients.pop(), self.address, i)
        self.calibration_coefficients = []

    def fix_axis(self):
        self.i2c.mem_write(0x24, self.address, 0x41)
        self.i2c.mem_write(0x06, self.address, 0x42)

    def read_angles(self):
        self.i2c.mem_write(0x00, self.address, 0x3B)

        self.euler_angles[0] = (self.i2c.mem_read(self.data, self.address, 0x1A)[0] |
                                self.i2c.mem_read(self.data, self.address, 0x1B)[0] << 8)/16
        self.euler_angles[1] = (self.i2c.mem_read(self.data, self.address, 0x1C)[0] |
                                self.i2c.mem_read(self.data, self.address, 0x1D)[0] << 8)/16
        self.euler_angles[2] = (self.i2c.mem_read(self.data, self.address, 0x1E)[0] |
                                self.i2c.mem_read(self.data, self.address, 0x1F)[0] << 8)/16

        if self.euler_angles[1] > 360:
            self.euler_angles[1] = 360 - (4096 - self.euler_angles[1])
        if self.euler_angles[2] > 360:
            self.euler_angles[2] = 360 - (4096 - self.euler_angles[2])

    def get_heading(self):
        self.read_angles()
        return self.euler_angles[0]
