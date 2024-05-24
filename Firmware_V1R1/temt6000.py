from machine import ADC, Pin
import utime

adc = ADC(Pin(28))

while True:
    a = 0
    for i in range(1000):
        a += adc.read_u16() // 64
    media = a / 1000
    lux = round((3.3 * 2 * 1000000) / (1024 * 5000) * media)
    offset = 57
    lux_offsetted = lux + offset
    print("lux:", lux_offsetted)
    utime.sleep(2)  # Optional: add a delay to avoid printing too frequently


