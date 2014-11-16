from copy import deepcopy
import random
import serial
import time

# vars
from led_states import DumbRGBLEDStepState,HSVAwareLEDStepState

LED_COUNT = 240
LED_PORT = "/dev/ttyACM0"
LED_DURATION = 600
LED_FADE_TIME = 0.05
LED_FADE_STEPS = 30


class LEDStringTwinkle(object):
    def __init__(self, led_count, run_duration, fade_time, fade_steps, device, twinkle_hues=[], fadeout=True,
                 debug=False, state=DumbRGBLEDStepState):
        self.led_count = led_count
        self.run_duration = run_duration
        self.fade_time = fade_time
        self.fade_steps = fade_steps
        self.hues = twinkle_hues
        self.device = device
        self.fadeout = fadeout
        self.debug = debug

        # figure out when to stop
        self.t_start = time.time()
        self.t_end = self.t_start + self.run_duration

        # create objects for tracking LED states
        self.leds = [state(id=i) for i in range(self.led_count)]

        # create the send buffer
        buffer_start = ['\x41', '\x64', '\x61']
        buffer_3 = (self.led_count - 1) >> 8
        buffer_4 = (self.led_count - 1) & 0xff
        buffer_5 = buffer_3 ^ buffer_4 ^ 0x55
        self.buffer_complete = buffer_start + [buffer_3, buffer_4, buffer_5]

    def dprint(self, string):
        if self.debug:
            print(string)

    def run(self):
        while time.time() < self.t_end:
            new_buffer = deepcopy(self.buffer_complete)
            for led in self.leds:
                if led.at_target():  # we set values here
                    self.dprint("@target")
                    if led.at_zeroes():  # we input new colors here
                        self.dprint("@zeroes")
                        # for now just twinkle to some random orange, we'll do hue juggling next
                        led.set_step_target(
                            random.randint(192, 255),
                            random.randint(0, 64),
                            0,  # random.randint(0,128),
                        )

                    else:
                        led.set_step_target(
                            0, 0, 0
                        )

                led.do_step()
                new_buffer.extend(led.read_rgb())

            self.device.write(new_buffer)
            time.sleep(self.fade_time)

        # fadeout
        if self.fadeout:
            for l in self.leds:
                l.set_step_target(0, 0, 0)

            while not all([l.at_zeroes() for l in self.leds]):
                new_buffer = deepcopy(self.buffer_complete)
                for led in self.leds:
                    if led.at_target() and led.at_zeroes():
                        pass
                    else:
                        led.do_step()
                    new_buffer.extend(led.read_rgb())

                self.device.write(new_buffer)
                time.sleep(self.fade_time)


s = serial.Serial(LED_PORT, 115200)

t = LEDStringTwinkle(LED_COUNT, LED_DURATION, LED_FADE_TIME, LED_FADE_STEPS, s, [0], state=HSVAwareLEDStepState)
t.run()

s.close()

# ##

## TODO
# LED_HOLD : int: hold a value at its peak for x cycles. (remember to reset the hold after its done)
# LED_HOLD_LOW: bool to do this when we're zeroed
# hue mode: add in list of hues and we can pick colors eg halloween mode [yellow, read, orange, puple] xmas [greens, reds, whites] murica [reds, whites, blues]
#        also a "huestep" so that the colors stay consistent eg dark orange to oranger, vs green -> yellow -> orange as there are far more red levels to step thru
