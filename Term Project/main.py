""" Description of this file """

from pyb import Pin, Timer
from Encoder import *
import cotask
from MotorControl import *
from RomiControl import *
from BlinkLedOnNucleo import *
# from IMUController import *

if __name__ == '__main__':

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




    mot_per = 10
    mot_freq = 1000 / mot_per

    # Motor Controller for Motor A (Left)
    task1 = cotask.Task(TaskMotorControl(left_motor, data_A, L_Enc, L_omega).run,
                        "Task 1", priority=2, period=mot_per)

    # Motor Controller for Motor B (Right)
    task2 = cotask.Task(TaskMotorControl(right_motor, data_B, R_Enc, R_omega).run,
                        "Task 2", priority=2, period=mot_per)

    # User Interface Task
    task3 = cotask.Task(TaskRomiControlGenFun(motor_A_flag, motor_B_flag, data_A, data_B, L_Enc, R_Enc).simple_line_follow,
                        "Task 3", priority=1, period=15)

    # Blink LED Task (used for ensuring that computer is still multitasking)line_follow
    task4 = cotask.Task(BlinkLedGenFun().run, "Task 4", priority=0, period=250)
    
    # # Positional Calculate
    # task5 = cotask.Task(TaskAquirePositionGenFun(L_omega, R_omega, x_coord, y_coord), "Task 5", priority=1, period=15)

    # Adding Tasks to a Task List
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    cotask.task_list.append(task3)
    cotask.task_list.append(task4)
    # cotask.task_list.append(task5)

    # Run All tasks and break from program and send task info if debug key (+) is pressed
    while True:
        cotask.task_list.pri_sched()
