import pyb
from pyb import Pin


class LimitSwitch:

    def __init__(self, signal_pin):
        """!@brief A class for the limit switch at the front of the romi
        @details Objects of this class can be used to apply PWM to a given
        DC motor on one channel of the L6206 from ST Microelectronics.
        @param signal_pin the pin that is used for the switch to send signals
        """
        self.pin = Pin(signal_pin, mode=Pin.IN)
        self.signal_pin = pyb.ADC(self.pin)

    def get_state(self):
        """!@brief A function that returns if the switch is currently pressed
        """
        if self.signal_pin.read() > 1000:
            return False
        else:
            return True
