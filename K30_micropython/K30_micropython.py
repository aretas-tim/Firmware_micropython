import pyb
from pyb import I2C

#The default I2c address of the K30 Co2 monitor 
i2c_addr = 0x68
    
    

class K30:
    
    
    
    # Constructor.
    # 
    def __init__(self, mac, address= i2c_addr, bus_num=1, baud = 100000, general_call = True):
        
        self.i2c_address = i2c_addr
        self.i2c = I2C(bus_num,I2C.MASTER,baudrate=baud)
        self.mac_addr = mac
        
    # This function returns an integer representation of the K30's CO2 reading.   
    def readRam2bytes(self):
        
        # This is the buffer that will be sent to the K30 that initiates the data read frame.
        # 0x22 indicates a read from RAM (0x20) of a length of 2 bytes (0x02), hence 0x22
        # 0x00 0x08, indicate the address the CO2 data will be measured from. 
        # The k30 requires this address to be 2 bytes long hence 0x00 0x08 instead of just 0x08
        # 0x2A is the checksum value (the sume of the previous 3 bytes, 0x22 + 0x00 + 0x08 = 0x2A)
        buf = b'\x22\x00\x08\x2A'
        
        #send the buffer to the K30 over I2C bus
        self.i2c.send(buf, self.i2c_address)
        
        # Delay 10ms. This is here because the K30 shuts down the I2C bus while 
        # a measurement is being taken. Reading from the I2C bus would interrupt 
        # the sensor so a wait period necessary.
        pyb.delay(10)
        
        # receive the resulting 4 bytes (command, data[0], data[1], checksum)
        # from the K30. The actual measurement will be bytes 2 and 3 of the 4-bytes received.
        result_buff = bytearray(4)
        self.i2c.recv(result_buff, self.i2c_address)
        
        #this line used for testing when K30 sensor was unavailable
        #result_buff = b'\x01\x02\x03\x06'
        
        #Zero out the initialized return value
        CO2_val  = 0
        #Take the high-byte of the returned data value
        CO2_val |= (result_buff[1] & 0xFF)
        #Shift the high-byte up 8 bits
        CO2_val = CO2_val << 8
        #Add the low-byte onto the result
        CO2_val |= (result_buff[2] & 0xFF)
        
        #the sum that will be used to verify the check-sum
        sum = 0
        sum = result_buff[0] + result_buff[1] + result_buff[2]
        
        #if the sum of the first 3 bytes is the same as the check-sum (byte 3 of the returned result)
        if(sum == result_buff[3]):
            
            #convert CO2_val to an integer and return
            return CO2_val
        
        else:
            
            print("Check-sum error. K30 read failure.")
     
    # This function calls self.readRam2Bytes() to get the most recent CO2 reading
    # from the K30 and then prints it to the screen.        
    def printCO2(self):
        
        C02 = self.readRam2bytes() 
        print("The most recent C02 reading from mac addres %d is %d" %(self.mac_addr,C02))
        
        
        
        
        



    
        
        

