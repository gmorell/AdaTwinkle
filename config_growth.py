from filters.colors import RGBtoGRBLambentOutputFilter, InvertLambentOutputFilter, PercentageBrightnessReduc50, \
    PercentageBrightnessReduc66, PercentageBrightnessReduc75, PercentageBrightnessReduc80, PercentageBrightnessReduc90, \
    NeonOutputFilter, PastelOutputFilter, DarkenedOutputFilter
from growth_mortality.states import BaseGMStateHSV
from growth_mortality.steps import GrowthAndMortality, GAMLeaves
from lambents.test_patterns import TestRunner
from minmax.states import MinMaxHSVState
from minmax.steps import MinMaxHSVStep
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
    "solid.pink":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 255,
            "g": 0,
            "b": 255,
        },
        "grouping": "solid",
        "display": "Solid - Pink",
    },
    "solid.white":{
        "class": SolidRGB,
        "kwargs": {
            "state_storage": SolidRGBState,
            "r": 255,
            "g": 255,
            "b": 255,
        },
        "grouping": "solid",
        "display": "Solid - Full White",
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