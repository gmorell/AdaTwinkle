import collections
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

    def proto_value(self):
        return "Been running command %s seconds" % (self.counter / 10)


class BaseTwistedStep(object):
    def __init__(self, *args, **kwargs):
        filters = kwargs.pop('filters', collections.OrderedDict())
        self.filters = filters
        self.transitions_list = []
        kwargs.pop("id", None)
        super(BaseTwistedStep, self).__init__(*args, **kwargs)
    def intermediate_extra_led(self, led):
        pass
    def final_extra_group(self):
        pass
    def step(self):
        if self.transitions_list:
            # oh man since the filters were pre-calculated, no extra work
            self.device.write(self.transitions_list.pop(0))
        else:
            # new_buffer = deepcopy(self.buffer_header())
            new_buffer = []
            for led in self.leds:
                led.do_step()
                self.intermediate_extra_led(led)
                state = led.read_rgb()
                # apply output filters in the order they're in

                for f in self.filters:
                    state = f.do_filter(state)
                new_buffer.extend(state)

            self.final_extra_group()
            self.device.write(new_buffer)
            # time.sleep(self.fade_time)