from ada_protocol import BaseTwistedStep, AdaProtocolHandler
from growth_mortality.states import BaseGMStateHSV


class GrowthAndMortality(BaseTwistedStep, AdaProtocolHandler):
    def __init__(self, *args, **kwargs):
        if "state_storage" not in kwargs:
            kwargs['state_storage'] = BaseGMStateHSV
        if hasattr(self, "state_kwargs"):
            kwargs['state_kwargs'] = self.state_kwargs
        super(GrowthAndMortality, self).__init__(*args, **kwargs)

class GAMLeaves(GrowthAndMortality):
    state_kwargs = {
        # "growth_hues": [110, 98, 100, 111, 99],
        "growth_hues": [90, 98, 94, 95, 90],
        "death_hues": [90, 95, 85, 90, 80, 85, 75, 80, 70, 75, 65, 70, 60, 65, 55, 60, 50, 55, 45, 50, 40, 45, 35, 40, 30, 35, 25, 30, 20, 25, 15, 20, 10, 15, 5, 10, 0]
    }