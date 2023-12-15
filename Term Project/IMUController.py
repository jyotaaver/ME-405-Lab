from IMU import *
import math
from utime import ticks
from utime import ticks_diff

class TaskAquirePositionGenFun:
    
    def __init__(self, left_mot_omega, right_mot_omega, x_position , y_position):
        
        self.imu = BNO055(1)
        self.left_speed = left_mot_omega
        self.right_speed = right_mot_omega
        self.x = x_position
        self.y = y_position
        self.init_yaw = self.imu.get_heading()
        self.x_pos = 0
        self.y_pos = 0
        self.speed = 0
        self.state = 1
        self.yaw = 0
        self.t1 = ticks()
        self.t2 = 0
        
    def velocity_calc(self):
        self.left_omega = self.left_speed.get()
        self.right_omega = self.right_speed.get()
        self.speed = (self.left_omega + self.right_omega) // 2
        return self.speed
    
    def yaw_calc(self):
        self.yaw = self.init_yaw - self.imu.get_heading()
    
    def calc_x_pos(self):
        self.x_pos += (ticks_diff(self.t2, self.t1)) * self.velocity_calc() * math.cos(math.radians(self.yaw_calc()))
        return self.x_pos
        
    def calc_y_pos(self):
        self.y_pos += (ticks_diff(self.t2, self.t1)) * self.velocity_calc() * math.sin(math.radians(self.yaw_calc()))
        return self.y_pos
        
    def Position_Out(self):
        
        while True:
            
            if self.state == 1:
                self.t2 = ticks()
                self.x.put(self.calc_x_position())
                self.y.put(self.calc_y_position())
                self.t1 = self.t2
                yield self.state                