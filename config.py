from filters.colors import RGBtoGRBLambentOutputFilter, InvertLambentOutputFilter, PercentageBrightnessReduc50, \
    PercentageBrightnessReduc66, PercentageBrightnessReduc75, PercentageBrightnessReduc80, PercentageBrightnessReduc90, \
    NeonOutputFilter, PastelOutputFilter, DarkenedOutputFilter
from growth_mortality.states import BaseGMStateHSV
from growth_mortality.steps import GrowthAndMortality, GAMLeaves
from lambents.test_patterns import TestRunner
from simpleprogs import WaitingCounter, DoubleWaitingCounter
from led_states import ChaserLEDState, RainbowLEDState, DualHueLEDState, MultiChaserLEDState, MultiNoSpaceChaseState, \
    HSVAwareLEDStepState, ChaoticPixelState, EntropicPixelState
from run_chaser import SimpleColorChaser, SimpleShiftingColorChaser, ChaosPixel, EntropicPixel
from run_chaser import RainbowChaser, BouncyChaser
from run_chaser import MultiSimpleColorChaser, MultiSimpleNoSpaceChaser
from solids.states import SolidRGBState
from solids.steps import SolidRGB
from standby import StandbyRunner, StandbyFadeRunner

avail_progs = {
    "default": {
        "class": WaitingCounter,
        "kwargs": {},
        "display": "Default",
    },
    "standby": {
        "class": StandbyRunner,
        "kwargs": {},
        "grouping": "waiting",
        "display": "Standby",
    },
    "standbyfade": {
        "class": StandbyFadeRunner,
        "kwargs": {},
        "grouping": "waiting",
        "display": "Standby w/ Fade",
    },
    "scc.blue": {
        "class": SimpleColorChaser,
        "kwargs": {
            "state_storage": ChaserLEDState,
            "hue": 128,
            "fade_by": 15,
            "spacing": 30,
        },
        "grouping":"cchaser",
        "display": "SimpleColorChaser - Blue",
    },
    "scc.red": {
        "class": SimpleColorChaser,
        "kwargs": {
            "state_storage": ChaserLEDState,
            "hue": 0,
            "fade_by": 15,
            "spacing": 30,
        },
        "grouping":"cchaser",
        "display": "SimpleColorChaser - Red",
    },
    "sscc": {
        "class": SimpleShiftingColorChaser,
        "kwargs": {
            "state_storage": ChaserLEDState,
            "hue": 0,
            "fade_by": 15,
            "spacing": 30
        },
        "grouping":"cchaser",
        "display": "SimpleShiftingColorChaser",
    },
    "rainbow": {
        "class": RainbowChaser,
        "kwargs": {
            "state_storage": RainbowLEDState,
        },
        "grouping":"hchaser",
        "display": "Chaser - Rainbow",
    },
    "bouncy": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState
        },
        "grouping":"hchaser",
        "display": "Chaser - Vista",
    },
    "love": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 230,
            "hue2": 20,
        },
        "grouping":"hchaser",
        "display": "Chaser - Love",
    },
    "ocean": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 90,
            "hue2": 160,
        },
        "grouping":"hchaser",
        "display": "Chaser - Ocean",
    },
    "forest": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 60,
            "hue2": 90,
        },
        "grouping":"hchaser",
        "display": "Chaser - Forest",
    },
    "royal": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 190,
            "hue2": 210,
        },
        "grouping":"hchaser",
        "display": "Chaser - Royal",
    },
    "sunny": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 34,
            "hue2": 42,
        },
        "grouping":"hchaser",
        "display": "Chaser - Sunny",
    },
    "night": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 245,
            "hue2": 10,
            "value": 60
        },
        "grouping":"hchaser",
        "display": "Chaser - Night",
    },
    "mscc": {
        "class": MultiSimpleColorChaser,
        "kwargs": {
            "state_storage": MultiChaserLEDState,
            "hues": [0, 128],
            "fade_by": 15,
            "spacing": 30
        },
        "grouping":"cchaser",
        "display": "Multi-Chaser - Red/Blue",
    },
    "msnsc": {
        "class": MultiSimpleNoSpaceChaser,
        "kwargs": {
            "state_storage": MultiNoSpaceChaseState,
            "hues": [0, 64, 128, 192],
            "spacing": 15,
        },
        "grouping":"cchaser",
        "display": "Multi-Chaser - 0/64/128/192",
    },
    "chaos": {
        "class": ChaosPixel,
        "kwargs": {
            "state_storage": ChaoticPixelState,
        },
        "grouping":"rando",
        "display": "Chaos",
    },
    "entropy": {
        "class": EntropicPixel,
        "kwargs" : {
            "state_storage": EntropicPixelState
        },
        "grouping":"rando",
        "display": "Entropy",
    },
    "seafoam": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 90,
            "hue2": 160,
        },
        "grouping":"filterpile",
        "display": "Seafoam - TEST",
    },
    "leaves": {
        "class": GAMLeaves,
        "kwargs": {
            "state_storage": BaseGMStateHSV,
            "growth_hues": [90, 98, 94, 95, 90],
            "death_hues": [90, 95, 85, 90, 80, 85, 75, 80, 70, 75, 65, 70, 60, 65, 55, 60, 50, 55, 45, 50, 40, 45, 35, 40, 30, 35, 25, 30, 20, 25, 15, 20, 10, 15, 5, 10, 0]
        },
        "grouping":"growth_mortality",
        "display": "Leaves - TEST",
    },
    # "test.sweep": {
    #     "class":TestRunner,
    #     "grouping": "test",
    #     "display": "TEST - SWEEP",
    # },
    "solid.ww":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 255,
            "g": 255,
            "b": 190,
        },
        "grouping": "solid",
        "display": "Solid - Warm White",
    },
    "solid.h4x":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 0,
            "g": 102,
            "b": 202,
        },
        "grouping": "solid",
        "display": "Solid - h4xmb blue",
    },
    "solid.ruby":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 155,
            "g": 17,
            "b": 30,
        },
        "grouping": "solid",
        "display": "Solid - Ruby",
    },
    "solid.emerald":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 4,
            "g": 93,
            "b": 28,
        },
        "grouping": "solid",
        "display": "Solid - Emerald",
    },
    "solid.gold":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 255,
            "g": 215,
            "b": 0,
        },
        "grouping": "solid",
        "display": "Solid - Gold",
    },
    "solid.coffee":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 117,
            "g": 86,
            "b": 56,
        },
        "grouping": "solid",
        "display": "Solid - Coffee",
    }
}

avail_filters = {
    "GRB": RGBtoGRBLambentOutputFilter,
    "INV": InvertLambentOutputFilter,

    # Reductions
    "R50": PercentageBrightnessReduc50,
    "R66": PercentageBrightnessReduc66,
    "R75": PercentageBrightnessReduc75,
    "R80": PercentageBrightnessReduc80,
    "R90": PercentageBrightnessReduc90,
    # output
    "ONE": NeonOutputFilter,
    "OPA": PastelOutputFilter,
    "ODO": DarkenedOutputFilter,
}