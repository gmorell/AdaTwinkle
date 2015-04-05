from copy import deepcopy
import time
from led_states import BaseLEDState


class AdaProtocolHandler(object):
    def __init__(self, device, led_count, run_duration, fade_time, fade_steps, state_storage=BaseLEDState, state_kwargs={}, debug=False):
        self.device = device
        self.led_count = led_count
        self.run_duration = run_duration
        self.fade_time = fade_time
        self.fade_steps = fade_steps
        self.state_storage = state_storage
        self.debug = debug
        self.state_kwargs = state_kwargs

        self.t_start = time.time()
        self.t_end = self.t_start + self.run_duration

        self.leds = [self.state_storage(id=i, **self.state_kwargs) for i in range(self.led_count)]

    def dprint(self, string):
        if self.debug:
            print(string)

    def buffer_header(self):
        buffer_start = ['\x41', '\x64', '\x61']
        buffer_3 = (self.led_count - 1) >> 8
        buffer_4 = (self.led_count - 1) & 0xff
        buffer_5 = buffer_3 ^ buffer_4 ^ 0x55
        buffer_complete = buffer_start + [buffer_3, buffer_4, buffer_5]
        return buffer_complete

    def run(self):
        raise NotImplementedError("Need to implement a run function")


class BaseTwistedStep(object):
    def intermediate_extra_led(self, led):
        pass
    def step(self):
        new_buffer = deepcopy(self.buffer_header())
        for led in self.leds:
            led.do_step()
            self.intermediate_extra_led(led)
            new_buffer.extend(led.read_rgb())
        self.device.write(new_buffer)
        time.sleep(self.fade_time)