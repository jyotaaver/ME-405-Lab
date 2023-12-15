from pyb import Pin


class BlinkLedGenFun:
    def __init__(self, blue_button):
        """ A class to blink an LED on the Nucleo.

            It only makes sense to have one object of this class because all objects would send signals to the same
            LED on the nucleo. This task will change the state of the LED from on to off or from off to on each time this
            task runs. The LED will only blink if the blue_button is set to 1.
        """
        self.state = 1
        self.PA5 = Pin(Pin.cpu.A5, mode=Pin.OUT_PP)
        self.blue_button_flag = blue_button

    def run(self):
        """ Generator function to blink the LED only if the blue button has been pressed an odd amount of times."""
        while True:

            if self.blue_button_flag.get() == 1:
                if self.state == 1:
                    self.PA5.high()
                    self.state = 2
                elif self.state == 2:
                    self.PA5.low()
                    self.state = 1

            else:
                self.PA5.low()

            yield self.state
