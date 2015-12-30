from helpers import HSVHelper
from led_states import BaseLEDState
import random


class BaseGMStateHSV(BaseLEDState, HSVHelper):
    max_s = 255
    max_v = 255
    def __init__(self, 
                 growth_hues=[], death_hues=[], 
                 linger_min_g=10, linger_max_g=50,
                 linger_min_d=5, linger_max_d=25,
                 linger_between_min=30, linger_between_max=130,
                 h=0, s=0, v=0, **kwargs
                 ):
        self.grown = False
        self.died = False

        self.growth_hues = growth_hues
        self.death_hues = death_hues
        self.linger_min_g = linger_min_g
        self.linger_max_g = linger_max_g
        self.linger_min_d = linger_min_d
        self.linger_max_d = linger_max_d
        self.linger_between_min = linger_between_min
        self.linger_between_max = linger_between_max

        self.h = 0
        self.s = 0
        self.v = 0

        self.instantiate_lists()


    def _expansion_func(self, iterable):
        grown = []
        for g,d in iterable:
            x = [g] * d
            grown.extend(x)

        bigger = []
        lengrown = len(grown)
        for q in xrange(0, lengrown):
            if q+1 >= len(grown):
                continue
            if grown[q] != grown[q+1]:
                bigger.extend(xrange(grown[q], grown[q+1]))
            else:
                bigger.append(grown[q])

        return bigger

    def instantiate_lists(self):
        self.growth_values = [
            [i, random.randint(self.linger_min_g, self.linger_max_g)] for i in self.growth_hues
        ]

        self.death_values = [
            [i, random.randint(self.linger_min_d, self.linger_max_d)] for i in self.death_hues
        ]
        
        self.linger_duration = random.randint(self.linger_between_min, self.linger_between_max)

        expanded_growth_hues = self._expansion_func(self.growth_values)
        expanded_death_hues = self._expansion_func(self.death_values)

        if expanded_growth_hues and expanded_death_hues:
            if expanded_growth_hues[-1] == expanded_death_hues[0]:
                newrange = [expanded_death_hues[0]] * self.linger_duration
            else:
                linger0 = [expanded_growth_hues[-1] * self.linger_duration/2]
                linger1 = [expanded_death_hues[0] * self.linger_duration/2]
                lingerbetween = xrange(expanded_growth_hues[-1],expanded_death_hues[0])
                newrange = linger0 + list(lingerbetween) + linger1

            final_hue_list = expanded_growth_hues + newrange + expanded_death_hues
        else:
            final_hue_list = expanded_growth_hues + expanded_death_hues

        all_vals = final_hue_list
        self.final_hue_list = final_hue_list
        val_first = all_vals.pop(0)
        val_last = all_vals.pop(-1)
        val_mid = all_vals


        # set max sat / max val eventually via __init__
        first_hues = [val_first] * self.max_v
        first_saturations = [self.max_s] * self.max_v
        first_values = [i for i in xrange(0,self.max_v)]

        last_hues = [val_last] * self.max_v
        last_saturations = [self.max_s] * self.max_v
        last_values = reversed(first_values)

        init_growth_triplets = zip(first_hues, first_saturations, first_values)
        exit_death_triplets = zip(last_hues, last_saturations, last_values)
        middle_triplets = [(i, self.max_s, self.max_v) for i in val_mid]

        final_triplets = init_growth_triplets + middle_triplets + exit_death_triplets

        self.final_output_hsvs = final_triplets


    def do_step(self):
        if self.final_output_hsvs:
            self.h, self.s, self.v = self.final_output_hsvs.pop(0)
        else:
            self.instantiate_lists()
