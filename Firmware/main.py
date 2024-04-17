from machine import I2C, Pin
from time import sleep, time
from relays import Relays, VALVE_OUT, LAMP_OUT, PUMP_OUT, FEED_OUT, MIX_OUT, TURN_ON, TURN_OFF
from sensors import Sensors
from mcp7940 import MCP7940
from utime import localtime
from pico_i2c_lcd import I2cLcd
from wifi import WiFiConfig
from tago import TagoIO

# Calculo do proximo evento
def calc_next_time(new_time, last_time, hours, minutes):
    new_time["hours"] = last_time["hours"] + hours
    new_time["minutes"] = last_time["minutes"] + minutes
    if new_time["minutes"] >= 60:
        new_time["minutes"] -= 60
        new_time["hours"] += 1
    if new_time["hours"] >= 24:
        new_time["hours"] -= 24
    new_time["valid"] = True
    return new_time

# RTC indexes
YEAR = 0
MONTH = 1
DAY = 2
HOURS = 3
MINUTES = 4
SECONDS = 5
WK_DAY = 6

# Ciclos de acionamento (24h)
DAYTIME = {"min": 5, "max": 17}
NIGHTTIME = {"min": 18, "max": 4}
next_time_on = {"hours": 0, "minutes": 0, "valid": False}
next_time_off = {"hours": 0, "minutes": 0, "valid": False}

# Range do sensor de PH
PH_SENS_RANGE = {"min": 0, "max": 14}

# Por do sol
is_sunset = False

# Indice de dados do LCD
lcd_data_index = 0
lcd_data_write = True
lcd_showing_data_seconds = 0

# Envio de dados para a Tago
next_time_send_data = {"hours": 0, "minutes": 0, "valid": False}
SSID = "Crias 2G" # SSID REDE WIFI
PASSWORD = "RTRR2023" # SENHA REDE WIFI
tago = TagoIO("1c7097ad-c7f8-4834-a5e0-6895be0b6d1b") # TOKEN PARA TRANSMITIR PARA TAGO

wifi_config = WiFiConfig(SSID, PASSWORD)
wifi_config.connect()

relays = Relays()
sensors = Sensors()
i2c = I2C(1, sda=Pin(18), scl=Pin(19), freq=100000)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)
mcp = MCP7940(i2c)
mcp.time = localtime()
mcp.start()
mcp.battery_backup_enable(True)
first_mcp_time = mcp.time
next_time_on["hours"] = first_mcp_time[HOURS]
next_time_on["minutes"] = first_mcp_time[MINUTES]
next_time_send_data["hours"] = first_mcp_time[HOURS]
next_time_send_data["minutes"] = first_mcp_time[MINUTES]
calc_next_time(next_time_on, next_time_on, 0, 1)
calc_next_time(next_time_send_data, next_time_send_data, 0, 1)
        
