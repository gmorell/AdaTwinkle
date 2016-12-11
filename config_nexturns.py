from filters.colors import RGBtoGRBLambentOutputFilter, InvertLambentOutputFilter, PercentageBrightnessReduc50, \
    PercentageBrightnessReduc66, PercentageBrightnessReduc75, PercentageBrightnessReduc80, PercentageBrightnessReduc90, \
    NeonOutputFilter, PastelOutputFilter, DarkenedOutputFilter
from minmax.states import MinMaxHSVState
from minmax.steps import MinMaxHSVStep
from simpleprogs import WaitingCounter
from solids.states import SolidRGBState
from solids.steps import SolidRGB
from standby import StandbyRunner, StandbyFadeRunner
from twinklers.states import BaseTwinkleState
from twinklers.steps import TwinklerBase, TwinklerRedGreen, TwinklerPurp, TwinklerBlue, TwinklerGreen, TwinklerRed, \
    TwinklerAll, TwinklerAmber, TwinklerAllButMore, TwinklerWintry, TwinklerAmberRed

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
    },
    "minmax.warm":{
        "class": MinMaxHSVStep,
        "kwargs": {
            "state_storage": MinMaxHSVState,
            "min": 192,
            "max": 15,
        },
        "grouping": "minmax",
        "display": "MINMAX - Warm",
    },
    "minmax.fire":{
        "class": MinMaxHSVStep,
        "kwargs": {
            "state_storage": MinMaxHSVState,
            "min": 0,
            "max": 24,
        },
        "grouping": "minmax",
        "display": "MINMAX - Fire",
    },
    "minmax.cool":{
        "class": MinMaxHSVStep,
        "kwargs": {
            "state_storage": MinMaxHSVState,
            "min": 100,
            "max": 200,
        },
        "grouping": "minmax",
        "display": "MINMAX - Warm",
    },
    "minmax.bouncy":{
        "class": MinMaxHSVStep,
        "kwargs": {
            "state_storage": MinMaxHSVState,
            "min": 30,
            "max": 150,
        },
        "grouping": "minmax",
        "display": "MINMAX - Bouncy",
    },
    "minmax.rainbow": {
        "class": MinMaxHSVStep,
        "kwargs": {
            "state_storage": MinMaxHSVState,
            "min": 0,
            "max": 255,
        },
        "grouping": "minmax",
        "display": "MINMAX - Rainbow",
    },
    # twinkle
    "twinke.warm":{
        "class": TwinklerBase,
        "kwargs": {
            "state_storage": BaseTwinkleState,
        },
        "grouping": "twinkle",
        "display": "Twinkle - Base",
    },
    "twinke.redgreen":{
        "class": TwinklerRedGreen,
        "kwargs": {
            "state_storage": BaseTwinkleState,
        },
        "grouping": "twinkle",
        "display": "Twinkle - RedGreen",
    },
    "twinke.purple":{
        "class": TwinklerPurp,
        "kwargs": {
            "state_storage": BaseTwinkleState,
        },
        "grouping": "twinkle",
        "display": "Twinkle - Purp",
    },
    "twinke.blue":{
        "class": TwinklerBlue,
        "kwargs": {
            "state_storage": BaseTwinkleState,
        },
        "grouping": "twinkle",
        "display": "Twinkle - Blue",
    },
    "twinke.wintry":{
        "class": TwinklerWintry,
        "kwargs": {
            "state_storage": BaseTwinkleState,
        },
        "grouping": "twinkle",
        "display": "Twinkle - Wintry",
    },
    "twinke.green":{
        "class": TwinklerGreen,
        "kwargs": {
            "state_storage": BaseTwinkleState,
        },
        "grouping": "twinkle",
        "display": "Twinkle - Green",
    },
    "twinke.red":{
        "class": TwinklerRed,
        "kwargs": {
            "state_storage": BaseTwinkleState,
        },
        "grouping": "twinkle",
        "display": "Twinkle - Red",
    },
    "twinke.amber":{
        "class": TwinklerAmber,
        "kwargs": {
            "state_storage": BaseTwinkleState,
        },
        "grouping": "twinkle",
        "display": "Twinkle - Amber",
    },
    "twinke.amberred":{
        "class": TwinklerAmberRed,
        "kwargs": {
            "state_storage": BaseTwinkleState,
        },
        "grouping": "twinkle",
        "display": "Twinkle - AmberRed",
    },
    "twinke.all":{
        "class": TwinklerAll,
        "kwargs": {
            "state_storage": BaseTwinkleState,
        },
        "grouping": "twinkle",
        "display": "Twinkle - All",
    },
    "twinke.allplusplus":{
        "class": TwinklerAllButMore,
        "kwargs": {
            "state_storage": BaseTwinkleState,
        },
        "grouping": "twinkle",
        "display": "Twinkle - All++",
    },
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

remote_device_managed = 7