# raspi pin read
from devices.base import BaseDevice

import RPi.GPIO as GPIO


class PinReadDevice(BaseDevice):
    """
    Poor Guy, only reads.
    """
    def __init__(self, pin, mode=GPIO.BOARD):
        self.pin = pin
        self.mode = mode

        if self.mode not in [GPIO.BOARD, GPIO.BCM]:
            raise ValueError("Invalid Mode %s", self.mode)
        if self.mode == GPIO.BOARD:
            pass # TODO limit/warn pins in this direction
        elif self.mode == GPIO.BCM:
            pass # TODO limit/warn pins in the other way

        GPIO.setup(self.pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

    def read(self):
        return GPIO.input(self.pin)

    def die(self):
        GPIO.cleanup()