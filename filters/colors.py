## Basic Color Filters
from helpers import convert_hsv_rgb_int, convert_rgb_hsv_int


class RGBtoGRBLambentOutputFilter(object):
    _desc = "RGB -> GRB"

    def do_filter(self, rgbvals):
        val = [rgbvals[1], rgbvals[0], rgbvals[2]]
        return val


class InvertLambentOutputFilter(object):
    _desc = "Invert"

    def do_filter(self, rgbvals):
        return [255 - rgbvals[0], 255 - rgbvals[1], 255 - rgbvals[2]]


class PercentageBrightnessReduc50(object):
    """
    Divides the output values by 50%
    """
    _desc = "Reduce 50"
    reduction = 2

    def do_filter(self, rgbvals):
        return [rgbvals[0] / self.reduction, rgbvals[1] / self.reduction, rgbvals[2] / self.reduction]


class PercentageBrightnessReduc66(object):
    """
    Divides the output values by 66%
    """
    _desc = "Reduce 66"
    reduction = 3


class PercentageBrightnessReduc75(PercentageBrightnessReduc50):
    """
    Divides the output values by 75%
    """
    _desc = "Reduce 75"
    reduction = 4


class PercentageBrightnessReduc80(PercentageBrightnessReduc50):
    """
    Divides the output values by 80%
    """
    _desc = "Reduce 80"
    reduction = 5


class PercentageBrightnessReduc90(PercentageBrightnessReduc50):
    """
    Divides the output values by 90%
    """
    _desc = "Reduce 90"
    reduction = 10


class NeonOutputFilter(object):
    """
    Neon-ifies the output colors
    """
    _desc = "Neon-ify"

    def do_filter(self, rgbvals):
        hsv = convert_rgb_hsv_int(*rgbvals)
        rgb = convert_hsv_rgb_int(hsv[0], 90, 60)
        return rgb


class PastelOutputFilter(object):
    """
    pastel-ifies the output colors
    """
    _desc = "Pastel-ify"

    def do_filter(self, rgbvals):
        hsv = convert_rgb_hsv_int(*rgbvals)
        rgb = convert_hsv_rgb_int(hsv[0], 156, 209)
        return rgb


class DarkenedOutputFilter(object):
    """
    Makes output colors dark
    """
    _desc = "Darken-ify"

    def do_filter(self, rgbvals):
        hsv = convert_rgb_hsv_int(*rgbvals)
        rgb = convert_hsv_rgb_int(hsv[0], 255, 75)
        return rgb
