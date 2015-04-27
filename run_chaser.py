from copy import deepcopy
import serial
from ada_protocol import AdaProtocolHandler, BaseTwistedStep
import random
import time
from helpers import DummySerialDevice, pattern_list_fill
from led_states import ChaserLEDState, RainbowLEDState, DualHueLEDState, MultiChaserLEDState, MultiNoSpaceChaseState

LED_COUNT = 240
LED_PORT = "/dev/ttyACM0"
LED_DURATION = 600
LED_FADE_TIME = 0.05
LED_FADE_STEPS = 30


class SimpleColorChaser(BaseTwistedStep, AdaProtocolHandler):
    def __init__(self, *args, **kwargs):
        self.spacing = kwargs.pop('spacing', 30)
        self.fade_by = kwargs.pop('fade_by', 15)
        self.hue = kwargs.pop('hue', 0)
        kwargs['state_kwargs'] = {"spacing": self.spacing, "fade_by": self.fade_by, "hue": self.hue}
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


class MultiSimpleColorChaser(BaseTwistedStep, AdaProtocolHandler):
    def __init__(self, *args, **kwargs):
        self.hues = kwargs.pop('hues', [0, 128])
        self.spacing = kwargs.pop('spacing', 30)
        self.fade_by = kwargs.pop('fade_by', 15)
        kwargs['state_kwargs'] = {"spacing": self.spacing, "fade_by": self.fade_by, "hues": self.hues}
        super(MultiSimpleColorChaser, self).__init__(*args, **kwargs)

        self.init_leds()

    def init_leds(self):
        for led in self.leds:
            led.status = led.id % (led.spacing * len(self.hues))

    def run(self):
        while time.time() < self.t_end:
            new_buffer = deepcopy(self.buffer_header())
            for led in self.leds:
                led.do_step()
                new_buffer.extend(led.read_rgb())
            self.device.write(new_buffer)
            time.sleep(self.fade_time)


class MultiSimpleNoSpaceChaser(BaseTwistedStep, AdaProtocolHandler):
    def __init__(self, *args, **kwargs):
        self.hues = kwargs.pop('hues', [0, 128])
        self.spacing = kwargs.pop('spacing', 30)
        kwargs['state_kwargs'] = {"spacing": self.spacing, "hues": self.hues}
        super(MultiSimpleNoSpaceChaser, self).__init__(*args, **kwargs)

        self.init_leds()


    def init_leds(self):
        for led in self.leds:
            led.status = led.id % (led.spacing * len(self.hues))

    def run(self):
        while time.time() < self.t_end:
            new_buffer = deepcopy(self.buffer_header())
            for led in self.leds:
                led.do_step()
                new_buffer.extend(led.read_rgb())
            self.device.write(new_buffer)
            time.sleep(self.fade_time)


class SimpleShiftingColorChaser(SimpleColorChaser):
    def run(self):
        while time.time() < self.t_end:
            new_buffer = deepcopy(self.buffer_header())
            for led in self.leds:
                led.do_step()
                led.h = ( led.h + 1 ) % 255
                new_buffer.extend(led.read_rgb())
            self.device.write(new_buffer)
            time.sleep(self.fade_time)

    def intermediate_extra_led(self, led):
        led.h = ( led.h + 1 ) % 255

class RainbowChaser(BaseTwistedStep, AdaProtocolHandler):
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


