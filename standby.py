from ada_protocol import BaseTwistedStep


class StandbyLED(object):
    def __init__(self, **kwargs):
        pass

    def read_rgb(self):
        return [0, 0, 0]


class StandbyRunner(BaseTwistedStep):
    def __init__(self, *args, **kwargs):
        self.device = kwargs.pop("device")
        self.led_count = kwargs.pop("led_count")
        # super(StandbyRunner, self).__init__(*args, **kwargs)

    def step(self):
        self.device.write([0 for i in xrange(3 * self.led_count)])


class StandbyFadeRunner(BaseTwistedStep):
    def __init__(self, *args, **kwargs):
        self.device = kwargs.pop("device")
        self.led_count = kwargs.pop("led_count")
        self.transitions_list = []
        self.leds = [StandbyLED() for i in xrange(3 * self.led_count)]
        # super(StandbyRunner, self).__init__(*args, **kwargs)

    def step(self):
        if self.transitions_list:
            print self.transitions_list
            self.device.write(self.transitions_list.pop(0))
        else:
            self.device.write([0 for i in xrange(3 * self.led_count)])
