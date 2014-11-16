from copy import deepcopy
import serial
from ada_protocol import AdaProtocolHandler
import time
from helpers import DummySerialDevice
from led_states import ChaserLEDState

LED_COUNT = 240
LED_PORT = "/dev/ttyACM0"
LED_DURATION = 600
LED_FADE_TIME = 0.05
LED_FADE_STEPS = 30


class ColorChaser(AdaProtocolHandler):
    def __init__(self, *args, **kwargs):
        print args
        print kwargs
        super(ColorChaser, self).__init__(*args, **kwargs)
        # do something else
        self.spacing = 30
        self.fade_by = 20
        # # kwargs['state_kwargs'] = {"spacing": self.spacing, "fade_by": self.fade_by}


        self.init_leds()

    def init_leds(self):
        c = 0
        for led in self.leds:
            led.hue = 60
            led.spacing = self.spacing
            led.fade_by = self.fade_by
            led.status = led.id % led.spacing

    def run(self):
        while time.time() < self.t_end:
            new_buffer = deepcopy(self.buffer_header())
            for led in self.leds:
                led.do_step()
                new_buffer.extend(led.read_rgb())
            self.device.write(new_buffer)
            time.sleep(self.fade_time)

# for debugging
# s = serial.Serial(LED_PORT, 115200)
s = DummySerialDevice()
t = ColorChaser(device=s, led_count=LED_COUNT, run_duration=LED_DURATION, fade_time=LED_FADE_TIME, fade_steps=LED_FADE_STEPS, state_storage=ChaserLEDState)
t.run()

s.close()