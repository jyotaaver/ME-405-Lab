from pyb import Timer
import pyb
from pyb import Pin
from array import array
from time import ticks_ms
from time import ticks_diff


class LimitSwitch:
    '''!@brief A driver class for one channel of the L6206.
    @details Objects of this class can be used to apply PWM to a given
    DC motor on one channel of the L6206 from ST Microelectronics.
    '''

    def __init__(self, signal_pin):
        self.pin = Pin(signal_pin, mode=Pin.IN)
        self.signal_pin = pyb.ADC(self.pin)

        # self.power_pin.high()

    def get_state(self):
        if self.signal_pin.read() > 1000:
            return False
        else:
            return True
