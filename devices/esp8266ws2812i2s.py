from devices.base import BaseDevice
import socket
import struct
from filters.colors import RGBtoGRBLambentOutputFilter
from helpers import chunks
import itertools



class ESPDevice(BaseDevice):
    def __init__(self, addr, port=7777):
        self.addr = addr
        self.port = port
        self.socket = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM) # UDP

    def write(self, values):
        chunked = chunks(values, 3)
        # convert list from RGB to GRB internally
        # yay code reuse
        filt = RGBtoGRBLambentOutputFilter()
        filtered = [filt.do_filter(i) for i in chunked]
        values = list(itertools.chain.from_iterable(filtered))

        structd = struct.pack('B'*len(values), *values)
        self.socket.sendto(structd, (self.addr, self.port))
