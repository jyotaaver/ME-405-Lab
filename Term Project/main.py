""" Description of this file """

from pyb import Pin, Timer
from Encoder import *
import cotask
from MotorControl import *
from RomiControl import *
from BlinkLedOnNucleo import *
from IMUController import *

if __name__ == '__main__':
    """ The main file that establishes all shares between tasks, the tasks themselves, then runs the tasks according
    to a scheduler.
    
    The order that the tasks run in is dependent on the priority and period of each task. A larger number for priority
    indicates a higher priority. There are 4 tasks total. The first two tasks are the motor controller tasks for the left
    and right motors. The third task is the Romi Control task that tells the motors how fast to spin depending on the 
    input sensor data. The fourth task blinks an LED to indicate that the Romi is on and Romi control is telling the motors
    to run at a non-zero speed. As can be seen in the code and in the files, there is a fifth task declared but not used.
    This task was meant to be used for IMU sensor data to tell romi how to drive straight to the start once it reaches the
    finish. Due to task timing issues in the scheduler as a result of this task taking too long to run, this task was not 
    used. 
    """

    # Left Wheel Motor
    left_encoder = Encoder(3, Pin.cpu.B4, Pin.cpu.B5, 65535, 0)
    left_motor = RomiMotor(1, Pin.cpu.A9, Pin.cpu.C7, Pin.cpu.A10, left_encoder, 0)
    left_motor.set_duty(0)
    left_motor.enable()

    # Right Wheel Motor
    right_encoder = Encoder(2, Pin.cpu.A0, Pin.cpu.A1, 65535, 0)
    right_motor = RomiMotor(8, Pin.cpu.B0, Pin.cpu.B7, Pin.cpu.C1, right_encoder, 1)
    right_motor.set_duty(0)
    right_motor.enable()

    motor_A_flag = task_share.Share('f', name="Control Flag A")
    motor_B_flag = task_share.Share('f', name="Control Flag B")

    data_A = task_share.Share('f', name="Data A")
    data_B = task_share.Share('f', name="Data B")
    L_Enc = task_share.Share('f', name="L Enc")
    R_Enc = task_share.Share('f', name="R Enc")
    L_omega = task_share.Share('f', name="L omega")
    R_omega = task_share.Share('f', name="L omega")
    x_coord = task_share.Share('f', name="X Coord")
    y_coord = task_share.Share('f', name="y Coord")
    blue_button = task_share.Share('f', name="Blue Button")
    imu_control_flag = task_share.Share('f', name="Blue Button")

    mot_per = 10
    mot_freq = 1000 / mot_per

    # Motor Controller for Motor A (Left)
    task1 = cotask.Task(TaskMotorControl(left_motor, data_A, L_Enc, L_omega).run,
                        "Task 1", priority=3, period=mot_per)

    # Motor Controller for Motor B (Right)
    task2 = cotask.Task(TaskMotorControl(right_motor, data_B, R_Enc, R_omega).run,
                        "Task 2", priority=3, period=mot_per)

    # Romi Control Task
    task3 = cotask.Task(TaskRomiControlGenFun(motor_A_flag, motor_B_flag, data_A, data_B, L_Enc, R_Enc, blue_button).run,
                        "Task 3", priority=2, period=15)

    # Blink LED Task (used for ensuring that computer is still multitasking)line_follow
    task4 = cotask.Task(BlinkLedGenFun(blue_button).run, "Task 4", priority=0, period=250)

    # Positional Calculate
    task5 = cotask.Task(TaskAcquirePositionGenFun(L_omega, R_omega, x_coord, y_coord, blue_button).run,
                        "Task 5", priority=1, period=50)

    # Adding Tasks to a Task List
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    cotask.task_list.append(task3)
    cotask.task_list.append(task4)
    # Task 5, the position tracker is commented out because the current task causes scheduling to fall behind resulting
    # in poor function of the rest of the tasks.
    # cotask.task_list.append(task5)

    # Run All tasks and break from program and send task info if debug key (+) is pressed
    while True:
        cotask.task_list.pri_sched()
