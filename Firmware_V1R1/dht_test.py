import dht
import machine
import time

# Define the pin number
dht_pin = machine.Pin(2)

# Create a DHT object
dht_sensor = dht.DHT11(dht_pin)

# Function to read and print sensor data
def read_sensor():
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    print("Temperature: {:.1f}°C, Humidity: {:.1f}%".format(temperature, humidity))

# Main loop
while True:
    try:
        # Read sensor data
        read_sensor()
    except OSError as e:
        print("Failed to read sensor:", e)
    
    # Wait for 30 seconds
    time.sleep(2)
