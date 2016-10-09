import random

from helpers import convert_hsv_rgb_int
from led_states import BaseLEDState


class MinMaxHSVState(BaseLEDState):
    def __init__(self, min, max, sat, val, **kwargs):
        self.min = min
        self.max = max
        self.sat = sat
        self.val = val

        self.hue = self._get_minmax(self.min, self.max)

    def _get_minmax(self, mini, maxi):
        if mini <= maxi:
            h_ = random.randint(mini, maxi)
        else:  # we do a clever wrap-around
            min_a = mini
            max_a = 255

            min_b = 0
            max_b = maxi

            ch = random.choice(['a', 'b'])
            if ch == 'a':
                h_ = random.randint(min_a, max_a)
            elif ch == 'b':
                h_ = random.randint(min_b, max_b)

        return h_

    def read_rgb(self):
        return convert_hsv_rgb_int(self.hue, self.sat, self.val)

    def do_step(self):
        self.hue = self._get_minmax(self.min, self.max)