from copy import deepcopy
import serial
from ada_protocol import AdaProtocolHandler
import time
from helpers import DummySerialDevice
from led_states import ChaserLEDState, RainbowLEDState

LED_COUNT = 240
LED_PORT = "/dev/ttyACM0"
LED_DURATION = 600
LED_FADE_TIME = 0.05
LED_FADE_STEPS = 30


class SimpleColorChaser(AdaProtocolHandler):
    def __init__(self, *args, **kwargs):
        self.spacing = kwargs.pop('spacing', 30)
        self.fade_by = kwargs.pop('fade_by', 15)
        self.hue = kwargs.pop('hue', 0)
        kwargs['state_kwargs'] = {"spacing": self.spacing, "fade_by": self.fade_by, "hue":self.hue}
        super(SimpleColorChaser, self).__init__(*args, **kwargs)

        self.init_leds()

    def init_leds(self):
        for led in self.leds:
            led.status = led.id % led.spacing

    def run(self):
        while time.time() < self.t_end:
            new_buffer = deepcopy(self.buffer_header())
            for led in self.leds:
                led.do_step()
                new_buffer.extend(led.read_rgb())
            self.device.write(new_buffer)
            time.sleep(self.fade_time)

class RainbowChaser(AdaProtocolHandler):
    def __init__(self, *args, **kwargs):
        self.saturation = kwargs.pop('saturation', 255)
        self.value = kwargs.pop('value', 255)
        kwargs['state_kwargs'] = {"saturation": self.saturation, "value": self.value}
        super(RainbowChaser, self).__init__(*args, **kwargs)

        self.init_leds()

    def init_leds(self):
        for led in self.leds:
            led.status = led.id % 255

    def run(self):
        while time.time() < self.t_end:
            new_buffer = deepcopy(self.buffer_header())
            for led in self.leds:
                led.do_step()
                new_buffer.extend(led.read_rgb())
            self.device.write(new_buffer)
            time.sleep(self.fade_time)

# for debugging
# s = DummySerialDevice()
s = serial.Serial(LED_PORT, 115200)
# t = SimpleColorChaser(device=s, led_count=LED_COUNT, run_duration=LED_DURATION, fade_time=LED_FADE_TIME, fade_steps=LED_FADE_STEPS, state_storage=ChaserLEDState,
#                       hue=128, fade_by=15, spacing=30)

t = RainbowChaser(device=s, led_count=LED_COUNT, run_duration=LED_DURATION, fade_time=LED_FADE_TIME, fade_steps=LED_FADE_STEPS, state_storage=RainbowLEDState)
t.run()

s.close()