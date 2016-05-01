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
        "kwargs": {}
    },
    "standby": {
        "class": StandbyRunner,
        "kwargs": {},
        "grouping": "waiting"
    },
    "standbyfade": {
        "class": StandbyFadeRunner,
        "kwargs": {},
        "grouping": "waiting"
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
    },
    "rainbow": {
        "class": RainbowChaser,
        "kwargs": {
            "state_storage": RainbowLEDState,
        },
        "grouping":"hchaser",
    },
    "bouncy": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState
        },
        "grouping":"hchaser",
    },
    "love": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 230,
            "hue2": 20,
        },
        "grouping":"hchaser",
    },
    "ocean": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 90,
            "hue2": 160,
        },
        "grouping":"hchaser",
    },
    "forest": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 60,
            "hue2": 90,
        },
        "grouping":"hchaser",
    },
    "royal": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 190,
            "hue2": 210,
        },
        "grouping":"hchaser",
    },
    "sunny": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 34,
            "hue2": 42,
        },
        "grouping":"hchaser",
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
    },
    "msnsc": {
        "class": MultiSimpleNoSpaceChaser,
        "kwargs": {
            "state_storage": MultiNoSpaceChaseState,
            "hues": [0, 64, 128, 192],
            "spacing": 15,
        },
        "grouping":"cchaser",
    },
    "chaos": {
        "class": ChaosPixel,
        "kwargs": {
            "state_storage": ChaoticPixelState,
        },
        "grouping":"rando",
    },
    "entropy": {
        "class": EntropicPixel,
        "kwargs" : {
            "state_storage": EntropicPixelState
        },
        "grouping":"rando",
    },
    "seafoam": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 90,
            "hue2": 160,
        },
        "grouping":"filterpile",
    },
    "leaves": {
        "class": GAMLeaves,
        "kwargs": {
            "state_storage": BaseGMStateHSV,
        },
        "grouping":"growth_mortality",
    },
    "test.sweep": {
        "class":TestRunner,
        "grouping": "test"
    },
    "solid.ww":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 255,
            "g": 255,
            "b": 190,
        },
        "grouping": "solid"
    },
    "solid.h4x":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 0,
            "g": 102,
            "b": 202,
        },
        "grouping": "solid"
    },
    "solid.ruby":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 155,
            "g": 17,
            "b": 30,
        },
        "grouping": "solid"
    },
    "solid.emerald":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 4,
            "g": 93,
            "b": 28,
        },
        "grouping": "solid"
    },
    "solid.gold":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 255,
            "g": 215,
            "b": 0,
        },
        "grouping": "solid"
    },
    "solid.coffee":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 117,
            "g": 86,
            "b": 56,
        },
        "grouping": "solid"
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