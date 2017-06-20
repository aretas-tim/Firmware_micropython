
from pyb import I2C


# List of methods/functions:
#
# 1)  __init__(self, address=0x48, bus_num=1, freq = 100000, general_call = True)
# 2)  setConfig(self,acqmode='single', compmode='trad', pol='low', latch='nolatch', que=0, pga=4096, sps=128, mux='chan 0')
# 3)  Getters
# 4)  Setters
# 5)  printConfiguration(self)
# 6)  startADCConversion(self, delay=5000)
# 7)  startCompConversion(self, threshold_H, threshold_L, delay=5000)
# 8)  readConversion(self, delay=5000)
# 9)  writeToHi(self,val, delay=5000)
# 10) writeToLow(self,val, delay=5000)
# 11) readRegister(self, reg, delay=5000)
# 12) isConversionDone(self, delay=5000)
# 13) smbusAlertResponse(self, delay=5000)
# 14) enterPowerDown(self, delay=5000)
# 15) setConvReadyPin(self,delay=5000)
# 16) printContinousVoltage(self, chan)
# 17) printSingleShotVoltage(self, chan)


class ADS1115:

# Pointer Register
    __REG_POINTER_MASK        = 0x03
    __REG_POINTER_CONVERT     = 0x00
    __REG_POINTER_CONFIG      = 0x01
    __REG_POINTER_LOWTHRESH   = 0x02
    __REG_POINTER_HITHRESH    = 0x03
  