while True:
    # Lendo o RTC e sensores
    time_now = mcp.time
    sensors.sample_sensors()

    # Checando ciclos de acionamento da bomba
    if time_now[HOURS] >= DAYTIME["min"] and time_now[HOURS] <= DAYTIME["max"]:
        if next_time_on["valid"]:
            if(time_now[HOURS] is next_time_on["hours"]) and (time_now[MINUTES] is next_time_on["minutes"]):
                relays.turn_output(PUMP_OUT, TURN_ON)
                next_time_off = calc_next_time(next_time_off, next_time_on, 0, 15)
                next_time_on["valid"] = False
        if next_time_off["valid"]:
            if(time_now[HOURS] is next_time_off["hours"]) and (time_now[MINUTES] is next_time_off["minutes"]):
                relays.turn_output(PUMP_OUT, TURN_OFF)
                next_time_on = calc_next_time(next_time_on, next_time_off, 0, 15)
                next_time_off["valid"] = False
            
    elif time_now[HOURS] >= NIGHTTIME["min"] or time_now[HOURS] <= NIGHTTIME["max"]:
        if next_time_on["valid"]:
            if(time_now[HOURS] is next_time_on["hours"]) and (time_now[MINUTES] is next_time_on["minutes"]):
                relays.turn_output(PUMP_OUT, TURN_ON)
                next_time_off = calc_next_time(next_time_off, next_time_on, 0, 15)
                next_time_on["valid"] = False
        if next_time_off["valid"]:
            if(time_now[HOURS] is next_time_off["hours"]) and (time_now[MINUTES] is next_time_off["minutes"]):
                relays.turn_output(PUMP_OUT, TURN_OFF)
                next_time_on = calc_next_time(next_time_on, next_time_off, 2, 0)
                next_time_off["valid"] = False
    else:
        # Deu ruim...
        relays.turn_output(PUMP_OUT, TURN_OFF)
    
    # Checando por do sol
    if time_now[HOURS] >= 18 and (time_now[HOURS] <= 21 and time_now[MINUTES] < 30):
        if not is_sunset:
            relays.turn_output(LAMP_OUT, TURN_ON)
            is_sunset = True
    if is_sunset and (time_now[HOURS] >= 21 and time_now[MINUTES] >= 30):
        relays.turn_output(LAMP_OUT, TURN_OFF)
        is_sunset = False
        
    # Checando mistura da agua
    if sensors.get_ph_data() < PH_SENS_RANGE["min"] or sensors.get_ph_data() > PH_SENS_RANGE["max"]:
        relays.turn_output(FEED_OUT, TURN_ON)
        relays.turn_output(MIX_OUT, TURN_ON)
    else:
        relays.turn_output(FEED_OUT, TURN_OFF)
        relays.turn_output(MIX_OUT, TURN_OFF)
    
    # Atualizar dados LCD
    if lcd_data_index is 0:
        lcd.clear()
        if time_now[HOURS] < 10:
            lcd.putstr("0")
        lcd.putstr("{}:".format(time_now[HOURS]))
        if time_now[MINUTES] < 10:
            lcd.putstr("0")
        lcd.putstr("{}:".format(time_now[MINUTES]))
        if time_now[SECONDS] < 10:
            lcd.putstr("0")
        lcd.putstr("{}\n".format(time_now[SECONDS]))
        if time_now[DAY] < 10:
            lcd.putstr("0")
        lcd.putstr("{}/".format(time_now[DAY]))
        if time_now[MONTH] < 10:
            lcd.putstr("0")
        lcd.putstr("{}/".format(time_now[MONTH]))
        if time_now[YEAR] < 10:
            lcd.putstr("0")
        lcd.putstr("{}\n".format(time_now[YEAR]))
    elif lcd_data_index is 1:
        if lcd_data_write:
            lcd.putstr("Nivel Min :{}\n".format(sensors.get_level_sensors_data()[0]))
            lcd.putstr("Nivel Max :{}\n".format(sensors.get_level_sensors_data()[1]))
            lcd_data_write = False
    elif lcd_data_index is 2:
        if lcd_data_write:
            lcd.putstr("DHT Temp :{}oC\n".format(sensors.get_dht_data()[0]))
            lcd.putstr("DHT Umid :{}%\n".format(sensors.get_dht_data()[1]))
            lcd_data_write = False
    elif lcd_data_index is 3:
        if lcd_data_write:
            lcd.putstr("DS18B20: {:.2f}oC\n".format(sensors.get_ds18b20_data()[1]))
            lcd.putstr("TEMT6000:{}lux\n".format(sensors.get_light_data()))
            lcd_data_write = False
    elif lcd_data_index is 4:
        if lcd_data_write:
            lcd.putstr("PH: {}\n".format(sensors.get_ph_data()))
            lcd_data_write = False
    elif lcd_data_index is 5:
        if lcd_data_write:
            lcd.putstr("V:{} L:{} P:{} F:{}\n".format(relays.get_output_state(VALVE_OUT),
                                                    relays.get_output_state(LAMP_OUT),
                                                    relays.get_output_state(PUMP_OUT),
                                                    relays.get_output_state(FEED_OUT)))
            lcd.putstr("M:{}\n".format(relays.get_output_state(MIX_OUT)))
            lcd_data_write = False
    elif lcd_data_index is 6:
        if lcd_data_write:
            if next_time_on["valid"]:
                lcd.putstr("Next Pump On:\n")
                if next_time_on["hours"] < 10:
                    lcd.putstr("0")
                lcd.putstr("{}:".format(next_time_on["hours"]))
                if next_time_on["minutes"] < 10:
                    lcd.putstr("0")
                lcd.putstr("{}\n".format(next_time_on["minutes"]))
            if next_time_off["valid"]:
                lcd.putstr("Next Pump Off:\n")
                if next_time_off["hours"] < 10:
                    lcd.putstr("0")
                lcd.putstr("{}:".format(next_time_off["hours"]))
                if next_time_off["minutes"] < 10:
                    lcd.putstr("0")
                lcd.putstr("{}\n".format(next_time_off["minutes"]))
            lcd_data_write = False
    lcd_showing_data_seconds += 1
    if lcd_showing_data_seconds >= 6:
        lcd_showing_data_seconds = 0
        lcd_data_index += 1
        lcd_data_write = True
        lcd.clear()
        if lcd_data_index > 6:
            lcd_data_index = 0
            
    # Enviar dados para Tago
    # Dados a serem enviados para a plataforma Tago
    if next_time_send_data["valid"] and time_now[HOURS] is next_time_send_data["hours"] and time_now[MINUTES] is next_time_send_data["minutes"]:
        data = [
            {
                "value": sensors.get_level_sensors_data()[0],
                "variable": "level_sens_min",
            },
            {
                "value": sensors.get_level_sensors_data()[1],
                "variable": "level_sens_max",
            },
            {
                "value": sensors.get_dht_data()[0],
                "unit": "C",
                "variable": "dht_temp",
            },
            {
                "value": sensors.get_dht_data()[1],
                "unit": "%",
                "variable": "dht_humid",
            },
            {
                "value": sensors.get_ds18b20_data()[1],
                "unit": "C",
                "variable": "ds18b20_temp",
            },
            {
                "value": sensors.get_light_data(),
                "units": "lux",
                "variable": "light",
            },
            {
                "value": sensors.get_ph_data(),
                "variable": "ph",
            },
#             {
#                 "value": {
#                     "Valve": relays.get_output_state(VALVE_OUT),
#                     "Lamp": relays.get_output_state(LAMP_OUT),
#                     "Pump": relays.get_output_state(PUMP_OUT),
#                     "Feed": relays.get_output_state(FEED_OUT),
#                     "Mix": relays.get_output_state(MIX_OUT)
#                     }
#                 "variable": "relay_status",
#             },
        ]
        success = tago.send_data(data)
        calc_next_time(next_time_send_data, next_time_send_data, 1, 0)
    sleep(1)


