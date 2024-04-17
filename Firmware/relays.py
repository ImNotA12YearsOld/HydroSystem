from machine import Pin
import gc

VALVE_OUT = 27
LAMP_OUT = 22
PUMP_OUT = 21
FEED_OUT = 20
MIX_OUT = 17

TURN_ON = True
TURN_OFF = False

class Relays():
    
    def __init__(self):
        self.valve = Pin(VALVE_OUT, Pin.OUT)
        self.lamp = Pin(LAMP_OUT, Pin.OUT)
        self.pump = Pin(PUMP_OUT, Pin.OUT)
        self.feed = Pin(FEED_OUT, Pin.OUT)
        self.mix = Pin(MIX_OUT, Pin.OUT)
        gc.collect()
    
    def toggle_output(self, out):
        if out is VALVE_OUT:
            self.valve.toggle()
        elif out is LAMP_OUT:
            self.lamp.toggle()
        elif out is PUMP_OUT:
            self.pump.toggle()
        elif out is FEED_OUT:
            self.feed.toggle()
        elif out is MIX_OUT:
            self.mix.toggle()
        gc.collect()
    
    def turn_output(self, out, turn):
        if out is VALVE_OUT:
            self.valve.high() if turn else self.valve.low()
        elif out is LAMP_OUT:
            self.lamp.high() if turn else self.lamp.low()
        elif out is PUMP_OUT:
            self.pump.high() if turn else self.pump.low()
        elif out is FEED_OUT:
            self.feed.high() if turn else self.feed.low()
        elif out is MIX_OUT:
            self.mix.high() if turn else self.mix.low()
        gc.collect()