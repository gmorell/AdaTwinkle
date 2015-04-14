class WaitingCounter(object):
    def __init__(self, val=0, **kwargs):
        self.counter = val

    def step(self):
        self.counter += 1

    def reset(self):
        self.counter = 0

    def proto_value(self):
        return "Waiting for command for %s seconds" % (self.counter / 10)


class DoubleWaitingCounter(WaitingCounter):
    def step(self):
        self.counter += 10