#     FW_Teste
#     relays.turn_output(VALVE_OUT, TURN_ON)
#     sleep(1)
#     relays.turn_output(LAMP_OUT, TURN_ON)
#     sleep(1)
#     relays.turn_output(PUMP_OUT, TURN_ON)
#     sleep(1)
#     relays.turn_output(FEED_OUT, TURN_ON)
#     sleep(1)
#     relays.turn_output(MIX_OUT, TURN_ON)
#     sleep(1)
#     relays.turn_output(VALVE_OUT, TURN_OFF)
#     sleep(1)
#     relays.turn_output(LAMP_OUT, TURN_OFF)
#     sleep(1)
#     relays.turn_output(PUMP_OUT, TURN_OFF)
#     sleep(1)
#     relays.turn_output(FEED_OUT, TURN_OFF)
#     sleep(1)
#     relays.turn_output(MIX_OUT, TURN_OFF)
#     sleep(1)
#     print("Testing Sensors...")
#     sensors.sample_sensors()
#     sleep(1)
#     print("DHT11: {}".format(sensors.get_dht_data()))
#     sleep(1)
#     print("DS18B20: {}".format(sensors.get_ds18b20_data()))
#     sleep(1)
#     print("TEMT6000: {}".format(sensors.get_light_data()))
#     sleep(1)
#     print("PH-4502: {}".format(sensors.get_ph_data()))
#     sleep(1)
#     print("Level sensors: {}".format(sensors.get_level_sensors_data()))
#     sleep(1)
#     print("Reading RTC...")
#     print(mcp.time)
#     sleep(1)
#     print(I2C_ADDR)
#     lcd.blink_cursor_on()
#     lcd.putstr("Endereco I2C:"+str(I2C_ADDR)+"\n")
#     lcd.putstr("HydroSystem")
#     sleep(5)
#     lcd.clear()
#     lcd.putstr("Hex I2C:"+str(hex(I2C_ADDR))+"\n")
#     lcd.putstr("HydroSystem")
#     sleep(5)
#     lcd.blink_cursor_off()
#     lcd.clear()
#     lcd.putstr("Backlight Test")
#     for i in range(10):
#         lcd.backlight_on()
#         sleep(0.2)
#         lcd.backlight_off()
#         sleep(0.2)
#     lcd.backlight_on()
#     lcd.hide_cursor()
#     for i in range(20):
#         lcd.putstr(str(i))
#         sleep(0.4)
#         lcd.clear()