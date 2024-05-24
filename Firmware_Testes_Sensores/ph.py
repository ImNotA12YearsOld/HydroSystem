from machine import Pin, ADC
import time

class pH_Sensor:
    def __init__(self, pin_number):
        # Initialize ADC with default (maximum) resolution
        self.ph_sens = ADC(Pin(pin_number))
        # Calibration parameters (adjust according to your calibration)
        self.calibration_slope = -25.78  # Example value, adjust based on your calibration
        self.calibration_intercept = 47.404 # Example value, adjust based on your calibration

    def read_ph_sensor(self):
        # Read analog value from the pH sensor
        raw_value = self.ph_sens.read_u16() >> 4  # Read 16-bit unsigned integer
        # Convert analog value to voltage (0-3.3V)
        voltage = raw_value * 3.3 / 4096
        # Convert voltage to pH value using calibration
        pH_value = self.map_voltage_to_pH(voltage)
        return pH_value

    def map_voltage_to_pH(self, voltage):
        # Convert voltage to pH using calibration equation
        pH = voltage * self.calibration_slope + self.calibration_intercept
        return pH

# Usage example:
ph_sensor = pH_Sensor(26)  # Assuming the sensor is connected to pin 26

while True:
    # Read pH values and calculate the average
    total_pH = 0
    for _ in range(1000):
        # Read pH value
        pH_value = ph_sensor.read_ph_sensor()
        total_pH += pH_value

    # Calculate average pH
    average_pH = total_pH / 1000

    # Print the average pH value
    print("Average pH Value:", average_pH)

    # Wait for 2 seconds before the next reading
    time.sleep(2)
