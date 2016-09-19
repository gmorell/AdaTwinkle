from itertools import chain
from helpers import HSVHelper
import random


class BaseLEDState(object):
    def __init__(self, r=0, g=0, b=0, step_size=3, id=0):
        self.r = r
        self.g = g
        self.b = b
        self.sz = step_size

        self.r_t = 0
        self.g_t = 0
        self.b_t = 0
        self.id = id

    # generic step function
    def _step(self, current, dest):
        if abs(current - dest) > self.sz:
            if current > dest:
                current -= self.sz
            elif current < dest:
                current += self.sz
            else:
                pass
        else:
            current = dest
        return current

    def at_target(self):
        raise NotImplementedError("Need to implement a stop function")

    def at_zeroes(self):  # for fading up or down
        raise NotImplementedError("Need to implement a reverse function")

    def read(self):
        raise NotImplementedError("Need to implement a read for internal state")

    def read_rgb(self):
        raise NotImplementedError("Need to implement a read for internal state (converted to RGB)")

    def read_t(self):
        raise NotImplementedError("Need to implement a read for internal target state")

    def read_t_rgb(self):
        raise NotImplementedError("Need to implement a read for internal target state (converted to RGB)")


class DumbRGBLEDStepState(BaseLEDState):
    """
    Steps around with no regard to maintaining consistent hues or anything else really
    """

    def at_target(self):  # to write the next values
        if self.r == self.r_t and self.g == self.g_t and self.b == self.b_t:
            return True
        else:
            return False

    def at_zeroes(self):  # for fading up or down
        return self.r == self.g == self.b == 0

    def set_step_target(self, r, g, b):
        self.r_t = r
        self.g_t = g
        self.b_t = b

    def set_step_target_to_zeroes(self):
        self.r_t = 0
        self.g_t = 0
        self.b_t = 0

    def do_step(self):
        self.r = self._step(self.r, self.r_t)
        self.g = self._step(self.g, self.g_t)
        self.b = self._step(self.b, self.b_t)

    def read(self):
        return [self.r, self.g, self.b]

    def read_rgb(self):
        return [self.r, self.g, self.b]

    def read_t(self):
        return [self.r_t, self.g_t, self.b_t]

    def read_t_rgb(self):
        return [self.r_t, self.g_t, self.b_t]


class HSVAwareLEDStepState(BaseLEDState, HSVHelper):
    def __init__(self, hue=0, saturation=0, value=0, step_size=1, id=0):
        self.h = hue
        self.s = saturation
        self.v = value
        self.sz = step_size
        self.id = id

        self.h_t = 0
        self.s_t = 0
        self.v_t = 0

    def at_zeroes(self):
        return self.s == self.v == 0

    def at_target(self):  # to write the next values
        if self.h == self.h_t and self.s == self.s_t and self.v == self.v_t:
            return True
        else:
            return False

    def set_step_target(self, r, g, b):
        h, s, v = self._rgb_to_hsv(r, g, b)
        self.h_t = h
        self.s_t = 255
        self.v_t = 255

    def set_step_target_to_zeroes(self):
        self.s_t = 0
        self.v_t = 0

    def do_step(self):
        self.h = self._step(self.h, self.h_t)
        self.s = self._step(self.s, self.s_t)
        self.v = self._step(self.v, self.v_t)

    def read(self):
        return [self.h, self.s, self.v]

    def read_rgb(self):
        r, g, b = self._hsv_to_rgb(self.h, self.s, self.v)
        return [int(r), int(g), int(b)]

    def read_t(self):
        return [self.h_t, self.s_t, self.v_t]

    def read_t_rgb(self):
        r, g, b = self._hsv_to_rgb(self.h_t, self.s_t, self.v_t)
        return [r, g, b]


class ChaserLEDState(BaseLEDState, HSVHelper):  # kinda like a cylon
    def __init__(self, id, hue=0, spacing=30, fade_by=20, status=0):
        self.id = id
        self.h = hue
        self.s = 255
        self.v = 0
        self.spacing = spacing
        self.fade_by = fade_by
        self.window = 255 / (self.spacing - self.fade_by)

        self.status = status  # this gets set later

    def color_from_status(self):
        if self.fade_by < self.status < self.spacing:
            self.v = self.window * (self.status % self.fade_by)
        else:
            self.v = 0

    def set_status(self, value):  # useful for init
        self.status = value
        self.color_from_status()

    def do_step(self):
        self.status = (self.status + 1) % self.spacing
        self.color_from_status()

    def read_rgb(self):
        r, g, b = self._hsv_to_rgb(self.h, self.s, self.v)
        return [int(r), int(g), int(b)]

class MultiChaserLEDState(BaseLEDState, HSVHelper):
    def __init__(self, id, hues=[0,64,128], spacing=30, fade_by=20, status=0):
        self.id = id
        self.hs = hues
        self.hc = len(hues)
        self.h = 0  # gets set later
        self.s = 255
        self.v = 0
        self.spacing = spacing
        self.fade_by = fade_by
        self.window = 255 / (self.spacing - self.fade_by)

        self.status = status

        self.statushues = list(chain.from_iterable([[x for i in xrange(self.spacing)] for x in self.hs]))
        # print self.statushues

    def color_from_status(self):
        self.h = self.statushues[self.status]

        # brightness is diff here
        if self.fade_by < self.status % self.spacing < self.spacing:
            self.v = self.window * (self.status % self.fade_by)

        else:
            self.v = 0

    def do_step(self):
        self.status = (self.status + 1) % (self.spacing * self.hc)
        # if self.id == 1: print "STATUS %s %s %s" % (self.status, self.h, self.v)

        self.color_from_status()

    def read_rgb(self):
        r, g, b = self._hsv_to_rgb(self.h, self.s, self.v)
        return [int(r), int(g), int(b)]

