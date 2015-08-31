from helpers import chunks
import random
## Base
class BaseOutputFilter(object):
    avail_blending = ['lin_average', 'lin_additive']

    ### setups
    def split_rgbvals(self, vals):
        return [i for i in chunks(vals, 3)]

    def convert_overlay_to_RGB(self, overlay_values, overlay_colors):
        out = []
        for v in overlay_values:
            out.append([i*v for i in overlay_colors])
        return out

    ### blending
    def blend(self, original, overlay, method):
        if method not in self.avail_blending:
            raise SyntaxError("Bad blend method")

        methodstr = "blend_" + method
        blendr = getattr(self, methodstr)
        return blendr()

    ## actual blenders
    # linear
    def blend_lin_average(self, og, overlay):
        pixel_out = []
        for c1,c2 in zip(og, overlay):
            pixel_out.append(
                (c1+c2)/2
            )

        return pixel_out

    def blend_lin_additive(self, og, overlay):
        pixel_out = []
        for c1,c2 in zip(og, overlay):
            pixel_out.append(
                min(c1 + c2, 255)
            )

        return pixel_out

    def blend_lin_diff(self, og, overlay):
        pixel_out = []
        for c1,c2 in zip(og, overlay):
            pixel_out.append(
                abs(c1-c2)
            )

        return pixel_out

## FX output filters

### Noise Overlay
class NoiseOverlayOutputFilter(BaseOutputFilter):
    color_overlays = [
        {
            "color": [230, 230, 230],
            "min_dist": 7,
            "max_dist": 11,
            "pattern_min": 2,
            "pattern_max": 4,
            "pattern_cnt": 3,
            "pattern_off_min": 1,
            "pattern_off_max": 2,
            "currently_on": False,
            "move_every": 1,
            "method": "average",
        },
    ]

    def __init__(self, count):
        self.value_count = count
        self.values = []
        self.initialize_initial_values()

    def generate_container_pattern_values(self, overlay):
        cnt = overlay['pattern_cnt']
        min = overlay['pattern_min']
        max = overlay['pattern_max']
        pmin = overlay['pattern_off_min']
        pmax = overlay['pattern_off_max']

        out = []
        container_count = random.randint(1, cnt)
        for c in xrange(container_count):
            onlen = random.randint(min, max)
            out.extend([1 for i in xrange(onlen)])
            offlen = random.randint(pmin, pmax)
            out.extend([0 for i in xrange(offlen)])

        return out

    def generate_container_space_values(self, overlay):
        return [0 for i in xrange(random.randint(overlay['min_dist'],overlay['max_dist']))]


    def initialize_initial_values(self):
        for overlay in self.color_overlays:
            val_starting = random.choice([True,False])
            val_container = []
            while len(val_container) < self.value_count:
                if not val_starting:
                    val_container.extend(
                        self.generate_container_space_values(overlay)
                    )
                else:
                    val_container.extend(
                        self.generate_container_pattern_values(overlay)
                    )
                val_starting = not val_starting

            self.values.append(val_container)
            overlay['currently_on'] = val_starting

    def generate_next_step(self):
        for overlay, value_container in zip(self.color_overlays, self.values):
            value_container.pop(0)
            if len(value_container) < self.value_count:
                if not overlay['currently_on']:
                    value_container.extend(
                        self.generate_container_space_values(overlay)
                    )
                else:
                    value_container.extend(
                        self.generate_container_pattern_values(overlay)
                    )
                overlay['currently_on'] = not overlay['currently_on']

    def apply_filter(self, rgbvals): # current a big TODO, actually write this
        split_vals = self.split_rgbvals(rgbvals)
        for overlay, value_container in zip(self.color_overlays, self.values):
            new_split = []
            as_rgb = self.convert_overlay_to_RGB(value_container, overlay['color'])
            for value, pixel in zip(as_rgb, split_vals):
                rgbval = self.blend(pixel, value, overlay['method'])
                new_split.append(rgbval)
            split_vals = new_split

        return split_vals



    # def do_filter(self, rgbvals):
