from copy import deepcopy
from devices.base import BaseDevice

class AdaDevice(BaseDevice):
    def __init__(self, serial, led_count=240):
        self.led_count = led_count
        self.serial = serial

    def buffer_header(self):
        buffer_start = ['\x41', '\x64', '\x61']
        buffer_3 = (self.led_count - 1) >> 8
        buffer_4 = (self.led_count - 1) & 0xff
        buffer_5 = buffer_3 ^ buffer_4 ^ 0x55
        buffer_complete = buffer_start + [buffer_3, buffer_4, buffer_5]
        return buffer_complete

    def write(self, values):
        new_buffer = deepcopy(self.buffer_header())
        new_buffer.extend(values)
        self.serial.write(new_buffer)