# Config Register
    __REG_CONFIG_OS_MASK      = 0x8000
    __REG_CONFIG_OS_SINGLE    = 0x8000  # Write: Set to start a single-conversion
    __REG_CONFIG_OS_BUSY      = 0x0000  # Read: Bit = 0 when conversion is in progress
    __REG_CONFIG_OS_NOTBUSY   = 0x8000  # Read: Bit = 1 when device is not performing a conversion
      
      # Mux settings
    __REG_CONFIG_MUX_MASK     = 0x7000
    __REG_CONFIG_MUX_DIFF_0_1 = 0x0000  # Differential P = AIN0, N = AIN1 (default)
    __REG_CONFIG_MUX_DIFF_0_3 = 0x1000  # Differential P = AIN0, N = AIN3
    __REG_CONFIG_MUX_DIFF_1_3 = 0x2000  # Differential P = AIN1, N = AIN3
    __REG_CONFIG_MUX_DIFF_2_3 = 0x3000  # Differential P = AIN2, N = AIN3
    __REG_CONFIG_MUX_SINGLE_0 = 0x4000  # Single-ended AIN0
    __REG_CONFIG_MUX_SINGLE_1 = 0x5000  # Single-ended AIN1
    __REG_CONFIG_MUX_SINGLE_2 = 0x6000  # Single-ended AIN2
    __REG_CONFIG_MUX_SINGLE_3 = 0x7000  # Single-ended AIN3

        # programmable gain settings
    __REG_CONFIG_PGA_MASK     = 0x0E00
    __REG_CONFIG_PGA_6_144V   = 0x0000  # +/-6.144V range
    __REG_CONFIG_PGA_4_096V   = 0x0200  # +/-4.096V range
    __REG_CONFIG_PGA_2_048V   = 0x0400  # +/-2.048V range (default)
    __REG_CONFIG_PGA_1_024V   = 0x0600  # +/-1.024V range
    __REG_CONFIG_PGA_0_512V   = 0x0800  # +/-0.512V range
    __REG_CONFIG_PGA_0_256V   = 0x0A00  # +/-0.256V range

        # conversion mode settings
    __REG_CONFIG_MODE_MASK    = 0x0100
    __REG_CONFIG_MODE_CONTIN  = 0x0000  # Continuous conversion mode
    __REG_CONFIG_MODE_SINGLE  = 0x0100  # Power-down single-shot mode (default)

        #data rate settings
    __REG_CONFIG_DR_8SPS      = 0x0000  # 8 samples per second
    __REG_CONFIG_DR_16SPS     = 0x0020  # 16 samples per second
    __REG_CONFIG_DR_32SPS     = 0x0040  # 32 samples per second
    __REG_CONFIG_DR_64SPS     = 0x0060  # 64 samples per second
    __REG_CONFIG_DR_128SPS    = 0x0080  # 128 samples per second
    __REG_CONFIG_DR_250SPS    = 0x00A0  # 250 samples per second (default)
    __REG_CONFIG_DR_475SPS    = 0x00C0  # 475 samples per second
    __REG_CONFIG_DR_860SPS    = 0x00E0  # 860 samples per second

        #comparator mode settings
    __REG_CONFIG_CMODE_MASK   = 0x0010
    __REG_CONFIG_CMODE_TRAD   = 0x0000  # Traditional comparator with hysteresis (default)
    __REG_CONFIG_CMODE_WINDOW = 0x0010  # Window comparator

        # latch polarity settings
    __REG_CONFIG_CPOL_MASK    = 0x0008
    __REG_CONFIG_CPOL_ACTVLOW = 0x0000  # ALERT/RDY pin is low when active (default)
    __REG_CONFIG_CPOL_ACTVHI  = 0x0008  # ALERT/RDY pin is high when active

        #latch settings
    __REG_CONFIG_CLAT_MASK    = 0x0004  # Determines if ALERT/RDY pin latches once asserted
    __REG_CONFIG_CLAT_NONLAT  = 0x0000  # Non-latching comparator (default)
    __REG_CONFIG_CLAT_LATCH   = 0x0004  # Latching comparator

        #comparator period setting (number of readings before conversionis asserted)
    __REG_CONFIG_CQUE_MASK    = 0x0003
    __REG_CONFIG_CQUE_1CONV   = 0x0000  # Assert ALERT/RDY after one conversions
    __REG_CONFIG_CQUE_2CONV   = 0x0001  # Assert ALERT/RDY after two conversions
    __REG_CONFIG_CQUE_4CONV   = 0x0002  # Assert ALERT/RDY after four conversions
    __REG_CONFIG_CQUE_NONE    = 0x0003  # Disable the comparator and put ALERT/RDY in high state (default)

   
   
   
    # Dictionary with register addresses
    reg_dict = {
        'convert':__REG_POINTER_CONVERT,     
        'config':__REG_POINTER_CONFIG,     
        'lowthresh':__REG_POINTER_LOWTHRESH,  
        'hithresh':__REG_POINTER_HITHRESH   
    }
    
    # Dictionary with acquisition modes (continuous vs single-shot)
    acqmode_dict = {
        'contin':__REG_CONFIG_MODE_CONTIN, 
        'single':__REG_CONFIG_MODE_SINGLE     
       
    }
    
    # Dictionary with comparator modes (traditional vs window)
    compmode_dict = {
        'trad':__REG_CONFIG_CMODE_TRAD, 
        'window':__REG_CONFIG_CMODE_WINDOW,
             
       
    }
    
    # Dictionary with Alert pin modes (active low vs active high, latch vs non-latching)
    comppol_dict = {
        'low':__REG_CONFIG_CPOL_ACTVLOW, 
        'high':__REG_CONFIG_CPOL_ACTVHI,
        
       
    }
    
    # Dictionary with comparator latch modes (latch value vs don't latch value)
    latch_dict = {
        'nolatch':__REG_CONFIG_CLAT_NONLAT, 
        'latch':__REG_CONFIG_CLAT_LATCH
    }
    
    # Dictionary with alert pin assertion periods (1, 2 or 4 conversions, 0 dissabels comparator)
    que_dict = {
        1:__REG_CONFIG_CQUE_1CONV, 
        2:__REG_CONFIG_CQUE_2CONV,
        4:__REG_CONFIG_CQUE_4CONV, 
        0:__REG_CONFIG_CQUE_NONE
    }
   
    
	# Dictionary with the sampling speed values
    sps_dict = {
        8:__REG_CONFIG_DR_8SPS,
        16:__REG_CONFIG_DR_16SPS,
        32:__REG_CONFIG_DR_32SPS,
        64:__REG_CONFIG_DR_64SPS,
        128:__REG_CONFIG_DR_128SPS,
        250:__REG_CONFIG_DR_250SPS,
        475:__REG_CONFIG_DR_475SPS,
        860:__REG_CONFIG_DR_860SPS
    }    
  
  	# Dictionary with the programable gains
    pga_dict = {
        6144:__REG_CONFIG_PGA_6_144V,
        4096:__REG_CONFIG_PGA_4_096V,
        2048:__REG_CONFIG_PGA_2_048V,
        1024:__REG_CONFIG_PGA_1_024V,
        512:__REG_CONFIG_PGA_0_512V,
        256:__REG_CONFIG_PGA_0_256V
    } 
    
    # Dictionary with mux configurations
    mux_dict = {
        'chan 0': __REG_CONFIG_MUX_SINGLE_0,
        'chan 1': __REG_CONFIG_MUX_SINGLE_1,
        'chan 2': __REG_CONFIG_MUX_SINGLE_2,
        'chan 3': __REG_CONFIG_MUX_SINGLE_3,
        'chan 0_1': __REG_CONFIG_MUX_DIFF_0_1,
        'chan 0_3': __REG_CONFIG_MUX_DIFF_0_3,
        'chan 1_3': __REG_CONFIG_MUX_DIFF_1_3,
        'chan 2_3': __REG_CONFIG_MUX_DIFF_2_3
    }   	
 
    # Constructor: Initializes an ADS1115 object in single-shot, ADC mode (comparator off)
	#              with data rate of 128 sps, programmable gain in the range of +- 4.096,
	#              collecting data from channel 0.
	# PARAMS:
	#   1) address is the address of slave device (hardware selected). 
	#	   One of: 0x48,  0x49,  0x4A, 0x4B  
	#	2) bus_num is the I2C bus ADS1115 is wired to on the MicroPython board. 
	#	   One of: 1, 2
	#	3) freq is the desired operating frequency of the ADS1115. 
	#	   100 kHz - 400 kHZ is standard and fast mode. Above 400kHz requires HS mode
	#	4) general_call is boolean enabling the I2C line's recognition of the general call
	#          
	       
	
    def __init__(self, address=0x48, bus_num=1, freq = 100000, general_call = True):
	   
		
		
        if (bus_num < 1) or (bus_num > 2):
            print ('The Bus number is out of range. bus_num must be either 1 or 2\n')
            return -1
			
		# Initialize hardware  		
       
        self.i2c = I2C(bus_num,I2C.MASTER,baudrate=100000)
        #self.i2c = I2C(bus_num)
        #self.i2c.init(I2C.MASTER, baudrate = freq, gencall = general_call)
		
		
        self.address= address
        self.gencall = general_call
        self.acqmode = 'single'
        self.comp_mode = 'trad'
        self.comp_pol = 'low'
        self.latch = 'nolatch'
        self.que = 0
        self.sps = 128
        self.pga = 4096
        self.mux = 'chan 0'
        
        #initialize register values to zero then set config reg
        self.lowthresh_reg = 0x0000
        self.highthresh_reg = 0x0000
        self.config = 0x0000 
        
        self.config = self.acqmode_dict['single'] | \
                      self.compmode_dict['trad']  | \
                      self.comppol_dict['low']   | \
                      self.latch_dict['nolatch']  | \
                      self.que_dict[0]        | \
                      self.sps_dict[128]          | \
                      self.pga_dict[4096]         | \
                      self.mux_dict['chan 0']

    # MODIFIES: self.
	# 
	# PARAMS:
	# 1) acqmode is one of: 'contin', 'single'.               default: 'single'
	# 2) compmode is one of: 'trad', 'window'.                default: 'trad'
	# 3) pol is one of: 'low', 'high'.                        default: 'low'
	# 4) latch is one of 'latch', 'nolatch'.                  default: 'no latch'
	# 5) que is one of: 0,1,2,4.  0 disables comparator       default: 0
	# 6) pga is the programmable gain amplifier.              default: '6144' 
	#	 One of: 6144, 4096, 2048, 1024, 512, 256	   			
	# 7) sps  is the data rate in samples per second.         default: '250'
	#	 One of: 8, 16, 32, 64, 128, 250, 475, 860 	
	# 8)mux is one of:'chan 0', 'chan 1', 'chan 2', 'chan 3', default: 'chan 0'
	#              'chan 0_1','chan 0_3', 'chan 1_3', 'chan 2_3'  .
	# RETURNS: nothing 
	                 
    def setConfig(self,acqmode='single', compmode='trad', pol='low', latch='nolatch', que=0, pga=4096, sps=128, mux='chan 0'):
        
        #error handling
        if (acqmode not in self.acqmode_dict):	  
            print ("acqmode must be one of: 'contin', 'single'. using 'single'\n")
            self.acqmode = 'single'
        elif (compmode not in self.compmode_dict):	  
            print ("compmode must be one of: 'trad', 'window'. using 'trad'\n")
            self.comp_mode = 'trad'
        elif (pol not in self.comppol_dict):	  
            print ("pol must be one of: 'low', 'high'. using 'low'\n")
            self.comp_mode = 'low'
        elif (latch not in self.latch_dict):	  
            print ("latch must be one of: 'latch', 'nolatch'. using 'nolatch'\n")
            self.latch = 'nolatch'
        elif (que not in self.que_dict):	  
            print ("que must be one of: 1,2,4,0. using 0\n")
            self.que = 0
        elif (pga not in self.pga_dict):	  
            print ('pga must be one of 6144, 4096, 2048, 1024, 512, 256, using 6144mV')      
            self.pga = 6144
        elif (sps not in self.sps_dict):	  
            print ("sps must be one of 8, 16, 32, 64, 128, 250, 475, 860. using 250.\n")
            self.sps = 128
        elif (mux not in self.mux_dict):	  
            print ("mux must be one of 'chan 0', 'chan 1', 'chan 2', 'chan 3','chan 0_1','chan 0_3', 'chan 1_3', 'chan 2_3'.  using 'chan 0'.\n")
            self.mux = 'chan 1'                 
        else: 
            self.acqmode = acqmode
            self.comp_mode = compmode
            self.comp_pol = pol
            self.latch = latch
            self.que = que
            self.sps = sps
            self.pga = pga
            self.mux = mux
        
        self.config = 0x0000 #initialize config to 0
        self.config = self.acqmode_dict[self.acqmode]    | \
                      self.compmode_dict[self.comp_mode] | \
                      self.comppol_dict[self.comp_pol]  | \
                      self.latch_dict[self.latch]        | \
                      self.que_dict[self.que]            | \
                      self.sps_dict[self.sps]            | \
                      self.pga_dict[self.pga]            | \
                      self.mux_dict[self.mux] 



    # Getter Functions 
    #
    #------------------
    def getAddress(self):
        return self.address
        
    def getAcqmode(self):
        return self.acqmode
        
    def getCompMode(self):
        return self.comp_mode
        
    def getCompPol(self):
        return self.comp_pol
    
    def getLatch(self):
        return self.latch
        
    def getQue(self):
        return self.que 
        
    def getDataRate(self):
        return self.sps
        
    def getPGA(self):
        return self.pga
        
    def getChannel(self):
        return self.mux
        
    # Setter Functions
    #
    #------------------- 
    
    def setChannel(self, chan):
        #clear mux selection bits in config register
        self.config &= 0b1000111111111111
        self.config |= self.mux_dict[chan]
        self.mux = chan
        

    
    def setPGA(self, pga):
        #clear pga bits
        self.config &= 0b1111000111111111
        self.config |= self.pga_dict[pga] 
        self.pga = pga
            
    def setAcqmode(self, mode):
        #clear acquisition mode bit
        self.config &= 0b1111111011111111
        self.config |= self.acqmode_dict[mode]
        self.acqmode = mode
        
    def setDataRate(self, sps):
        #clear sps bits
        self.config &= 0b1111111100011111
        self.config |= self.sps_dict[sps] 
        self.sps = sps
        
    def setCompMode(self, mode):
        #clear comparator mode bits
        self.config &= 0b1111111111101111
        self.config |= self.compmode_dict[mode] 
        self.comp_mode = mode
            
        
    def setComPol(self, pol):
        #clear latch polarity bits
        self.config &= 0b1111111111110111
        self.config |= self.comppol_dict[pol]
        self.comp_pol = pol
            
        
     def setLatch(self, latch):
        #clear latch bits
        self.config &= 0b1111111111111011
        self.config |= self.latch_dict[latch]
        self.latch = latch
            
        
     def setQue(self, que):
        #clear comparator que and disable bits
        self.config &= 0b1111111111111100
        self.config |= self.que_dict[que]
        self.que = que
             
        
      
    
     
    # Prints the current configuration of ADS1115
    #
    # MODIFIES: Nothing.
	# 
	# PARAMS: None
	#
	# RETURNS: Nothing    
    def printConfiguration(self):
    
        print ("device address:")
        print (self.getAddress())
        print ("generall call endabled ?")
        print (self.gencall)
        print ("acquisition mode:")
        print (self.getAcqmode())
        print ("comparator mode:")
        print (self.getCompMode())
        print ("comparator polarity:")
        print (self.getCompPol())
        print ("latch ?")
        print (self.getLatch())
        print ("que:")
        print (self.getQue())
        print ("SPS:")
        print (self.getDataRate())
        print ("PGA:")
        print (self.getPGA())
        print ("mux/channels in use:")
        print (self.getChannel())
        print ("low thresh register value:")
        print (hex(self.lowthresh_reg))
        print ("high thresh register value:")
        print (hex(self.highthresh_reg))
        print ("config register value:")
        print (hex(self.config))

   
        

    # starts a conversion based on the mode specified by bits in the config register
    # assumes device is configured for ADC acquisition NOT comparator acquisition
    #
    # MODIFIES: self.config.
	# 
	# PARAMS: Delay (desired timeout delay in ms)
	# 
	# RETURNS: nothing
    def startADCConversion(self, delay=5000):
    
        if(self.acqmode=='single'):
            # Set 'start single-conversion' bit 
            self.config |= self.__REG_CONFIG_OS_SINGLE
    	
        
        #if device is ready fro instruction
        if(self.i2c.is_ready(self.address)):
            #fill buffer with memory address of config register followed by the data to be written
            data_buf = bytearray([self.__REG_POINTER_CONFIG,(self.config >> 8) & 0xFF, self.config & 0xFF])
            #send data
            self.i2c.send(data_buf,self.address)            
        
        else:
            print("The slave device is not ready. i2c.id_ready() returned false") 
            
      
          
    # starts a conversion based on the mode specified by bits in the config register
    # assumes device is configured for Comparitor acquisition NOT ADC acquisition
    #
    # MODIFIES: self
	# 
	# PARAMS: 1) threshhold_H is the upper threshold for the comparator in mV
	#         2) theshold_L is the lower threshold for the comparator in mV
	#         3) delay (timout dely in ms)
	# RETURNS: nothing
    def startCompConversion(self, threshold_H, threshold_L, delay=5000):
        
        if(self.getQue()==0):
            print("Comparator is currently configured to be off, self.que == 0. self.que must be either 1,2 or 4 to operate as a comparator.")
    
        if(self.acqmode=='single'):
            # Set 'start single-conversion' bit 
            self.config |= self.__REG_CONFIG_OS_SINGLE
        
        
        #convert threshold_H to 16bit int and write to Hi_thresh register
        self.highthresh_reg = int(threshold_H*(32767.0/self.pga))
        
        #fill buffer with memory address of highthresh register followed by the data to be written and send it
        data_buf = bytearray([self.__REG_POINTER_HITHRESH,(self.highthresh_reg >> 8) & 0xFF, self.highthresh_reg & 0xFF])
        self.i2c.send(data_buf,self.address,timeout=delay)
        
      
        #convert threshold_L to 16bit int and write to Lo_thresh register
        self.lowthresh_reg = int(threshold_L*(32767.0/self.pga))
        
        #fill buffer with memory address of lowthresh register followed by the data to be written and send it
        data_buf = bytearray([self.__REG_POINTER_LOWTHRESH,(self.lowthresh_reg >> 8) & 0xFF, self.lowthresh_reg & 0xFF])
        self.i2c.send(data_buf,self.address,timeout=delay)

        #write to config reg to start conversion
        data_buf = bytearray([self.__REG_POINTER_CONFIG, (self.config >> 8) & 0xFF, self.config & 0xFF])
        self.i2c.send(data_buf,self.address,timeout=delay)        
        

    # reads conversion register and returns the value as an int in mV
    #
    # MODIFIES: Nothing.
	# 
	# PARAMS: delay (timout delay in ms) 
	# 
	# RETURNS: Value held in conversion register
     
    def readConversion(self, delay=5000):
        
        if(self.i2c.is_ready(self.address)):     
            result_buf = bytearray(2)
            
            #point the device to its conversion register
            self.i2c.send(self.__REG_POINTER_CONVERT,self.address)
            #get data from the conversion register and put the result into result_buf
            self.i2c.recv(result_buf, self.address)	
            
            #convert raw bits into millivolts and return the value
            val = (result_buf[0] << 8) | (result_buf[1])
            if val > 0x7FFF:
                return (val - 0xFFFF)*self.pga/32768.0
            else:
                return ( (result_buf[0] << 8) | (result_buf[1]) )*self.pga/32768.0
        else:            
            print("The slave device is not ready. i2c.id_ready() returned false") 
            
    
    # Writes a 2 byte value to Hi_thresh register
    #
    # MODIFIES: self.
	# 
	# PARAMS: 
	#       1) val. the value in millivolts to be written to hi threshold register
	#       2) delay (timout delay in ms) 
	# 
	# RETURNS: Nothing
	
    def writeToHi(self,val, delay=5000):
        
        #convert threshold_H to 16bit int and write to Hi_thresh register
        self.highthresh_reg = int(val*(32767.0/self.pga))
        
        #fill buffer with memory address of highthresh register followed by the data to be written and send it
        data_buf = bytearray([self.__REG_POINTER_HITHRESH,(self.highthresh_reg >> 8) & 0xFF, self.highthresh_reg & 0xFF])
        self.i2c.send(data_buf,self.address,timeout=delay)
        
    
    # Writes a 2 byte value to Lo_thresh register
    #
    # MODIFIES: self.
	# 
	# PARAMS: 
	#       1) val. the value in millivolts to be written to low threshold register
	#       2) delay (timout delay in ms) 
	# 
	# RETURNS: Nothing
	
    def writeToLow(self,val, delay=5000):
        
        #convert threshold_L to 16bit int and write to Lo_thresh register
        self.lowthresh_reg = int(val*(32767.0/self.pga))
        
        #fill buffer with memory address of lowthresh register followed by the data to be written and send it
        data_buf = bytearray([self.__REG_POINTER_LOWTHRESH,(self.lowthresh_reg >> 8) & 0xFF, ads.lowthresh_reg & 0xFF])
        self.i2c.send(data_buf,self.address,timeout=delay)
      
    # Writes a 2 byte value to Lo_thresh register
    #
    # MODIFIES: self.
	# 
	# PARAMS: 
	#       1) reg. Name of register to be read. One of:
	#          'hithresh', 'lowthresh', 'convert', 'config' 
	#       2) delay (timout delay in ms) 
	# 
	# RETURNS: Value contained in specifies register  
    def readRegister(self, reg, delay=5000):
        
        if(self.i2c.is_ready(self.address)):     
            result_buf = bytearray(2)
            
            #point the device to its conversion register
            self.i2c.send(self.reg_dict[reg],self.address)
            #get data from the specified register and put the result into result_buf
            self.i2c.recv(result_buf, self.address)	
            
            
            val = (result_buf[0] << 8) | (result_buf[1])
            return hex(val)
            
    
        
            
    # reads busy bit in config register to see if a conversion is in progress
    #
    # MODIFIES: Nothing
	# 
	# PARAMS:delay (timout dely in ms) 
	# 
	# RETURNS: Boolean
     
    def isConversionDone(self, delay=5000):
        
         
        result_buf = bytearray(2)
    	# Read the config register
        self.i2c.send(self.__REG_POINTER_CONFIG,self.address)
        self.i2c.recv(result_buf,self.address)
    		
    	# Return a mV value for the ADS1115
		# (Take signed values into account as well)
		
        val = (result_buf[0] << 8) | (result_buf[1])
        val &= 0x8000
        if (val == 0x8000):
            return False
        else:
            return True

    # issues SMBUS alert response to clear a latched ALERT/RDY pin
    # assumes the device is configured in latching mode (self.latch = 'latch')
    # Note: Simply reading the conversion register accomplishes the same thing
    #
    # MODIFIES: Nothing.
	# 
	# PARAMS: delay (timout dely in ms)
	# 
	# RETURNS: Nothing
    
    def smbusAlertResponse(self, delay=5000):
    
         
        self.i2c.send(0x19,self.address,timeout=delay)

   
   
    # issues general call, then if any device responds, issues a command to
    # enter power down mode.
    # 
    # assumes self was initialized with the general call enabled (general_call = True) 
    #
    # MODIFIES: Nothing.
	# 
	# PARAMS: delay (timout dely in ms)
	# 
	# RETURNS: Nothing
    def enterPowerDown(self, delay=5000):
         
        
        #general call 
        self.i2c.send(0x00,self.address,timeout=delay)
        
        #scan for response
        respond = self.i2c.scan()
        
        if (self.address in respond):
            #enter power down command
            self.i2c.send(0x06,self.address,timeout=delay)

    # Configures the ALERT/RDY pin as a conversion ready pin (page 15 of ADS115 data sheet)
    # Sets MSB of Hi_thresh to 1, and MSB of Lo_tresh to 0
    # 
    #  
    #
    # MODIFIES: self.
	# 
	# PARAMS: None
	# 
	# RETURNS: Nothing
    def setConvReadyPin(self,delay=5000):
         
       
        
        #set MSB in Hi_thresh reg to 1
        self.highthresh_reg |= 0x8000
        
        #set MSB in Lo_thresh reg to 0
        self.lowthresh_reg &= 0x7FFF
        
        data_buf = bytearray([self.__REG_POINTER_HITHRESH,(self.highthresh_reg >> 8) & 0xFF, self.highthresh_reg & 0xFF])
        self.i2c.send(data_buf,self.address,timeout=delay)
     
        data_buf = bytearray([self.__REG_POINTER_LOWTHRESH,(self.lowthresh_reg >> 8) & 0xFF, self.lowthresh_reg & 0xFF])
        self.i2c.send(data_buf,self.address,timeout=delay)


 
