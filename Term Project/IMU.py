from pyb import I2C
import time
from pyb import *

class BNO055:
    """A driver class to interface with a BNO055 sensor.
    
    Objects of this class can be used to configure the BNO055 sensor
    and retrieve data from it.
    
    Args:
        bus: The I2C bus that the I2C device is on
    """
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
        """ A method that sets the BNO055 into the fusion/9DOF modes that we desire
        """
        self.i2c.mem_write(addr, self.address, self.opr_address) # use 0x08 for imu mode

    def calibrate(self):
        """ A method that outputs the IMU/BNO055 to a user interface for debugging
        """
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
        """ A method that reads the calibration status of the IMU/BNO055
        """
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
        """ A method that reads the calibration coefficients of the several 
        sensors composing the IMU/BNO055, and writing them to a text file
        """
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
        """ A method that writes the calibration coefficients of the 
        IMU in order to avoid the need for recalibration
        """
        with open("IMU_cal_coeffs.txt", "r") as file:
            self.calibration_coefficients = file.readline().split()
            file.close()

        print("Coefficients: " + str(self.calibration_coefficients))

        for i in range(0x55, 0x6B):
            self.i2c.mem_write(self.calibration_coefficients.pop(), self.address, i)
        self.calibration_coefficients = []

    def fix_axis(self):
        """ A method that sets the appropriate axis for the IMU
        """
        self.i2c.mem_write(0x24, self.address, 0x41)
        self.i2c.mem_write(0x06, self.address, 0x42)

    def read_angles(self):
        """ A method that reads the roll,pitch, and yaw angles of the IMU
        
        Once the MSB and LSB of the 3 euler angles have been concatenated, they are stored in the attribute 
        self.euler_angles
        """
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
        """ A method that outputs the yaw angle of the IMU, in relation to North
        
        Reads new euler angles of the IMU, and outputs them for use elsewhere
        
        Returns:
            The new yaw angle of Romi in Degrees
        """
        self.read_angles()
        return self.euler_angles[0]
