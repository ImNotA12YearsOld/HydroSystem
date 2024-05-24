def const(val):
    return val

class MCP7940:
    
    ADDRESS = const(0x6F)
    RTCSEC = 0x00
    ST = 7
    RTCWKDAY = 0x03
    VBATEN = 3

    def __init__(self, i2c, status=True, battery_enabled=True):
        self._i2c = i2c

    def start(self):
        self._set_bit(MCP7940.RTCSEC, MCP7940.ST, 1)

    def stop(self):
        self._set_bit(MCP7940.RTCSEC, MCP7940.ST, 0)

    def is_started(self):
        return self._read_bit(MCP7940.RTCSEC, MCP7940.ST)

    def battery_backup_enable(self, enable):
        self._set_bit(MCP7940.RTCWKDAY, MCP7940.VBATEN, enable)

    def is_battery_backup_enabled(self):
        return self._read_bit(MCP7940.RTCWKDAY, MCP7940.VBATEN)

    def _set_bit(self, register, bit, value):
        mask = 1 << bit
        current = self._i2c.readfrom_mem(MCP7940.ADDRESS, register, 1)
        updated = (current[0] & ~mask) | ((value << bit) & mask)
        self._i2c.writeto_mem(MCP7940.ADDRESS, register, bytes([updated]))

    def _read_bit(self, register, bit):
        register_val = self._i2c.readfrom_mem(MCP7940.ADDRESS, register, 1)
        return (register_val[0] & (1 << bit)) >> bit

    @property
    def time(self):
        return self._get_time()

    @time.setter
    def time(self, t):
        year, month, date, hours, minutes, seconds, weekday, yearday = t
        time_reg = [seconds, minutes, hours, weekday + 1, date, month, year % 100]
        print(
            "{}/{}/{} {}:{}:{} (day={})".format(
                time_reg[6],
                time_reg[5],
                time_reg[4],
                time_reg[2],
                time_reg[1],
                time_reg[0],
                time_reg[3],
            )
        )
        print(time_reg)
        reg_filter = (0x7F, 0x7F, 0x3F, 0x07, 0x3F, 0x3F, 0xFF)
        t = [(MCP7940.int_to_bcd(reg) & filt) for reg, filt in zip(time_reg, reg_filter)]
#         print(t)
        self._i2c.writeto_mem(MCP7940.ADDRESS, 0x00, bytes(t))
        
    @property
    def alarm1(self):
        return self._get_time(start_reg=0x0A)

    @alarm1.setter
    def alarm1(self, t):
        _, month, date, hours, minutes, seconds, weekday, _ = t
        time_reg = [seconds, minutes, hours, weekday + 1, date, month]
        reg_filter = (0x7F, 0x7F, 0x3F, 0x07, 0x3F, 0x3F)
        t = [(MCP7940.int_to_bcd(reg) & filt) for reg, filt in zip(time_reg, reg_filter)]
        self._i2c.writeto_mem(MCP7940.ADDRESS, 0x0A, bytes(t))

    @property
    def alarm2(self):
        return self._get_time(start_reg=0x11)

    @alarm2.setter
    def alarm2(self, t):
        _, month, date, hours, minutes, seconds, weekday, _ = t
        time_reg = [seconds, minutes, hours, weekday + 1, date, month]
        reg_filter = (0x7F, 0x7F, 0x3F, 0x07, 0x3F, 0x3F)
        t = [(MCP7940.int_to_bcd(reg) & filt) for reg, filt in zip(time_reg, reg_filter)]
        self._i2c.writeto_mem(MCP7940.ADDRESS, 0x11, bytes(t))

    def bcd_to_int(bcd):
        return (bcd & 0xF) + (bcd >> 4) * 10

    def int_to_bcd(i):
        return (i // 10 << 4) + (i % 10)

    def is_leap_year(year):
        if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
            return True
        return False

    def _get_time(self, start_reg = 0x00):
        num_registers = 7 if start_reg == 0x00 else 6
        time_reg = self._i2c.readfrom_mem(MCP7940.ADDRESS, start_reg, num_registers)
        reg_filter = (0x7F, 0x7F, 0x3F, 0x07, 0x3F, 0x3F, 0xFF)[:num_registers]
#         print(time_reg)
#         print(reg_filter)
        t = [MCP7940.bcd_to_int(reg & filt) for reg, filt in zip(time_reg, reg_filter)]
#         print(t)
        t2 = (t[5] - 20, t[4], t[2], t[1], t[0], t[3] - 1)
        t = (t[6] + 2000,) + t2 + (0,) if num_registers == 7 else t2
#         print(t)
        return t

    class Data:
        def __init__(self, i2c, address):
            self._i2c = i2c
            self._address = address
            self._memory_start = 0x20
            
        def __getitem__(self, key):
            get_byte = lambda x: self._i2c.readfrom_mem(self._address, x + self._memory_start, 1)(x)
            if type(key) is int:
#                 print('key: {}'.format(key))
                return get_byte(key)
            elif type(key) is slice:
#                 print('start: {} stop: {} step: {}'.format(key.start, key.stop, key.step))
                return [get_byte(i) for i in range(64)[key]]

        def __setitem__(self, key, value):
            if type(key) is int:
                print('key: {}'.format(key))
            elif type(key) is slice:
                print('start: {} stop: {} step: {}'.format(key.start, key.stop, key.step))
            print(value)