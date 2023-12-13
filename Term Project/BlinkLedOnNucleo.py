from pyb import Pin


class BlinkLedGenFun:
    def __init__(self):
        """!@brief A class to blink an LED on the Nucleo.
        @details It only makes sense to have one object of this class because all objects would send signals to the same
        pin on the nucleo. This task will change the state of the LED from on to off or from off to on each time this
        task runs.
        """
        self.state = 1
        self.PA5 = Pin(Pin.cpu.A5, mode=Pin.OUT_PP)

    def run(self):
        while True:
            if self.state == 1:
                self.PA5.high()
                self.state = 2
            elif self.state == 2:
                self.PA5.low()
                self.state = 1
            yield self.state
