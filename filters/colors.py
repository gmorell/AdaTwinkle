class RGBtoGRBLambentOutputFilter(object):
    def do_filter(self, rgbvals):
        val = [rgbvals[1],rgbvals[0],rgbvals[2]]
        return val

class InvertLambentOutputFilter(object):
    pass