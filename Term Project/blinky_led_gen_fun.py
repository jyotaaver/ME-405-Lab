from pyb import Pin

PA5 = Pin(Pin.cpu.A5, mode=Pin.OUT_PP)


class blinky_gen_fun:
    def __init__(self, state):
        self.state = state
        self.count = 0
        self.limit = 100

    def run(self):
        while True:
            if self.state == 1:
                PA5.high()
                self.state = 2
            elif self.state == 2:
                PA5.low()
                self.state = 1
            yield self.state