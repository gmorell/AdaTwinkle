from ada_protocol import AdaProtocolHandler, BaseTwistedStep


class MinMaxHSVStep(AdaProtocolHandler, BaseTwistedStep):
    def __init__(self, *args, **kwargs):
        self.min = kwargs.pop("min")
        self.max = kwargs.pop("max")
        self.sat = kwargs.pop("sat",255)
        self.val = kwargs.pop("val",255)
        self.id = kwargs.pop('id', 0)
        kwargs['state_kwargs'] = {"min": self.min, "max": self.max, "sat": self.sat, "val": self.val}
        super(MinMaxHSVStep, self).__init__(*args, **kwargs)
        self.transitions_list = []