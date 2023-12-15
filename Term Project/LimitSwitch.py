import pyb
from pyb import Pin


class LimitSwitch:

    def __init__(self, signal_pin):
        """A class for the limit switch at the front of the romi
        
        Objects of this class can be used to apply PWM to a given
        DC motor on one channel of the L6206 from ST Microelectronics.
        
        Args:
            signal_pin: the pin that is used for the switch to send signals
        """
        self.pin = Pin(signal_pin, mode=Pin.IN)
        self.signal_pin = pyb.ADC(self.pin)

    def get_state(self):
        """ A function that returns if the switch is currently pressed
        
        Returns:
            Informs the robot if the switch has been pressed or not
        """
        if self.signal_pin.read() > 1000:
            return False
        else:
            return True