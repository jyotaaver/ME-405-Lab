from RomiMotor import *
import micropython

micropython.alloc_emergency_exception_buf(150)


class TaskMotorControl:

    def __init__(self, motor: RomiMotor, speed_data, data):
        """!@brief This class is the motor controller for a Romi DC motor.
            @details This class takes the latest speed given to it from the RomiControl task and sets the motor speed to
            the provided speed by running closed loop control of that speed through its motor object
            @param motor the motor that this task controls
            @param speed_data data that is sent from RomiControl that tells MotorControl what to set the motor speed to
            """

        self.state = 1
        self.mot = motor
        self.data = data
        self.speed_data = speed_data

        self.kp = 0.5
        self.ki = 0.5
        self.desired_speed = 0

    def run(self):
        """!@brief The actual generator function that runs within this class to set the new motor speed
            """
        while True:

            self.desired_speed = self.speed_data.get()

            self.mot.closed_loop(self.kp, self.ki, self.desired_speed)

            yield self.state


TaskMotorControl.run()
