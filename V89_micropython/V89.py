from pyb import I2C

class V89Sensor:

    VZ89_CMD_GETSTATUS = 0x9	#This command is used to read the VZ89 status coded with 6 bytes:

    tvoc = 0
    CO2 = 0
    reactivity = 0
    status = 0
    address = 0

    def __init__(self, address = 0x70):

        self.tvoc = 0
        self.CO2 = 0
        self.status = 0
        self.reactivity = 0
        self.address = address

    def getData(self, i2c):

        i2c.send(9, 112)
        i2c.send(0, 112)
        i2c.send(0, 112)

        data = bytearray(6)

        try:
            i2c.recv(data, self.address)
        except Exception as e:
            print(e)
            return -1

        if (data[0] < 13 or data[1] < 13 or data[2] < 13):
            print("CORRUPT DATA")
            return False

        else:
            self.CO2 = (data[0] - 13) * (1600.0 / 229) + 400 #ppm: 400 .. 2000
            self.reactivity = data[1]
            self.tvoc = (data[2] - 13) * (1000.0/229) #ppb: 0 .. 1000
 	        #resistor = 10 * (data[3] +256 * data[4] + 65536 * data[5]);
            return True
