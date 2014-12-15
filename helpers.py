import colorsys

def pattern_list_fill(pattern, count):
    index = 0
    while index <= count:
        for i in pattern:
            yield i
            index +=1

class HSVHelper(object):
    def _sys_255_to_1(self, values):
        return [i / 255.0 for i in values]

    def _sys_1_to_255(self, values):
        return [i * 255 for i in values]

    def _hsv_to_rgb(self, h, s, v):
        h_, s_, v_ = self._sys_255_to_1([h, s, v])
        r_, g_, b_ = colorsys.hsv_to_rgb(h_, s_, v_)
        r, g, b = self._sys_1_to_255([r_, g_, b_])
        return r, g, b

    def _rgb_to_hsv(self, r, g, b):
        r_, g_, b_ = self._sys_255_to_1([r, g, b])
        h_, s_, v_ = colorsys.rgb_to_hsv(r_, g_, b_)
        h, s, v = self._sys_1_to_255([h_, s_, v_])
        return h, s, v


class DummySerialDevice(object):
    """
    For Debugging 
    """

    def write(self, buff):
        # pass
        print(buff)

    def close(self, *args, **kwargs):
        print("'Closed' dummy serial device")