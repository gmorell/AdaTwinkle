## Basic Color Filters
class RGBtoGRBLambentOutputFilter(object):
    def do_filter(self, rgbvals):
        val = [rgbvals[1],rgbvals[0],rgbvals[2]]
        return val

class InvertLambentOutputFilter(object):
    def do_filter(self, rgbvals):
        return [255-rgbvals[0],255-rgbvals[1],255-rgbvals[2]]





