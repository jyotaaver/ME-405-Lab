import pyb


class Encoder:
    """!@brief An encoder class for our motor encoders.
        @details Objects of this class can be used to determine the current
        and change in position of a DC motor on one channel.
        @param timer_channel timer channel used by the encoder to determine position.
        @param encoder_pin_A one of the pins for the encoder to determine position
        @param encoder_pin_B the other pin for the encoder to determine position
        @param AR auto reload value for the motor (set to 65535 for this lab)
        @param PS used if larger steps are needed (set to zero for this lab)
        """
    def __init__(self, timer_channel, encoder_pin_A, encoder_pin_B, AR, PS):
        self.timer_channel = timer_channel
        self.encoder_pin_A = encoder_pin_A
        self.encoder_pin_B = encoder_pin_B

        self.timer = pyb.Timer(timer_channel, period=AR, prescaler=PS)
        self.timer.channel(1, pin=encoder_pin_A, mode=pyb.Timer.ENC_AB)
        self.timer.channel(2, pin=encoder_pin_B, mode=pyb.Timer.ENC_AB)

        self.position = 0
        self.delta = 0
        self.speed = 0
        self.desired_speed = 0
        self.count = 0

        self.prev_count = 0

        self.AR = AR

        self.AR_limit = (AR + 1) // 2
        self.PS = PS

    """!@brief An function to update the current position and delta of the motor. 
        @details Function uses the timer counter to determine the delta of the motor
        and then calculates the new position of the motor
        """
    def update(self):

        self.count = self.timer.counter()
        self.delta = self.count - self.prev_count
        self.prev_count = self.count

        if self.delta > 0 and self.delta > self.AR_limit:
            self.delta -= (self.AR + 1)

        elif self.delta < 0 and self.delta < -self.AR_limit:
            self.delta += self.AR + 1

        self.position += self.delta

    """!@brief An function to output the current position of the motor
        @details Function uses the attribute of the encoder class.
        @retun Returns the position of the motor. 
        """
    def get_position(self):
        return self.position

    """!@brief An function to output the current delta of the motor
        @details Function uses the attribute of the encoder class.
        @retun Returns the delta of the motor. 
        """
    def get_delta(self):
        return self.delta

    def get_speed(self, freq):
        return self.get_delta() * freq * 60 // 1440

    """!@brief An function to reset the position in the encoder.
        @details Function sets the position to zero. 
        """
    def zero(self):
        self.position = 0
