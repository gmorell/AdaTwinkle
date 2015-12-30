from ada_protocol import BaseTwistedStep, AdaProtocolHandler
from led_states import BaseLEDState

class TestRunner(BaseTwistedStep, AdaProtocolHandler):
    def __init__(self, *args, **kwargs):
        if "state_storage" not in kwargs:
            kwargs['state_storage'] = TestPatternRGBBetween
        if hasattr(self, "state_kwargs"):
            kwargs['state_kwargs'] = self.state_kwargs
        super(TestRunner, self).__init__(*args, **kwargs)

class TestPatternRGBBetween(BaseLEDState):
    def __init__(self, ticks=100, **kwargs):
        super(TestPatternRGBBetween, self).__init__(**kwargs)
        self.ticks = ticks
        self.vals = [(255,0,0),(255,255,0),(0,255,0),(0,255,255),(0,0,255,),(255,0,255),(0,0,0),(255,255,255),(0,0,0)]
        self.init_list()

    def init_list(self):
        wrap  = []
        for v in self.vals:
            wrap.extend([v] * self.ticks)

        self.value_list = wrap

    def do_step(self):
        if self.value_list:
            self.r, self.g, self.b = self.value_list.pop(0)
            print self.r
        else:
            print "RE-INIT"
            self.init_list()

    def read_rgb(self):
        return [self.r, self.g, self.b]