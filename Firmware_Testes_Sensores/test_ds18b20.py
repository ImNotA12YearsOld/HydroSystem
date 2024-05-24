import time
import onewire
import ds18x20
from machine import Pin

# Define the pin connected to the DS18B20 sensor
pin = Pin(12)

# Create a OneWire bus object
ow = onewire.OneWire(pin)

# Create a DS18X20 sensor object
temp_sensor = ds18x20.DS18X20(ow)

# Scan for DS18B20 devices on the bus
devices = temp_sensor.scan()

# Check if any DS18B20 devices are found
if devices:
    # Loop to continuously read temperature and print
    while True:
        # Start temperature conversion
        temp_sensor.convert_temp()
        
        # Wait for conversion to complete (750ms for DS18B20)
        time.sleep_ms(750)
        
        # Read temperature from the sensor
        for device in devices:
            temperature = temp_sensor.read_temp(device)
            print("Temperature: {:.1f}°C".format(temperature))
        
        # Wait for 30 seconds before the next reading
        time.sleep(30)
else:
    print("No DS18B20 devices found.")
