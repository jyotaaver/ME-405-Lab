import cotask
from pyb import Pin
import time

if __name__ == '__main__':
    PA5 = Pin(Pin.cpu.A5, mode = Pin.OUT_PP)
    
    
    class task_motor_controller_gen_fun:
        def __init__(self,state):
            PA5.high()
            self.state = state
        def run(self):
            while True:
                PA5.high()
                time.sleep(.5)
                self.state = 2
                yield self.state
    class task_ui_gen_fun:
        def __init__(self,state):
            PA5.low()
            self.state = state

        def run(self):
            while True:
                PA5.low()
                time.sleep(.5)
                self.state = 1
                yield self.state

    task1 = cotask.Task(task_motor_controller_gen_fun(1).run, "Task 1", priority=1, period=1)
    task2 = cotask.Task(task_ui_gen_fun(1).run, "Task 2", priority=1, period=1)

    cotask.task_list.append(task1)
    cotask.task_list.append(task2)

    while True:
        cotask.task_list.pri_sched()