class MultiNoSpaceChaseState(BaseLEDState, HSVHelper):
    def __init__(self, id, hues, spacing, status=0):
        self.id = id
        self.hs = hues
        self.hc = len(hues)
        self.h = 0  # gets set later
        self.s = 255
        self.v = 255

        self.spacing = spacing
        self.status = status

        self.statushues = list(chain.from_iterable([[x for i in xrange(self.spacing)] for x in self.hs]))

    def color_from_status(self):
        self.h = self.statushues[self.status]

    def do_step(self):
        self.status = (self.status + 1) % (self.spacing * self.hc)
        self.color_from_status()

    def read_rgb(self):
        r, g, b = self._hsv_to_rgb(self.h, self.s, self.v)
        return [int(r), int(g), int(b)]

class RainbowLEDState(BaseLEDState, HSVHelper):
    def __init__(self, id, status=0, saturation=255, value=255, stepsize=1):
        self.id = id
        self.status = status
        self.h = 0
        self.s = saturation
        self.v = value
        self.stepsize = stepsize

    def set_status(self, value):  # useful for init
        self.status = value

    def do_step(self):
        self.status = (self.status + self.stepsize) % 256
        self.h = self.status

    def read_rgb(self):
        r, g, b = self._hsv_to_rgb(self.h, self.s, self.v)
        return [int(r), int(g), int(b)]


class DualHueLEDState(BaseLEDState, HSVHelper):
    def __init__(self, id, status=0, saturation=255, value=255, stepsize=1, hue1=0, hue2=0, **kwargs):
        self.id = id
        self.status = status
        self.sz = stepsize

        self.h_1 = hue1
        self.h_2 = hue2
        self.s = saturation
        self.v = value

        self.target = hue1
        self.hue_range = self._min_max_range_gen()
        self.hue_count = len(self.hue_range) - 1

        self.target = len(self.hue_range) -1

    def set_status(self, value):
        self.status = value

    def _min_max_range_gen(self):
        if self.h_1 <= self.h_2:
            return [i for i in xrange(self.h_1, self.h_2+1)]
        else:
            range_top = [i for i in xrange(self.h_1, 256)]
            range_bot = [i for i in xrange(0, self.h_2+1)]
            return range_top + range_bot

    def do_step(self):
        if self.at_target():
            if self.target == 0:
                self.target = self.hue_count
            else:
                self.target = 0

        self.status = self._step(self.status, self.target)

    def at_target(self):
        return self.status == self.target

    def read_rgb(self):
        r, g, b = self._hsv_to_rgb(self.hue_range[self.status], self.s, self.v)
        return [int(r), int(g), int(b)]

        # from led_states import DualHueLEDState
        # x = DualHueLEDState(id=0, hue1=30, hue2=40)
        # x.do_step(), x.at_target(), x.status, x.target


class ChaoticPixelState(BaseLEDState, HSVHelper):
    def __init__(self, hue=0, saturation=0, value=0, step_size=1, id=0):
        self.h = hue
        self.s = saturation
        self.v = value
        self.sz = step_size
        self.id = id

        self.h_t = 0

    def at_zeroes(self):
        return self.s == self.v == 0

    def at_target(self):  # to write the next values
        if self.h == self.h_t:
            return True
        else:
            return False

    def set_new_step_target(self):
        choice = random.randint(1,255)
        self.h_t = choice

    def do_step(self):
        self.h = self._step(self.h, self.h_t)
        if self.at_target():
            self.set_new_step_target()

    def read_rgb(self):
        r, g, b = self._hsv_to_rgb(self.h, self.s, self.v)
        return [int(r), int(g), int(b)]


class EntropicPixelState(BaseLEDState, HSVHelper):
    def __init__(self, hue=0, saturation=0, value=0, step_size=1, id=0, max_cycles=36): #cycleswas12,stepwas3
        self.h = hue
        self.s = saturation
        self.v = value
        self.sz = step_size
        self.id = id

        self.h_t = 0
        self.cycles_max = max_cycles
        self.cycles_state = 0

    def at_zeroes(self):
        return self.s == self.v == 0

    def at_target(self):  # to write the next values
        if self.h == self.h_t:
            # self.cycles_state += 1
            # TODO:
            # add a lock in a diff version of the class with this enabled
            # for the final_extra_group function to find,
            # and when all are set to the lock, unlock
            return True
        else:
            return False

    def set_new_step_target(self, target=None):
        if not target:
            choice = random.randint(1,255)
            self.h_t = choice

        else:
            self.h_t = target

    def do_step(self):
        self.h = self._step(self.h, self.h_t)
        if self.at_target():
            self.set_new_step_target()

        self.cycles_state += 1

    def read_rgb(self):
        r, g, b = self._hsv_to_rgb(self.h, self.s, self.v)
        return [int(r), int(g), int(b)]