from filters.colors import RGBtoGRBLambentOutputFilter, InvertLambentOutputFilter
from growth_mortality.states import BaseGMStateHSV
from growth_mortality.steps import GrowthAndMortality, GAMLeaves
from simpleprogs import WaitingCounter, DoubleWaitingCounter
from led_states import ChaserLEDState, RainbowLEDState, DualHueLEDState, MultiChaserLEDState, MultiNoSpaceChaseState, \
    HSVAwareLEDStepState, ChaoticPixelState, EntropicPixelState
from run_chaser import SimpleColorChaser, SimpleShiftingColorChaser, ChaosPixel, EntropicPixel
from run_chaser import RainbowChaser, BouncyChaser
from run_chaser import MultiSimpleColorChaser, MultiSimpleNoSpaceChaser
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

}

avail_filters = {
    "GRB": RGBtoGRBLambentOutputFilter,
    "INV": InvertLambentOutputFilter,
}