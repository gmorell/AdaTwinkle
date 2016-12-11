from ada_protocol import BaseTwistedStep, AdaProtocolHandler
from twinklers.states import BaseTwinkleState


class TwinklerBase(BaseTwistedStep, AdaProtocolHandler):
    state_kwargs = {}
    surprises = []
    chance = 4

    def __init__(self, *args, **kwargs):
        if "state_storage" not in kwargs:
            kwargs['state_storage'] = BaseTwinkleState
        if hasattr(self, "state_kwargs"):
            kwargs['state_kwargs'] = self.state_kwargs

        kwargs['state_kwargs']['surprises'] = kwargs.pop("surprises", self.surprises)
        kwargs['state_kwargs']['surprise_chance'] = kwargs.pop("chance", self.chance)

        super(TwinklerBase, self).__init__(*args, **kwargs)


class TwinklerGreen(TwinklerBase):
    surprises = [
        [50, 200, 50],
    ]

class TwinklerRed(TwinklerBase):
    surprises = [
        [255, 50, 50],
    ]

class TwinklerRedGreen(TwinklerBase):
    surprises = [
        [255, 50, 50],
        [50, 200, 50],
    ]

class TwinklerPurp(TwinklerBase):
    surprises = [
        [150, 0, 210],
    ]

class TwinklerBlue(TwinklerBase):
    surprises = [
        [0, 102, 202],
    ]

class TwinklerWintry(TwinklerBase):
    surprises = [
        [0, 102, 202],
        [47, 141, 179],
        [91,165,194],
        [141, 198, 217],
        [229,244,249]
    ]
    chance = 14

class TwinklerAmber(TwinklerBase):
    surprises = [
        [255, 191, 0],
    ]

class TwinklerAmberRed(TwinklerBase):
    surprises = [
        [255, 191, 0],
        [255, 50, 50],
    ]


class TwinklerAll(TwinklerBase):
    surprises = [
        [0, 102, 202],
        [150, 0, 210],
        [255, 50, 50],
        [50, 200, 50],
        [255, 191, 0],

        [0, 69, 129],
        [1, 138, 189],
    ]

class TwinklerAllButMore(TwinklerBase):
    surprises = [
        [0, 102, 202],
        [150, 0, 210],
        [255, 50, 50],
        [50, 200, 50],
        [255, 191, 0],
    ]
    chance = 10