# example function to read continuously from a specified channel and print value to screen 
# This function works in single channel or differential acquisition mode.
# For single channel, chan should be one of: 'chan 0','chan 1', 'chan 2', 'chan 3'. (make sure you include the single quotes) 
# For differential mode, chan should be one of: 'chan 0_1','chan 0_3', 'chan 1_3', 'chan 2_3'. 
# (These are the only channel combinations this chip offers )

def printContinousVoltage(self, chan):
    
     
    
    # configure object for continuous collection
    # and activate specified channel 
    self.setConfig(acqmode='contin',mux=chan)  
    
    # write to configuration register and start conversion
    self.startADCConversion()
    
    # read value and print to screen
    while True:
        
        res = self.readConversion()
        print(res)
        pyb.delay(1000)
        


# example function to read  from a specified channel once and print value to screen 
# This function works in single channel or differential acquisition mode.
# For single channel, chan should be one of: 'chan 0','chan 1', 'chan 2', 'chan 3'. (make sure you include the single quotes) 
# For differential mode, chan should be one of: 'chan 0_1','chan 0_3', 'chan 1_3', 'chan 2_3'. 
# (These are the only channel combinations this chip offers )        

def printSingleShotVoltage(self, chan):
    
     
    
    # configure object for continuous collection
    # and activate specified channel 
    self.setConfig(acqmode='single',mux=chan)  
    
    # write to configuration register and start conversion
    self.startADCConversion()
    
    # read value and print to screen
    
    res = self.readConversion()
    print(res)
    
    

           
