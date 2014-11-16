import colorsys

class HSVHelper(object):
    def _sys_255_to_1(self, values):
        return [i/255.0 for i in values]
    def _sys_1_to_255(self, values):
        return [i*255 for i in values]

    def _hsv_to_rgb(self, h, s, v):
        h_, s_, v_ = self._sys_255_to_1([h, s, v])
        r_, g_, b_ = colorsys.hsv_to_rgb(h_, s_, v_)
        r, g, b = self._sys_1_to_255([r_, g_, b_])
        return r, g, b
    
    
class DummySerialDevice(object):
    """
    For Debugging 
    """
    def write(self, buff):
        print(buff)