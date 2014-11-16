from helpers import HSVHelper

class BaseLEDState(object):
    def __init__(self, r=0, g=0, b=0, step_size=3, id=0):
        self.r = r
        self.g = g
        self.b = b
        self.sz = step_size
        
        self.r_t = 0
        self.g_t = 0
        self.b_t = 0
        self.id = id

    def at_zeroes(self): # for fading up or down
        return self.r == self.g == self.b == 0        

    def read(self):
        return [self.r, self.g, self.b]
    
    def read_t(self):
        return [self.r_t, self.g_t, self.b_t]
        
class DumbRGBLEDState(BaseLEDState):
    """
    Steps around with no regard to maintaining consistent hues or anything else really
    """
    
    def at_target(self): # to write the next values
        if self.r == self.r_t and self.g == self.g_t and self.b == self.b_t:
            return True
        else:
            return False

    
    def set_step_target(self,r,g,b):
        self.r_t = r
        self.g_t = g
        self.b_t = b
        
    def set_step_target_to_zeroes(self):
        self.r_t = 0
        self.g_t = 0
        self.b_t = 0
        
    def _step(self,current,dest):
        if abs(current-dest) > self.sz:
            if current > dest:
                current -= self.sz
            elif current < dest:
                current += self.sz
            else:
                pass
        else:
            current = dest
        return current
        
    def do_step(self):
        self.r = self._step(self.r, self.r_t)
        self.g = self._step(self.g, self.g_t)
        self.b = self._step(self.b, self.b_t)

            


class HSVAwareLEDState(BaseLEDState, HSVHelper):