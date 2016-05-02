import colorsys

def pattern_list_fill(pattern, count):
    index = 0
    while index <= count:
        for i in pattern:
            yield i
            index +=1

def convert_hsv_rgb_int(h,s,v):
    if s == 0:
        r = g = b = v;
        return r,g,b

    region = h/43;
    fpart = (h - (region * 43)) * 6

    p = (v * (255-s)) >> 8
    q = (v * (255 - ((s * fpart) >> 8))) >> 8
    t = (v * (255 - ((s * (255 - fpart)) >> 8))) >> 8

    if region == 0:
        r = v
        g = t
        b = p
    elif region == 1:
        r = q
        g = v
        b = p
    elif region == 2:
        r = p
        g = v
        b = t
    elif region == 3:
        r = p
        g = q
        b = v
    elif region == 4:
        r = t
        g = p
        b = v
    else:
        r = v
        g = p
        b = q

    return r,g,b


def convert_rgb_hsv_int(r, g, b):
    min_v = min(r, g, b)
    max_v = max(r, g, b)

    mm_delta = max_v - min_v

    v = max_v
    if v == 0:
        h = 0
        s = 0
        return h, s, v

    s = 255 * mm_delta / v
    if s == 0:
        h = 0
        return h, s, v

    if max_v == r:
        h = 43 * (g - b) / mm_delta;

    elif max_v == g:
        h = 85 + 43 * (b - r) / mm_delta;

    elif max_v == b:
        h = 171 + 43 * (r - g) / mm_delta;

    return h, s, v



class HSVHelper(object):
    def __init__(self,h,s,v):
        self.h = h
        self.s = s
        self.v = v

        self.h_t = h
        self.s_t = s
        self.v_t = v

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

    def read(self):
        return [self.h, self.s, self.v]

    def read_rgb(self):
        r, g, b = self._hsv_to_rgb(self.h, self.s, self.v)
        return [int(r), int(g), int(b)]

    def read_t(self):
        return [self.h_t, self.s_t, self.v_t]

    def read_t_rgb(self):
        r, g, b = self._hsv_to_rgb(self.h_t, self.s_t, self.v_t)
        return [r, g, b]



class DummySerialDevice(object):
    """
    For Debugging 
    """

    def write(self, buff):
        # pass
        print(buff)

    def close(self, *args, **kwargs):
        print("'Closed' dummy serial device")

# grabbed from http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def rgb_triplet_to_html_hex_code(triplet):
    return '#%02X%02X%02X' % tuple(triplet)
