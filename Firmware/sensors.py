from machine import Pin, ADC
from dht import DHT11
from ds18x20 import DS18X20
from onewire import OneWire
import gc


DHT11_PIN = 2
DS18B20_PIN = 12
PH_SENS_PIN = 26
LIGHT_SENS_PIN = 28
LOW_SENS_PIN = 14
HIGH_SENS_PIN = 15
    
class Sensors():
    
    def __init__(self):
        self.dht11 = DHT11(Pin(DHT11_PIN))
        self.ds18b20 = DS18X20(OneWire(Pin(DS18B20_PIN)))
        self.ds18b20_addr = None
        addresses = self.ds18b20.scan()
        if len(addresses) > 0:
            self.ds18b20_addr = addresses[0]
        self.light_sens = ADC(LIGHT_SENS_PIN)
        self.ph_sens = ADC(PH_SENS_PIN)
        self.last_light_measurement = 0
        self.last_ph_measurement = 0
        self.low = Pin(LOW_SENS_PIN, Pin.IN, Pin.PULL_DOWN)
        self.high = Pin(HIGH_SENS_PIN, Pin.IN, Pin.PULL_DOWN)
        self.last_low_sens_measurement = 0
        self.last_high_sens_measurement = 0
        gc.collect()
        
    def sample_sensors(self):
        self.dht11.measure()
        self.ds18b20.convert_temp()
        self.last_light_measurement = self.convert_to_lux()
        self.last_ph_measurement = self.read_ph_sensor()#self.ph_sens.read_u16()
        self.last_low_sens_measurement = self.low.value()
        self.last_high_sens_measurement = self.high.value()

        gc.collect()
    
    def get_dht_data(self):
        return self.dht11.temperature(), self.dht11.humidity()
    
    def get_ds18b20_data(self):
        if self.ds18b20_addr != None:
            return True, self.ds18b20.read_temp(self.ds18b20_addr)
        return False, None
    
    def get_light_data(self):
        return self.last_light_measurement
    
    def get_ph_data(self):
        return self.last_ph_measurement
    
    def get_level_sensors_data(self):
        return self.last_low_sens_measurement, self.last_high_sens_measurement

    def map_voltage_to_pH(self, voltage):
    # You need to implement this function based on your sensor's calibration curve
    # This is a placeholder
        pH = 7 - (voltage - 2.5)# Example mapping, adjust according to your sensor's characteristics
        return pH
 
    def read_ph_sensor(self):
        # Read analog value from the pH sensor
        analog_value = self.ph_sens.read_u16()  # Read 16-bit unsigned integer      
        # Convert analog value to voltage (0-3.3V)
        voltage = analog_value * 3.3 / 65535
        # Convert voltage to pH value (You need to calibrate this according to your sensor's specifications)
        pH_value = self.map_voltage_to_pH(voltage)  # You need to implement this function
        pH_value = round(pH_value, 2)
        return pH_value
   
    def linear_interpolation(self, x, x_values, y_values):
        if x <= x_values[0]:
            return y_values[0]
        if x >= x_values[-1]:
            return y_values[-1]
        for i in range(len(x_values) - 1):
            if x_values[i] <= x < x_values[i + 1]:
                # Perform linear interpolation
                slope = (y_values[i + 1] - y_values[i]) / (x_values[i + 1] - x_values[i])
                y_intercept = y_values[i] - slope * x_values[i]
                return slope * x + y_intercept

    def convert_to_lux(self):
        adc_reading = self.light_sens.read_u16()  # Read ADC value from the light sensor
    # Example ADC and lux calibration data
        adc_values = [0, 1000, 2000]  # Example ADC readings
        lux_values = [0, 100, 200]     # Corresponding lux values

    # Linear interpolation
        lux = self.linear_interpolation(adc_reading, adc_values, lux_values)
        rounded_lux = round(lux)
        return rounded_lux
