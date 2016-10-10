
import bluepy
from bluepy import btle
from devices.base import BaseDevice
from helpers import chunks
import random
import struct

class YifangSH201Device(BaseDevice):
    def __init__(self, devices, shuffle=True):
        """
        :param devices: List of MacAddress Strings
        :param shuffle:  Shuffe the values coming down the pipe written to each bulb
        """
        self.device_addresses = devices
        self.shuffle = shuffle

    def _connect_single(self, addr):

        try:
            print addr
            peripheral = btle.Peripheral(addr)
        except IOError:
            # raise
            # TODO add a cannot find exception here, in addition to failing to connect the first time
            print 'failed to find %s , trying again next tick around' % addr
            return None
        except:
            # raise
            print 'failed to connect to %s , trying again next tick around' % addr
            return None

        return peripheral

    def _write_rgb(self, r, g, b, periph):
        rc = struct.pack('h', r)[0]
        gc = struct.pack('h', g)[0]
        bc = struct.pack('h', b)[0]

        # get services
        try:
            periph.discoverServices()
        except bluepy.btle.BTLEException: # try again later
            return

        colorcontrol = periph.services.values()[2]

        # get characteristics
        x = colorcontrol.getCharacteristics()

        # write
        x[0].write(rc)
        x[1].write(gc)
        x[2].write(bc)

    def write(self, values):
        chunked = list(chunks(values, 3))
        if self.shuffle:
            random.shuffle(chunked) # operates in place yay

        self.peripherals = filter(None, [self._connect_single(a) for a in self.device_addresses])
        for p in self.peripherals:
            value = chunked.pop()
            self._write_rgb(*value, periph=p)

        for p in self.peripherals:
            p.disconnect()