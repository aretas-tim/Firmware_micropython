from pyb import I2C

class HIH6130:
    
    # Constructor: Initializes an HIH6130 .
	# PARAMS:
	#   1) address is the address of slave device (hardware selected). 
	#	   Default: 0x27  
	#	2) bus_num is the I2C bus ADS115 is wired to on the MicroPython board. 
	#	   One of: 1, 2
	#	3) freq is the desired operating frequency of the HIH6130. 
	#	   100 kHz - 400 kHZ is standard and fast mode. Above 400kHz requires HS mode
	#	4) general_call is boolean enabling the I2C line's recognition of the general call
	# 
    def __init__(self, address = 0x27, bus_num = 1, freq = 200000, general_call = False, RH_sensor_type = None, temp_sensor_type = None ):
        
        if (bus_num < 1) or (bus_num > 2):
            print ('The Bus number is out of range. bus_num must be either 1 or 2\n')
            return -1
            
            
        self.i2c = I2C(bus_num)
        self.i2c.init(I2C.MASTER, baudrate = freq, gencall = general_call)
        
        self.address= address
        self.gencall = general_call
        
        self.H_DAT = None
        self.T_DAT = None
        self.RH = None
        self.TC = None
        self._status = None
        self.RH_sensor_type = RH_sensor_type
        self.Temp_sensor_type = temp_sensor_type
        
        
        
    # Reads 4 bytes of data from HIH6130 over I2C bus and interprets the status of the device
    #
    # MODIFIES: Self.
	# 
	# PARAMS: delay is the timeout in milliseconds for i2c.recv() function 
	#
	# RETURNS: integer (_status)     
    def fetch(self, delay=5000):
       
        data = bytearray(4)
        self.i2c.recv(data,self.address, timeout = delay)
    
        Hum_H = data[0]
        Hum_L = data[1]
        Temp_H = data[2]
        Temp_L = data[3]
        _status = (Hum_H >> 6) & 0x03
        Hum_H = Hum_H & 0x3f
        self.H_dat = ((Hum_H) << 8) | Hum_L
        self.T_dat = ((Temp_H) << 8) | Temp_L
        self.T_dat = self.T_dat / 4
    
        return _status
    
       
    # Calls fetch() and calculates RH and TC values
    #
    # MODIFIES: Self.
    # 
    # PARAMS: None
    #
    # RETURNS: Nothing    
    def getTRH(self): 



        self._status  = self.fetch()


        if((self._status!=0) and (self._status!=1)):
            print("self.fetch() returned with no data!")
            print("Invalid Status:")
            print(self._status)
            return

        self.RH = self.H_dat * 6.10e-3
        self.TC = self.T_dat * 1.007e-2 - 40
        
    
    # Prints RH and TC values to the screen
    #
    # MODIFIES: Nothing.
	# 
	# PARAMS: p (boolean), mac (integer)
	#
	# RETURNS: Nothing
    def printTRH(self,p,mac):



        if(self.status == 0):
            pass
        elif (self._status == 1):
            print("HIH6130: STALE DATA")
        elif (self._status == 2):
            print("HIH6130: IN COMMAND MODE")
        else:
            print("HIH6030: DIAGNOSTIC")
    

        if((self._status!=0) and (self._status!=1)):
                print("self.fetch() returned with no data!")
                print("Invalid Status:")
                print(self._status)
                return
    
        if(p==True):

            print(" mac: %d, RH Sensor Type: %d, Rh: %f \n" %(mac, self.RH_sensor_type, self.RH)) 
            print(" mac: %d, Temp Sensor Type: %d, Rh: %f \n" %(mac, self.Temp_sensor_type, self.TC)) 
		    
	
	
	
	# Calls fetch(), calculates RH and TC values and prints RH and TC values to the screen
    #
    # MODIFIES: Self.
	# 
	# PARAMS: p (boolean), mac (integer)
	#
	# RETURNS: Nothing
    def getPrintTRH(self,p,mac):
        
        self._status  = self.fetch()
        
        if(self.status == 0):
            pass
        elif (self._status == 1):
            print("HIH6130: STALE DATA")
        elif (self._status == 2):
            print("HIH6130: IN COMMAND MODE")
        else:
            print("HIH6030: DIAGNOSTIC")
            
        
        if((_status != 0) and (_status != 1)):
            print("self.fetch() returned with no data!")
            print("Invalid Status:")
            print(self._status)
            return
		 
		 
        self.RH = self.H_dat * 6.10e-3
        self.TC = self.T_dat * 1.007e-2 - 40
        
            
        if(p==True):
		
            print(" mac: %d, RH Sensor Type: %d, Rh: %f \n" %(mac, self.RH_sensor_type, self.RH)) 
            print(" mac: %d, Temp Sensor Type: %d, Rh: %f \n" %(mac, self.Temp_sensor_type, self.TC))