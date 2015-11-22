from helpers import HSVHelper
from led_states import BaseLEDState
import random


class BaseLambentHSVState(BaseLEDState, HSVHelper):
    def _expand_hue_list(self, hues):
        out = []
        for h in hues:
            if type(h) == type(int()):
                if 0 < h < 255:
                    out.append(h)
            elif type(h) == type(list()):
                # clamp the values
                first = max(h[0],0)
                last = min(h[-1], 255)
                out.append([i for i in xrange(h[0], h[1]+1)])

        return out

    def __init__(self, available_hues):
        self.hue_list = available_hues
        self.hue_list_expanded = self._expand_hue_list(self.hue_list)

    def at_target(self):
        return self.status == self.target

    def set_rand_target(self):
        target_hue = random.choice(self.hue_list_expanded)
        target_saturation = random.randint(192,255)
        target_value = random.randint(192,255)
        self.target = (target_hue, target_saturation, target_value)

    def do_step(self):
        if self.at_target():
            if self.target == (0,0,0):
                self.set_rand_target()
            else:
                self.target = (0,0,0)