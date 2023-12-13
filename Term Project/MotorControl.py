from L6206 import *
import micropython

micropython.alloc_emergency_exception_buf(150)


class TaskMotorControl:

    def __init__(self, motor: L6206, speed_data):
        """!@brief This class is the motor controller for a DC motor.
            @details This class communicates with the UI task to decide what to do with regard to controlling the motor
            @param motor the motor that this task controls
            @param speed_data data that is sent from RomiControl that tells MotorControl what to set the motor speed to
            """
        self.state = 1
        self.mot = motor

        self.kp = 0.5
        self.ki = 0.5
        self.desired_speed = 0

        self.speed_data = speed_data

    """!@brief The actual generator function that runs within this class
        """
    def run(self):
        while True:

            self.desired_speed = self.speed_data.get()

            self.mot.closed_loop(self.kp, self.ki, self.desired_speed)

            yield self.state
