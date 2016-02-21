from ada_protocol import AdaProtocolHandler, BaseTwistedStep


class SolidRGB(AdaProtocolHandler, BaseTwistedStep):
    def __init__(self, *args, **kwargs):
        self.r = kwargs.pop('r', 255)
        self.g = kwargs.pop('g', 255)
        self.b = kwargs.pop('b', 255)
        kwargs['state_kwargs'] = {"r": self.r, "g": self.g, "b": self.b}
        super(SolidRGB, self).__init__(*args, **kwargs)
        self.transitions_list = []

    #     self.init_leds()
    #
    # def init_leds(self):
    #     for led in self.leds:
    #         led.r, led.g, led,b = self.r, self.g, self.b