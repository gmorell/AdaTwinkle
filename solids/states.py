from led_states import BaseLEDState


class SolidRGBState(BaseLEDState):
    def __init__(self, r=255, g=255, b=255, **kwargs):
        self.r = r
        self.g = g
        self.b = b

    def read_rgb(self):
        return [self.r, self.g, self.b]

    def do_step(self):
        pass