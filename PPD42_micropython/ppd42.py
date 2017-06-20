from pyb import I2C
from struct import *

class PPD42I2C:
    pm = 0
    address = 0

    def __init__(self, address = 0x1A):
        self.pm = 0
        self.address = address

    def getData(self, i2c):

        data = bytearray(4)

        try:
            i2c.recv(data, self.address)
        except Exception as e:
            print(e)
            return -1

        pmData = unpack("L",data)
        #pmData = ( (data[3] << 24) + (data[2] << 16) + (data[1] << 8) + (data[0] ) )
        self.pm = pmData[0];
        return 0
