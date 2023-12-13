from pyb import Timer
import pyb
from pyb import Pin
from array import array
from time import ticks_ms
from time import ticks_diff


class L6206:
    '''!@brief A driver class for one channel of the L6206.
    @details Objects of this class can be used to apply PWM to a given
    DC motor on one channel of the L6206 from ST Microelectronics.
    '''

    def __init__(self, pwm_tim, effort_pin, direction_pin, enable_pin, encoder, invert_flag):
        self.tim = Timer(pwm_tim, freq=20_000)
        self.effort_pin = Pin(effort_pin, mode=Pin.OUT_PP)
        self.direction_pin = Pin(direction_pin, mode=Pin.OUT_PP)
        self.enable_pin = Pin(enable_pin, mode=Pin.OUT_PP)
        self.duty_1 = 0
        self.duty_2 = 0
        self.pwm = self.tim.channel(2, pin=self.effort_pin, mode=Timer.PWM, pulse_width_percent=self.duty_1)
        self.invert_flag = invert_flag

        self.mot_positions = array('H', 500 * [0])
        self.mot_deltas = array('H', 500 * [0])
        self.enc = encoder
        self.tmp_position = 0
        self.current_error = 0
        self.prop_term = 0
        self.integral_term = 0
        self.derivative_term = 0
        self.speed = 0
        self.last_error = 0
        self.error_slope = 0
        self.sum = 0
        self.rpm_delta = 0
        self.duty = 0
        self.e_sum = 0
        self.kp_term = 0
        self.ki_term = 0
        self.k_total = 0
        self.freq = 0
        self.desired_speed = 0

        self.first_run = True
        self.freq = 0
        self.time_start = 0
        self.time_stop = 0

    def set_duty(self, duty):

        if self.invert_flag:
            if duty >= 0:
                if duty > 100:
                    duty = 100
                self.pwm.pulse_width_percent(100 - duty)
                self.direction_pin.low()
            else:
                if duty < -100:
                    duty = -100
                self.pwm.pulse_width_percent(100 + duty)
                self.direction_pin.high()
        else:
            if duty >= 0:
                self.pwm.pulse_width_percent(duty)
                self.direction_pin.low()
            else:
                self.pwm.pulse_width_percent(-duty)
                self.direction_pin.high()

    def set_speed(self, speed):
        self.desired_speed = speed

    def enable(self):
        self.enable_pin.high()

    def disable(self):
        self.enable_pin.low()

    def get_speed(self):
        return self.rpm_delta

    # def closed_loop(self,Kp,Ki,Kd,desired_speed,error,freq):
    def closed_loop(self, kp, ki, desired_speed):
        if self.first_run:
            self.enc.zero()
            self.time_start = ticks_ms()
            self.enc.update()
            self.first_run = False
        else:
            self.enc.update()
            self.time_stop = ticks_ms()
            self.freq = 1 / (ticks_diff(self.time_stop, self.time_start)) * 1000

            self.time_start = self.time_stop

            self.rpm_delta = self.enc.get_delta() * self.freq * 60 / 1440

            self.current_error = desired_speed - self.rpm_delta
            self.kp_term = -kp * self.current_error

            self.e_sum += self.current_error
            if self.e_sum > 500:
                self.e_sum = 500
            elif self.e_sum < -500:
                self.e_sum = -500

            self.ki_term = self.e_sum * -ki

            self.k_total = self.ki_term + self.kp_term

            self.duty = (self.k_total * 100 // (12 * 41))

            self.set_duty(self.duty)