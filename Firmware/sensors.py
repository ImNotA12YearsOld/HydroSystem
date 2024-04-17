from machine import Pin, ADC
from dht import DHT11
from ds18x20 import DS18X20
from onewire import OneWire
import gc

DHT11_PIN = 2
DS18B20_PIN = 12
LIGHT_SENS_PIN = 28
PH_SENS_PIN = 26
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
        self.last_light_measurement = self.light_sens.read_u16()
        self.last_ph_measurement = self.ph_sens.read_u16()
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