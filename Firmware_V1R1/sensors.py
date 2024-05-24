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
        self.last_ph_measurement = self.ph_average_value()#self.ph_sens.read_u16()
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
        self.calibration_slope = -25.78  # Example value, adjust based on your calibration
        self.calibration_intercept = 47.404 # Example value, adjust based on your calibration
        # Convert voltage to pH using calibration equation
        pH = voltage * self.calibration_slope + self.calibration_intercept
        return pH

    def read_ph_sensor(self):
        # Read analog value from the pH sensor
        raw_value = self.ph_sens.read_u16() >> 4  # Read 16-bit unsigned integer
        # Convert analog value to voltage (0-3.3V)
        voltage = raw_value * 3.3 / 4096
        # Convert voltage to pH value using calibration
        pH_value = self.map_voltage_to_pH(voltage)
        return pH_value
    
    def ph_average_value(self):
        total_pH = 0
        for _ in range(1000):
        # Read pH value
            pH_value = self.read_ph_sensor()
            total_pH += pH_value
        # Calculate average pH
        average_pH = round((total_pH / 1000) + 2, 1)
        return average_pH

    def convert_to_lux(self):
        a = 0
        for i in range(1000):
            a+=self.light_sens.read_u16() // 64  # Read ADC value from the light sensor
            media = a / 1000
        lux = round((3.3 * 2 * 1000000) / (1024 * 5000) * media)
        offset = 57
        lux_offsetted = lux + offset
        #print("lux:", lux_offsetted)
        #utime.sleep(2)  # Optional: add a delay to avoid printing too frequently# Optional: add a delay to avoid printing too frequently
        return lux_offsetted

