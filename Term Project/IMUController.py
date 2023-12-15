from IMU import *
import math
from utime import ticks_diff
from utime import ticks_ms


class TaskAcquirePositionGenFun:
    
    def __init__(self, left_mot_omega, right_mot_omega, x_position, y_position, blue_button):
        """A generator function class to determine the current position of the Romi at all times.

        Will Stop and start collecting data between presses of the blue button. The purpose of this task is to store the
        current x and y positions into shares that RomiControl can use to determine how to get back to the start position
        from the end position. Positions are collected in units of cm.

        Args:
            left_mot_omega: share used to store the angular motor speed of the left motor
            right_mot_omega: share used to store the angular motor speed of the right motor
            x_position: share used to store the current x position of the Romi
            y_position: share used to store the current y position of the Romi
            blue_button: signal flag to set collecting data to true or false.
        """
        
        self.imu = BNO055(1)
        self.left_speed_data = left_mot_omega
        self.right_speed_data = right_mot_omega
        self.x = x_position
        self.y = y_position
        self.init_yaw = self.imu.get_heading()
        self.x_pos = 0
        self.y_pos = 0
        self.speed = 0
        self.state = 1
        self.yaw = 0
        self.t1 = ticks_ms()
        self.t2 = 0
        self.left_omega = 0
        self.right_omega = 0
        self.heading_offset = self.imu.get_heading()

        self.set_init_yaw()

        self.blue_button_flag = blue_button

    def set_init_yaw(self):
        self.init_yaw = self.imu.get_heading()

    def velocity_calc(self):
        """Determines the velocity of the Romi based upon the angular velocity of the two wheels.

        Returns:
            The speed of the Romi in cm / s

        """
        self.left_omega = self.left_speed_data.get()
        self.right_omega = self.right_speed_data.get()
        self.speed = -1 * (self.left_omega + self.right_omega) * (math.pi * (7 / 2)**2 * 60) / 2 / 1000
        return self.speed
    
    def yaw_calc(self):
        """Determines the current yaw of the robot relative to the starting position.

        Returns:
             the final yaw in radians
        """
        self.yaw = self.init_yaw - self.imu.get_heading()
        if self.yaw < 0:
            self.yaw = 360 - self.yaw
        self.yaw = self.imu.get_heading()
        return math.radians(self.yaw)

    def calc_x_pos(self):
        """ Calculates the new x position based upon the change in time, yaw, and velocity of romi

        Once the new x position is calculated, it is stored into the attribute self.x_pos

        Returns:
            The new x position of the Romi
        """
        self.x_pos += (ticks_diff(self.t2, self.t1)) * self.velocity_calc() * math.cos(self.yaw_calc()) / 1000
        return self.x_pos
        
    def calc_y_pos(self):
        """ Calculates the new y position based upon the change in time, yaw, and velocity of Romi

            Once the new y position is calculated, it is stored into the attribute self.y_pos

        Returns:
            The new y position of the Romi
        """
        self.y_pos += (ticks_diff(self.t2, self.t1)) * self.velocity_calc() * math.sin(self.yaw_calc()) / 1000
        return self.y_pos
        
    def run(self):
        """ Generator function to continuously determine the position of the Romi as it traverses the track.

        Pressing the blue button toggles if data gets collected by this task.
        """
        
        while True:

            if self.blue_button_flag.get() == 1:
            
                if self.state == 1:
                    self.t2 = ticks_ms()
                    self.x.put(self.calc_x_pos())
                    self.y.put(self.calc_y_pos())
                    self.t1 = self.t2

                # print("\n\n\n")
                # print(self.x.get())
                # print(self.y.get())
                # print(self.speed)
                # print(self.yaw)
            else:
                self.x_pos = 0
                self.y_pos = 0

            yield self.state