class BouncyChaser(BaseTwistedStep, AdaProtocolHandler):
    def __init__(self, *args, **kwargs):
        self.saturation = kwargs.pop('saturation', 255)
        self.value = kwargs.pop('value', 255)
        self.hue1 = kwargs.pop('hue1', 240)
        self.hue2 = kwargs.pop('hue2', 120)
        self.initial_indices = []

        kwargs['state_kwargs'] = {
            "saturation": self.saturation,
            "value": self.value,
            "hue1": self.hue1,
            "hue2": self.hue2,
        }
        # do some juggling
        rangelen = len(self._min_max_range_gen())
        rangelen_fwd = [i for i in xrange(0, rangelen)]
        rangelen_back = [i for i in reversed(rangelen_fwd)]
        self.rangelen_pattern = rangelen_fwd + rangelen_back

        super(BouncyChaser, self).__init__(*args, **kwargs)

        self.init_leds()

    def _min_max_range_gen(self):
        if self.hue1 <= self.hue2:
            return [i for i in xrange(self.hue1, self.hue2)]
        else:
            range_top = [i for i in xrange(self.hue1, 255)]
            range_bot = [i for i in xrange(0, self.hue2)]
            return range_top + range_bot

    def init_leds(self):
        range_pattern = [i for i in pattern_list_fill(self.rangelen_pattern, self.led_count)]
        for led in self.leds:
            led.status = range_pattern[led.id]

    def run(self):
        while time.time() < self.t_end:
            new_buffer = deepcopy(self.buffer_header())
            for led in self.leds:
                led.do_step()
                new_buffer.extend(led.read_rgb())
            self.device.write(new_buffer)
            time.sleep(self.fade_time)


class ChaosPixel(BaseTwistedStep, AdaProtocolHandler):
    def __init__(self, *args, **kwargs):
        self.saturation = kwargs.pop('saturation', 255)
        self.value = kwargs.pop('value', 255)

        kwargs['state_kwargs'] = {
            "saturation": self.saturation,
            "value": self.value,
        }

        super(ChaosPixel, self).__init__(*args, **kwargs)

        self.init_leds()

    def init_leds(self):
        for led in self.leds:
            led.h = random.randint(1,255)
            led.status = led.id % 255

    def run(self):
        while time.time() < self.t_end:
            new_buffer = deepcopy(self.buffer_header())
            for led in self.leds:
                led.do_step()
                new_buffer.extend(led.read_rgb())
            self.device.write(new_buffer)
            time.sleep(self.fade_time)

if __name__ == "__main__":
    # for debugging
    s = DummySerialDevice()
    # s = serial.Serial(LED_PORT, 115200)
    # t = SimpleColorChaser(device=s, led_count=LED_COUNT, run_duration=LED_DURATION, fade_time=LED_FADE_TIME, fade_steps=LED_FADE_STEPS, state_storage=ChaserLEDState,
    # hue=128, fade_by=15, spacing=30)

    # t = SimpleShiftingColorChaser(device=s, led_count=LED_COUNT, run_duration=LED_DURATION, fade_time=LED_FADE_TIME,
    # fade_steps=LED_FADE_STEPS, state_storage=ChaserLEDState,
    # hue=0, fade_by=15, spacing=30)

    # t = RainbowChaser(device=s, led_count=LED_COUNT, run_duration=LED_DURATION, fade_time=LED_FADE_TIME, fade_steps=LED_FADE_STEPS, state_storage=RainbowLEDState)
    t = BouncyChaser(device=s, led_count=LED_COUNT, run_duration=LED_DURATION, fade_time=LED_FADE_TIME, fade_steps=LED_FADE_STEPS, state_storage=DualHueLEDState)

    t = MultiSimpleColorChaser(device=s, led_count=LED_COUNT, run_duration=LED_DURATION, fade_time=LED_FADE_TIME,
                               fade_steps=LED_FADE_STEPS, state_storage=MultiChaserLEDState,
                               hues=[0, 128], fade_by=15, spacing=30)

    t = MultiSimpleNoSpaceChaser(device=s, led_count=LED_COUNT, run_duration=LED_DURATION, fade_time=LED_FADE_TIME,
                                 fade_steps=LED_FADE_STEPS, state_storage=MultiNoSpaceChaseState,
                                 hues=[0, 128], spacing=15)

    # todo add some stuff that takes input of a few full HSV sets, so it can do 'murika mode
    t.run()
    s.close()