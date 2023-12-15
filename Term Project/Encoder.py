import pyb


class Encoder:
    """ An encoder class for our motor encoders.
        
        Objects of this class can be used to determine the current
        and change in position of a DC motor on one channel.
        
        Args:
             timer_channel: timer channel used by the encoder to determine position.
             encoder_pin_a: one of the pins for the encoder to determine position
             encoder_pin_b: the other pin for the encoder to determine position
             ar: auto reload value for the motor (set to 65535 for this lab)
             ps: used if larger steps are needed (set to zero for this lab)
    """
    def __init__(self, timer_channel, encoder_pin_a, encoder_pin_b, ar, ps):
        self.timer_channel = timer_channel
        self.encoder_pin_A = encoder_pin_a
        self.encoder_pin_B = encoder_pin_b

        self.timer = pyb.Timer(timer_channel, period=ar, prescaler=ps)
        self.timer.channel(1, pin=encoder_pin_a, mode=pyb.Timer.ENC_AB)
        self.timer.channel(2, pin=encoder_pin_b, mode=pyb.Timer.ENC_AB)

        self.position = 0
        self.delta = 0
        self.speed = 0
        self.desired_speed = 0
        self.count = 0

        self.prev_count = 0

        self.AR = ar

        self.AR_limit = (ar + 1) // 2
        self.PS = ps

    def update(self):
        """ A function to update the current position and delta of the motor.
            
            Function uses the timer counter to determine the delta of the motor
            and then calculates the new position of the motor
        """

        self.count = self.timer.counter()
        self.delta = self.count - self.prev_count
        self.prev_count = self.count

        if self.delta > 0 and self.delta > self.AR_limit:
            self.delta -= (self.AR + 1)

        elif self.delta < 0 and self.delta < -self.AR_limit:
            self.delta += self.AR + 1

        self.position += self.delta

    def get_position(self):
        """ A function to output the current position of the motor
            
            Function uses the attribute of the encoder class.
            
            Returns:
                Returns the position of the motor.
        """
        return self.position

    def get_delta(self):
        """ A function to output the current delta of the motor
            
            Function uses the attribute of the encoder class.
            Returns:
                Returns the delta of the motor.
        """
        return self.delta

    def zero(self):
        """ A function to reset the position in the encoder.
            
            Function sets the position to zero.
        """
        self.position = 0
