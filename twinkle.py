from copy import deepcopy
import random
import serial
import time

# vars
LED_COUNT = 240
LED_PORT = "/dev/ttyACM0"
LED_DURATION = 600
LED_FADE_TIME = 0.05
LED_FADE_STEPS = 30

class LEDState(object):
    def __init__(self, r=0, g=0, b=0, step_size=3, id=0):
        self.r = r
        self.g = g
        self.b = b
        self.sz = step_size
        
        self.r_t = 0
        self.g_t = 0
        self.b_t = 0
        self.id = id
    
    def at_target(self): # to write the next values
        if self.r == self.r_t and self.g == self.g_t and self.b == self.b_t:
            return True
        else:
            return False
        
    def at_zeroes(self): # for fading up or down
        return self.r == self.g == self.b == 0
    
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
        # step red
        self.r = self._step(self.r, self.r_t)
        self.g = self._step(self.g, self.g_t)
        self.b = self._step(self.b, self.b_t)
        #if self.r <= self.r_t:
            #if self.r + self.sz <= self.r_t:
                #self.r += self.sz
            #elif self.r + self.sz > self.r_t:
                #self.r = self.r_t
        #else:
            #if self.r - self.sz <= self.r_t:
                #self.r -= self.sz
            #elif self.r - self.sz < self.r_t:
                #self.r = self.r_t
        
        ## step green
        #if self.g <= self.g_t:
            #if self.g + self.sz <= self.g_t:
                #self.g += self.sz
            #elif self.g + self.sz > self.g_t:
                #self.g = self.g_t
                
        #else:
            #if self.g - self.sz >= self.g_t:
                #self.g -= self.sz
            #elif self.g - self.sz < self.g_t:
                #self.g = self.g_t
        
        ## step blue
        #if self.b <= self.b_t:
            #if self.b + self.sz <= self.b_t:
                #self.b += self.sz
            #elif self.b + self.sz > self.b_t:
                #self.b = self.b_t
                
        #else:
            #if self.b - self.sz >= self.b_t:
                #self.b -= self.sz
            #elif self.b - self.sz < self.b_t:
                #self.b = self.b_t
            
    def read(self):
        return [self.r, self.g, self.b]
    
    def read_t(self):
        return [self.r_t, self.g_t, self.b_t]

class LEDStringTwinkle(object):
    def __init__(self, led_count, run_duration, fade_time, fade_steps, device, twinkle_hues = [], fadeout=True, debug=False):
        self.led_count = led_count
        self.run_duration = run_duration
        self.fade_time = fade_time
        self.fade_steps = fade_steps
        self.hues = twinkle_hues
        self.device = device
        self.fadeout = fadeout
        self.debug = debug
        
        # figure out when to stop
        self.t_start = time.time()
        self.t_end = self.t_start + self.run_duration
        
        # create objects for tracking LED states
        self.leds = [LEDState(id=i) for i in range(self.led_count)]
        
        # create the send buffer
        buffer_start = ['\x41', '\x64', '\x61']
        buffer_3 = (self.led_count -1) >> 8
        buffer_4 = (self.led_count -1) & 0xff
        buffer_5 = buffer_3 ^ buffer_4 ^ 0x55
        self.buffer_complete = buffer_start + [buffer_3, buffer_4, buffer_5]
    
    def dprint(self, string):
        if self.debug:
            print(string)
    def run(self):
        while time.time() < self.t_end:
            new_buffer = deepcopy(self.buffer_complete)
            for led in self.leds:
                if led.at_target(): # we set values here
                    self.dprint("@target")
                    if led.at_zeroes(): # we input new colors here
                        self.dprint("@zeroes")
                        # for now just twinkle to some random orange, we'll do hue juggling next
                        led.set_step_target(
                            random.randint(192,255),
                            random.randint(0,64),
                            0, # random.randint(0,128),
                        )
               
                    else:
                        led.set_step_target(
                            0,0,0
                        )
                
                
                led.do_step()
                new_buffer.extend(led.read())
                
            self.device.write(new_buffer)
            time.sleep(self.fade_time)
        
        # fadeout
        if self.fadeout:
            for l in self.leds:
                l.set_step_target(0,0,0)
 
            while not all([l.at_zeroes() for l in self.leds]):
                new_buffer = deepcopy(self.buffer_complete)
                for led in self.leds:
                    if led.at_target() and led.at_zeroes():
                        pass
                    else:
                        led.do_step()
                    new_buffer.extend(led.read())
                        
                self.device.write(new_buffer)
                time.sleep(self.fade_time)
            

## make the input buffer
##               A       d       a       Fixme::-------------|
#buffer_start = ['\x41', '\x64', '\x61']
#buffer_3 = (LED_COUNT -1) >> 8
#buffer_4 = (LED_COUNT -1) & 0xff
#buffer_5 = buffer_3 ^ buffer_4 ^ 0x55
#buffer_complete = buffer_start + [buffer_3, buffer_4, buffer_5]

#hues = [0,1]

## fill dat buffer with shades of blue
#for i in range(30):
    #r = random.choice(hues)
    #if r == 1:
        #buffer_complete.append(random.randint(128,255))
        #buffer_complete.append(random.randint(0,64))
        #buffer_complete.append(0)
    #if r == 0:
        #buffer_complete.append(random.randint(128,255))
        #buffer_complete.append(0)
        #buffer_complete.append(random.randint(0,64))

# Crack it open
s = serial.Serial(LED_PORT,115200)


    
#s.write(buffer_complete)


t = LEDStringTwinkle(LED_COUNT, LED_DURATION, LED_FADE_TIME, LED_FADE_STEPS, s, [0])
t.run()

s.close()

###

## TODO
# LED_HOLD : int: hold a value at its peak for x cycles. (remember to reset the hold after its done)
# LED_HOLD_LOW: bool to do this when we're zeroed
# hue mode: add in list of hues and we can pick colors eg halloween mode [yellow, read, orange, puple] xmas [greens, reds, whites] murica [reds, whites, blues]
#        also a "huestep" so that the colors stay consistent eg dark orange to oranger, vs green -> yellow -> orange as there are far more red levels to step thru
