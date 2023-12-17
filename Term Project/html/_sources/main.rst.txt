main module
===========

The main file that establishes all shares between tasks, the tasks themselves, then runs the tasks according
to a scheduler.

The order that the tasks run in is dependent on the priority and period of each task. A larger number for priority
indicates a higher priority. There are 4 tasks total. The first two tasks are the motor controller tasks for the left
and right motors. The third task is the Romi Control task that tells the motors how fast to spin depending on the
input sensor data. The fourth task blinks an LED to indicate that the Romi is on and Romi control is telling the motors
to run at a non-zero speed. As can be seen in the code and in the files, there is a fifth task declared but not used.
This task was meant to be used for IMU sensor data to tell romi how to drive straight to the start once it reaches the
finish. Due to task timing issues in the scheduler as a result of this task taking too long to run, this task was not
used.

One novel aspect of this design include the use of only two sensor devices (two LEDS on each sensor) to limit the
pin usage on the Nucleo. An additional novel aspect to this code is the use of the LED module to allow the user to
see if Romi is in run mode or wait mode.

.. automodule:: main
   :members:
   :undoc-members:
   :show-inheritance:
