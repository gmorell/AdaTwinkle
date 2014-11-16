from helpers import HSVHelper


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
    def __init__(self, h=0, s=0, v=0, step_size=3, id=0):
        self.h = h
        self.s = s
        self.v = v
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
        h,s,v = self._rgb_to_hsv(r, g, b)
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

class ChaserLEDState(BaseLEDState, HSVHelper): # kinda like a cylon
    def __init__(self, id, hue=0, spacing=30, fade_by=20, status=0):
        self.id = id
        self.h = hue
        self.s = 255
        self.v = 0
        self.spacing = spacing
        self.fade_by = fade_by
        self.window = 255 / (self.spacing - self.fade_by)

        self.status = status # this gets set later

    def color_from_status(self):
        if self.fade_by < self.status < self.spacing:
            self.v = self.window * (self.status % self.fade_by)
        else:
            self.v = 0

    def set_status(self, value): # useful for init
        self.status = value
        # todo set the color here too

    def do_step(self):
        self.status = (self.status + 1) % self.spacing
        self.color_from_status()

    def read_rgb(self):
        r, g, b = self._hsv_to_rgb(self.h, self.s, self.v)
        return [int(r), int(g), int(b)]
