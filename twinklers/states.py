import random

from helpers import HSVHelper
from led_states import BaseLEDState


class BaseTwinkleState(BaseLEDState, HSVHelper):
    def __init__(self, target=[255,255,190], surprises=[], min_t=2, max_t=4, min_w=3, max_w=7, surprise_chance=2, **kwargs):
        self.at_max = False
        self.at_min = False
        self.going_up = True

        self.min_step_size=0
        self.max_step_size=2

        self.r = 0
        self.g = 0
        self.b = 0

        self.current_target = target
        self.min_target = [0,0,0]
        self.half_target = self.set_half()
        self.default_target = target
        self.surprise_target = surprises
        self.surprise_default = target
        self.surprise_chance = surprise_chance

        self.min_t_before_inc = min_t
        self.max_t_before_inc = max_t
        self.min_w_before_inc = min_w
        self.max_w_before_inc = max_w
        self.current_wait_count = 0
        self.current_twinkle_count = 0
        self._reset_twinkle_inc()
        self._reset_wait_inc()

    @property
    def current_position(self):
        return [self.r, self.g, self.b]

    @current_position.setter
    def current_position(self, value):
        self.r, self.g, self.b = value

    def at_middle(self):
        return self.half_target == self.current_position

    def _gen_wait_increments(self):
        return random.randint(self.min_w_before_inc, self.max_w_before_inc)

    def _reset_wait_inc(self):
        self.current_inc_wait_max = self._gen_wait_increments()

    def _add_surprise(self):
        if self.surprise_target and random.randrange(20) <= self.surprise_chance:
            surp = random.choice(self.surprise_target)
            self.current_target = surp

        else:
            self.current_target = self.surprise_default

        self.half_target = self.set_half() # happens no matter what
        
    def _gen_twinkle_increments(self):
        return random.randint(self.min_t_before_inc, self.max_t_before_inc)

    def _reset_twinkle_inc(self):
        self.current_inc_twinkle_max = self._gen_twinkle_increments()

    def set_half(self):
        self.half_target = [i/2 for i in self.current_target]
        return self.half_target

    def do_step(self):
        # determine if we're at the top / bottom / middle wth our last move?
        # print self.current_position

        # find what direction we're going
        if self.at_min:
            self.at_min = False
            self.going_up = True
            self._reset_wait_inc()
            self._reset_twinkle_inc()
            self._add_surprise()
            # get a target (set self.target)
            # get the half target
        elif self.at_max:
            self.at_max = False
            self.going_up = False
            self._reset_wait_inc()
            self.current_twinkle_count += 1
            if self.current_twinkle_count >= self.current_inc_twinkle_max:
                self.current_target = self.min_target # go to the bottom
                self.current_twinkle_count = 0
            else:
                self.current_target = self.half_target # go to the middle

        elif self.at_middle():
            self.current_target = self.default_target
            self.going_up = True

        # now move
        if self.going_up:
            self.step_up()
        else:
            self.step_down()

    def step_up(self):
        t_r, t_g, t_b = self.current_target
        self.r += random.randint(self.min_step_size, self.max_step_size)
        if self.r > t_r: self.r = t_r
        self.g += random.randint(self.min_step_size, self.max_step_size)
        if self.g > t_g: self.g = t_g
        self.b += random.randint(self.min_step_size, self.max_step_size)
        if self.b > t_b: self.b = t_b

        if self.r == t_r and self.g == t_g and self.b == t_b:
            # print "max"
            self.at_max = True

    def step_down(self):
        t_r, t_g, t_b = self.current_target
        self.r -= random.randint(self.min_step_size, self.max_step_size)
        if self.r < t_r: self.r = t_r
        self.g -= random.randint(self.min_step_size, self.max_step_size)
        if self.g < t_g: self.g = t_g
        self.b -= random.randint(self.min_step_size, self.max_step_size)
        if self.b < t_b: self.b = t_b

        if self.r == t_r and self.g == t_g and self.b == t_b:
            self.at_min = True

    def read_rgb(self):
        return self.r,self.g,self.b
