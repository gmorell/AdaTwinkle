from simpleprogs import WaitingCounter, DoubleWaitingCounter
from led_states import ChaserLEDState, RainbowLEDState, DualHueLEDState, MultiChaserLEDState, MultiNoSpaceChaseState
from run_chaser import SimpleColorChaser, SimpleShiftingColorChaser, RainbowChaser, BouncyChaser, \
    MultiSimpleColorChaser, \
    MultiSimpleNoSpaceChaser

avail_progs = {
    "default": {
        "class": WaitingCounter,
        "kwargs": {}
    },
    "alt": {
        "class": DoubleWaitingCounter,
        "kwargs": {}
    },
    "scc.blue": {
        "class": SimpleColorChaser,
        "kwargs": {
            "state_storage": ChaserLEDState,
            "hue": 128,
            "fade_by": 15,
            "spacing": 30,
        }
    },
    "scc.red": {
        "class": SimpleColorChaser,
        "kwargs": {
            "state_storage": ChaserLEDState,
            "hue": 0,
            "fade_by": 15,
            "spacing": 30,
        }
    },
    "sscc": {
        "class": SimpleShiftingColorChaser,
        "kwargs": {
            "state_storage": ChaserLEDState,
            "hue": 0,
            "fade_by": 15,
            "spacing": 30
        }
    },
    "rainbow": {
        "class": RainbowChaser,
        "kwargs": {
            "state_storage": RainbowLEDState,
        }
    },
    "bouncy": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState
        }
    },
    "love": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 230,
            "hue2": 20,
        }
    },
    "ocean": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 90,
            "hue2": 160,
        }
    },
    "forest": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 60,
            "hue2": 90,
        }
    },
    "royal": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 190,
            "hue2": 210,
        }
    },
    "sunny": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 34,
            "hue2": 42,
        }
    },
    "night": {
        "class": BouncyChaser,
        "kwargs": {
            "state_storage": DualHueLEDState,
            "hue1": 245,
            "hue2": 10,
            "value": 60
        }
    },
    "mscc": {
        "class": MultiSimpleColorChaser,
        "kwargs": {
            "state_storage": MultiChaserLEDState,
            "hues": [0, 128],
            "fade_by": 15,
            "spacing": 30
        }
    },
    "msnsc": {
        "class": MultiSimpleNoSpaceChaser,
        "kwargs": {
            "state_storage": MultiNoSpaceChaseState,
            "hues": [0, 64, 128, 192],
            "spacing": 15,
        }
    }
}