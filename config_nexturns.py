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