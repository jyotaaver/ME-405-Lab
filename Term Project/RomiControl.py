import task_share
from Sensor import *
from LimitSwitch import *
from pyb import Pin, ExtInt


class TaskRomiControlGenFun:

    def __init__(self, control_flag_a: task_share.Share, control_flag_b: task_share.Share, mot_a_speed, mot_b_speed,
                 l_enc, r_enc, blue_button_flag):
        """ This class is used to send signals to the motors based upon the sensor inputs

            This class communicates with the motor controller task to give inputs to the motor and collect
            data

            Args:
                control_flag_a: A shared variable between this task and one of the motor tasks to tell that motor task
                    what it needs to do independently of the other motor tasks
                control_flag_b: A shared variable between this task and one of the motor tasks to tell that motor task
                    what it needs to do independently of the other motor tasks
                mot_a_speed: speed to be sent to the left motor
                mot_b_speed: speed to be sent to the right motor
                l_enc: left encoder
                r_enc: right encoder
                blue_button_flag: flag used to tell other tasks if the blue button has been pressed
        """

        self.state = 0
        self.next_state = 0
        # self.data = data
        # self.data.put(value) to update value in share
        # self.data.get() to return value from share

        self.mot_A_flag: task_share.Share = control_flag_a
        self.mot_B_flag: task_share.Share = control_flag_b

        self.sensor_A = SensorTwoLeds(Pin.cpu.B13, Pin.cpu.B14, Pin.cpu.A6, Pin.cpu.A7)
        self.sensor_B = SensorTwoLeds(Pin.cpu.B11, Pin.cpu.B12, Pin.cpu.C2, Pin.cpu.C3)
        self.bump_sensor = LimitSwitch(Pin.cpu.C0)

        self.left_motor_speed = mot_a_speed
        self.right_motor_speed = mot_b_speed
        self.current_state = "Stop"
        
        self.left_position = l_enc
        self.right_position = r_enc

        self.left_zero = 0
        self.right_zero = 0
        self.left_delta = 0
        self.right_delta = 0

        # broken gain 0.8
        self.control_gain = 0.6

        self.slow_speed = -10 * self.control_gain
        self.med_speed = -60 * self.control_gain
        # broken top speed 95
        self.high_speed = -80 * self.control_gain

        self.saw_line = 0
        self.internal_count = 0
        self.start_line = 0

        self.tick_distance = 100 * self.control_gain
        self.end_distance = 250 * self.control_gain
        self.end_rotate_distance = 650 * 2

        self.wall_fast_speed = -100
        self.wall_slow_speed = -60

        self.first_in_place_rotate = 650
        self.final_in_place_rotate = 850
        self.pivot_rotation_delta = 1440
        self.wall_straight_delta = 1440*1.5
        self.wall_semi_final_delta = 1440*0.65
        self.wall_first_straight_delta = 1440*0.5
        # self.wall_first_straight_delta = 1440 * 0.75

        self.faith_count = 0
        self.faith_limit = 10000
        self.prev_state = ""

        self.half_way = False
        self.state3_part = 0

        self.blue_button_flag = blue_button_flag
        self.blue_button = ExtInt(Pin.cpu.C13, ExtInt.IRQ_FALLING, Pin.PULL_NONE, self.toggle_blue_button)
        self.use_imu = False

    def toggle_blue_button(self, line):
        """ function called when the blue button is pressed

        The function either disables the robot and resets all major variables or tells all tasks to start running properly
        """
        if self.state == 0:
            self.blue_button_flag.put(1)
            self.state = 1
        else:
            self.blue_button_flag.put(0)
            self.left_motor_speed.put(0)
            self.right_motor_speed.put(0)
            self.state = 0
            self.saw_line = 0
            self.internal_count = 0
            self.start_line = 0
            self.left_zero = 0
            self.right_zero = 0
            self.left_delta = 0
            self.right_delta = 0
            self.state3_part = 0

    def line_follow_control(self):
        """ Function used to determine what speeds to send to the motors """
        if self.current_state == "Go Straight":
            self.left_motor_speed.put(self.med_speed)
            self.right_motor_speed.put(self.med_speed)

        elif self.current_state == "Slight Left":
            self.left_motor_speed.put(self.med_speed // 2)
            self.right_motor_speed.put(self.med_speed)

        elif self.current_state == "Slight Right":
            self.left_motor_speed.put(self.med_speed)
            self.right_motor_speed.put(self.med_speed // 2)

        elif self.current_state == "Turn Left":
            self.left_motor_speed.put(self.slow_speed)
            self.right_motor_speed.put(self.high_speed)

        elif self.current_state == "Turn Right":
            self.left_motor_speed.put(self.high_speed)
            self.right_motor_speed.put(self.slow_speed)

        elif self.current_state == "Sharp Left":
            self.left_motor_speed.put(-self.slow_speed)
            self.right_motor_speed.put(self.high_speed)

        elif self.current_state == "Sharp Right":
            self.left_motor_speed.put(self.high_speed)
            self.right_motor_speed.put(-self.slow_speed)

        elif self.current_state == "Stop":
            self.left_motor_speed.put(0)
            self.right_motor_speed.put(0)

    def wall_avoid_control(self):
        """ Function used to determine what speeds to send to the motors during the wall avoidance process"""
        if self.current_state == "Go Straight":
            self.left_motor_speed.put(self.wall_fast_speed)
            self.right_motor_speed.put(self.wall_fast_speed)

        elif self.current_state == "First Straight":
            self.left_motor_speed.put(self.wall_fast_speed)
            self.right_motor_speed.put(self.wall_fast_speed)

        elif self.current_state == "Turn Right":
            self.left_motor_speed.put(self.wall_fast_speed)
            self.right_motor_speed.put(0)

        elif self.current_state == "Rotate Left":
            self.left_motor_speed.put(-self.wall_slow_speed)
            self.right_motor_speed.put(self.wall_slow_speed)

        elif self.current_state == "Rotate Right":
            self.left_motor_speed.put(self.wall_slow_speed)
            self.right_motor_speed.put(-self.wall_slow_speed)

        elif self.current_state == "Semifinal":
            self.left_motor_speed.put(self.wall_fast_speed)
            self.right_motor_speed.put(self.wall_fast_speed)

        elif self.current_state == "Final":
            self.left_motor_speed.put(-self.wall_slow_speed)
            self.right_motor_speed.put(self.wall_slow_speed)

    def run(self):
        """The generator function that runs endlessly within this class to give speed inputs to the motors depending
        on the sensor readings.
            """

        while True:

            if self.state == 0:
                """ The waiting state for the blue button to be pressed"""
                pass

            if self.state == 1:
                """ the state to follow the line until the Romi hits a wall or reaches the finish line"""

                if self.bump_sensor.get_state():
                    self.current_state = "Rotate Left"
                    self.right_zero = self.right_position.get()
                    self.state = 2

                elif self.sensor_A.state() == "Black" and self.sensor_B.state() == "White":
                    self.current_state = "Turn Left"
                    self.faith_count = 0

                elif self.sensor_A.state() == "White" and self.sensor_B.state() == "Black":
                    self.current_state = "Turn Right"
                    self.faith_count = 0

                elif self.sensor_A.state() == "Both" and self.sensor_B.state() == "Both":
                    self.current_state = "Go Straight"
                    self.faith_count = 0

                elif self.sensor_A.state() == "White" and self.sensor_B.state() == "Both":
                    if self.current_state == "Go Straight" or self.current_state == "Slight Right":
                        self.current_state = "Slight Right"
                    else:
                        self.current_state = "Sharp Right"
                    self.faith_count = 0

                elif self.sensor_A.state() == "Both" and self.sensor_B.state() == "White":
                    if self.current_state == "Go Straight" or self.current_state == "Slight Left":
                        self.current_state = "Slight Left"
                    else:
                        self.current_state = "Sharp Left"
                    self.faith_count = 0

                elif self.sensor_A.state() == "None" and self.sensor_B.state() == "None":
                    self.current_state = "Stop"
                    self.start_line = 0
                    self.saw_line = 0

                elif self.sensor_A.state() == "Black" and self.sensor_B.state() == "Black":
                    if self.start_line == 0:
                        self.start_line = 1
                    elif self.start_line == 2:
                        if self.saw_line == 0:
                            self.saw_line = 1
                        elif self.saw_line == 1:
                            self.internal_count = 0
                        elif self.saw_line == 2:
                            self.state = 3

                    self.current_state = "Go Straight"

                elif self.sensor_A.state() == "White" and self.sensor_B.state() == "White":
                    if self.start_line == 1:
                        self.start_line = 2
                    elif self.saw_line == 1:
                        if self.internal_count > self.tick_distance:
                            self.saw_line = 2
                        else:
                            self.internal_count += 1

                    if self.faith_count <= self.faith_limit:
                        if self.current_state != "Go Straight":
                            self.prev_state = self.current_state
                            self.current_state = "Go Straight"
                        self.faith_count += 1
                    else:
                        if self.prev_state == "Slight Left" or self.prev_state == "Turn Left":
                            self.current_state = "Sharp Left"
                        elif self.prev_state == "Slight Right" or self.prev_state == "Turn Right":
                            self.current_state = "Sharp Right"

                if self.faith_count <= self.faith_limit:
                    if self.current_state != "Sharp Left" and self.current_state != "Sharp Right":
                        self.line_follow_control()
                else:
                    self.line_follow_control()

            elif self.state == 2:
                """ This state is Romi's state once a wall has been hit.
                    
                    This state tells Romi to go around the perimeter of the box until we see a line. We does this 
                    by going around the box in a clock-wise fashion. The Romi will follow a square path. We stop following 
                    the perimeter of the box once the line sensors picks up a line. This "picking up" of a line is only allowed 
                    when the Romi is going in a straight line. This is done in order to avoid the possibility of picking up an 
                    incorrect line as much as possible. Once we pick up a line, we will turn left in order to follow this new 
                    line. This is due to the fact that the new path we must follow will always jut out of the box, meaning that 
                    since we always go clockwise around the box, the path will always be left of the robot.
                    @param Current_state This variable will tell us what portion of the path we are in. We can either be initializing
                    the path by turning left, going straight, turning right for the edges of the square, or turning left once reading 
                    a line.  
                    
                    Args:
                        Current_state: This variable will tell us what portion of the path we are in. We can either be initializing
                        the path by turning left, going straight, turning right for the edges of the square, or turning left once reading 
                        a line.
                        wall_back_count: A constant that sets the length of time to reverse.
                        wall_left_count: A constant that sets the length of time to turn left.
                        wall_right_count: A constant that sets the length of time to turn right.
                        wall_forward_count: A constant that sets the length of time to head straight.
                """

                if self.current_state == "Rotate Left":
                    if self.right_delta >= self.first_in_place_rotate:
                        self.current_state = "First Straight"
                        self.right_delta = 0
                        self.left_zero = self.left_position.get()
                        self.right_zero = self.right_position.get()
                    else:
                        self.right_delta = self.right_zero - self.right_position.get()

                if self.current_state == "First Straight":
                    if self.right_delta >= self.first_in_place_rotate:
                        self.current_state = "Turn Right"
                        self.right_delta = 0
                        self.left_zero = self.left_position.get()
                        self.right_zero = self.right_position.get()
                    else:
                        self.right_delta = self.right_zero - self.right_position.get()

                elif self.current_state == "Turn Right":
                    if self.left_delta >= self.pivot_rotation_delta:
                        self.current_state = "Go Straight"
                        self.left_delta = 0
                        self.left_zero = self.left_position.get()
                        self.left_zero = self.left_position.get()
                    else:
                        self.left_delta = self.left_zero - self.left_position.get()

                elif self.current_state == "Go Straight":
                    if self.sensor_A.state() == "Black" and self.sensor_B.state() == "Black":
                        self.current_state = "Semifinal"
                    else:
                        if self.left_delta >= self.wall_straight_delta:
                            self.current_state = "Turn Right"
                            self.left_delta = 0
                            self.left_zero = self.left_position.get()
                            self.right_zero = self.right_position.get()
                        else:
                            self.left_delta = self.left_zero - self.left_position.get()

                elif self.current_state == "Semifinal":
                    if self.half_way == False:
                        if self.left_delta >= self.wall_semi_final_delta:
                            self.current_state = "Final"
                            self.left_delta = 0
                            self.left_zero = self.left_position.get()
                            self.right_zero = self.right_position.get()
                        else:
                            self.left_delta = self.left_zero - self.left_position.get()
                    else:
                        if self.left_delta >= self.wall_semi_final_delta*1.4:
                            self.current_state = "Final"
                            self.left_delta = 0
                            self.left_zero = self.left_position.get()
                            self.right_zero = self.right_position.get()
                        else:
                            self.left_delta = self.left_zero - self.left_position.get()

                elif self.current_state == "Final":
                    if self.right_delta >= self.final_in_place_rotate:
                        self.current_state = "Go Straight"
                        self.state = 1
                        self.right_delta = 0
                        self.left_zero = self.left_position.get()
                        self.right_zero = self.right_position.get()
                    else:
                        self.right_delta = self.right_zero - self.right_position.get()

                self.wall_avoid_control()

            elif self.state == 3:
                """ This state is Romi's state once it has reached the finish line (or start line at the end of the run)
                    
                    This state tells Romi to rotate in place 180 degrees then continue forward to trace the path back to 
                    the start position
                """

                if self.use_imu == False:
                    if self.half_way == False:
                        if self.state3_part == 0:
                            if self.internal_count < self.end_distance:
                                self.internal_count += 1
                                self.left_motor_speed.put(-60 * self.control_gain)
                                self.right_motor_speed.put(-60 * self.control_gain)
                            else:
                                self.state3_part = 1
                                self.internal_count = 0
                                self.right_delta = 0
                                self.right_zero = self.right_position.get()

                        elif self.state3_part == 1:
                            if self.right_delta >= self.end_rotate_distance:
                                self.right_delta = 0
                                self.left_zero = self.left_position.get()
                                self.right_zero = self.right_position.get()
                                self.state3_part = 2
                            else:
                                self.right_delta = self.right_zero - self.right_position.get()
                                self.left_motor_speed.put(60)
                                self.right_motor_speed.put(-60)
                        elif self.state3_part == 2:
                            self.state = 1
                            self.left_motor_speed.put(0)
                            self.right_motor_speed.put(0)
                            self.saw_line = 0
                            self.internal_count = 0
                            self.start_line = 0
                            self.half_way = True

                    else:
                        # if self.internal_count < self.end_distance:
                        #     self.internal_count += 1
                        #     self.right_motor_speed.put(-40)
                        #     self.right_motor_speed.put(-40)
                        # else:
                        self.left_motor_speed.put(0)
                        self.right_motor_speed.put(0)
                        self.state = 99

                else:
                    pass



            elif self.state == 99:
                pass

            yield self.state
