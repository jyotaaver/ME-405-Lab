import pyb
from pyb import Pin


class SensorTwoLeds:

    def __init__(self, power_pin, control_pin, sig_1_pin, sig_2_pin):
        """ A driver class for a sensor with two LED sensors on it.
        
        Objects of this class can be used to read what each sensor on the device on the Romi is currently
        seeing (black, gray, or white). Objects of this class can also be used to tell RomiController if the sensor sees
        black, white, or both on the two sensors on the device.
        
        Args:
            power_pin: the pin that powers the IR sensor
            control_pin: the pin that controls that sensitivity of the sensors
            sig_1_pin: the pin that is used to read the first sensor
            sig_2_pin: the pin that is used to read the second sensor
        """
        self.power_pin = Pin(power_pin, mode=Pin.OUT)
        self.control_pin = Pin(control_pin, mode=Pin.OUT)
        self.sig_1_pin = Pin(sig_1_pin, mode=Pin.IN)
        self.sig_2_pin = Pin(sig_2_pin, mode=Pin.IN)
        self.sensor_1 = pyb.ADC(sig_1_pin)
        self.sensor_2 = pyb.ADC(sig_2_pin)

        self.control_pin.high()
        self.power_pin.high()

    def read(self, sensor):
        """A method that outputs a sensor reading as a value
        
        Returns:
            A value output from the LED sensor
        """
        if sensor == 1:
            return self.sensor_1.read()
        else:
            return self.sensor_2.read()

    def sees(self, sensor):
        """ A method that outputs the color read by a sensor
        
        Certain sensor output values are correlated with either black, gray, or white
        
        Returns:
            Returns the color read by the individual sensor
        """
        if sensor == 1:
            current_value = self.sensor_1.read()
            if 2000 < current_value < 3200:
                return "Black"
            elif 1000 < current_value < 2000:
                return "Gray"
            elif current_value < 1000:
                return "White"
            else:
                return "None"
        elif sensor == 2:
            current_value = self.sensor_2.read()
            if 2000 < current_value < 3200:
                return "Black"
            elif 1000 < current_value < 2000:
                return "Gray"
            elif current_value < 1000:
                return "White"
            else:
                return "None"

    def state(self):
        """A method that outputs a value for the two LED sensor object 
        in accordance to the two individual sensors on an array
        
        The output of the two individual sensors are tested to determine if the sensors are either over
        the line, off the line, or partially over the line
        
        Returns:
            The state of the 2 LED sensor, either a color or condition
        """
        if self.sees(1) == "Black" and self.sees(2) == "Black":
            return "Black"
        elif self.sees(1) == "White" and self.sees(2) == "White":
            return "White"
        elif self.sees(1) == "None" and self.sees(2) == "None":
            return "None"
        elif ((self.sees(1) == "Black" or self.sees(1) == "Gray") and self.sees(2) == "White" or
              self.sees(1) == "White" and (self.sees(2) == "Black" or self.sees(2) == "Gray")):
            return "Both"
        else:
            return "Error"
