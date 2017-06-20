from pyb import SPI
from pyb import Pin
from pyb import I2C

# SPI bus 1 has: (NSS, SCK, MISO, MOSI) = (X5, X6, X7, X8) = (PA4, PA5, PA6, PA7), is on APB2 clk with max freq of 84MHz
# SPI bus 2 has: (NSS, SCK, MISO, MOSI) = (Y5, Y6, Y7, Y8) = (PB12, PB13, PB14, PB15), is on APB1 with max freq of 42MHZ
#


#for SPI image data transfer:
    # 1) deassert CS and idle sCK for 5 frame periods (> 185 msec)
    # 2) Assert /CS and enable SCLK
    # 3) Examine the ID field of the packet, identifying a discard packet
    # 4) Continue reading packets. When a new frame is available 
    #    (should be less than 39 msec after asserting /CS and reading the first packet), 
    #     the first video packet will be transmitted. The master and slave are now synchronized.
    # 5) LEPTON SPI bus has max baud rate of 20MHz, because of Pyboard limitations 
    #    pyboard SPI_bus can only have multiples of its max frequnecy (either 21MHz or 10.5MHz)
    
    
#for i2C communication:
# 1) device ID 0x2A
# 2) all transfers and registers are 16 bits
#    Not sure if we need to append a zero onto all i2c writes less than 0x0F
#    to meet this constraint, or if sending 0x01 on the I2C bus will be interpreted as 0x0001       
# 3)
# 4)
# 5)


class flirLepton:

#image dimension
    frame_width = 80
    frame_height = 60
    packet_ID_length = 2
    packet_CRC_length = 2
    packet_data_length = 160
    packet_length = 164
    
#i2c addresses    
    i2c_address = 0x2A
    
    #registers adressess
    i2c_statusReg = 0x0002
    i2c_commandIdReg = 0x0004
    i2c_dataLengthReg = 0x0006
    i2c_dataReg_0 = 0x0008
    
    #Module IDs
    i2c_AGC_mode = 0x01
    i2c_SYS_mode = 0x02
    i2c_VID_mode = 0x03
    i2c_OEM_mode = 0x08
    
    #Commands
    i2c_get = 0x00
    i2c_set = 0x01
    i2c_run = 0x02
    

    def __init__(self, spi_bus=1,i2c_bus = 2, spi_baud=10500000, i2c_baud = 100000):
    
        ##lepton needs  CPOL=1,CPHA=1. master clock idle is high and data is sample on the rising edge
        self.spi = SPI(spi_bus)
        self.spi.init(SPI.MASTER, baudrate=spi_baud, polarity=1, phase=1, crc=None)
        self.i2c = I2C(i2c_bus,I2C.MASTER, baudrate=i2c_baud)
        self.current_packet=b''
        self.frame_data=b''

        ## make pin fields for CS and SCK to enable lepton synchronization
        # not sure if you can control sck when an spi object has incorporated it

        if(spi_bus == 1):
            self.chipSelect = Pin('X5', Pin.OUT_PP)

            #set cs pin high to de-select the lepton

            self.chipSelect.high()
            ##self.sck = Pin('X6', Pin.OUT_PP)

        elif(spi_bus == 2):
            self.chipSelect = Pin('Y5', Pin.OUT_PP)
            #set cs pin high to de-select the lepton

            self.chipSelect.high()
            ##self.sck = Pin('Y6', Pin.OUT_PP)
        else:
            print("The specified spi_bus number was not legal (1 or 2)") #the specified bus number is not legal   
    


    ###################################
    ###-----Private Functions-------###
    ###################################
    
    ##This function times out the lepton to put it in reset
    
    def _leptonReset(self):
        self.chipSelect.high()
        #186 ms delay because data sheet says a timeout > 185ms is needed 
        pyb.delay(186)
    
    ## This function selects the Lepton to begin packet transfer
    def _leptonBeginTransfer(self):
        self.chipSelect.low() 

    ## This function deselects the Lepton to end packet transfer
    def _leptonEndTransfer(self):
        self.chipSelect.high()
    
    ##This function reads one line of an image and saves it in self.current_packet
    def _leptonReadLine(self, line_num):
        
        #assert chip select
        self._leptonBeginTransfer()
        
        #read 164 bytes of data into packet list
        self.current_packet = self.spi.recv(164) # might want to try self.current_packet = self.spi.send_recv(0x00,self.current_packet)
        
        #if read packet is a discard packet
        if((self.current_packet[0] & 0x0F)==0x0F):
            read_success = False
        #if read packet doesn't match current line number    
        elif(self.current_packet[1] != bytes(str(line_num),'utf8')): 
            read_success = False
        else:
            read_success = True
            
        self._leptonEndTransfer()
        
     
    ##################################    
    ###-----Public Functions-------###   
    ##################################
    
     

    def printFields(self):

        print("--------current packet-----------")
        print(self.current_packet)

        print("---------frame data-------------")
        print(self.frame_data)


    ## This Function reads an entire frame of an image and stores the data in self.frame_data
    def leptonReadFrame(self):
    
        line_num = 0
        while(line_num < self.frame_height):
    
            #if a data packet is either a discard packet or a repeat (the same packet is)
            if(self._leptonReadLine(line_num) == True):
                self.frame_data += self.current_packet[4:]
                line_num+=1
            
       
            
    ## This function creates a look up table within the self.frame_data field.
    ## It can be used to easily write each pixel to serial or whatever bus is needed. 
    ## It assumes the data has already been loaded into self.frame_data by calling leptonReadFrame. 
          
    def leptonReadPixel(self, x, y):
        pixel_index = (y*packet_data_length)+(2*x) 
        high_byte = self.frame_data[pixel_index]
        low_byte = self.frame_data[pixel_index+1] 
    
        return ((high_byte[0] << 8)|low_byte[0])   
        
                  
            
    #################################################
    ###-----------I2C functions--------------########
    ## all registers on the chip are 16 bits ########
    #################################################
    
    ##This function loads a command into the command register of the Lepton
    def lepton_command(self, module_ID, command_ID, command):
        
        ##points to the command register
        self.i2c.send(0x00,self.i2c_address)
        self.i2c.send(0x04,self.i2c_address)
        #self.i2c.send(0x0004,self.i2c_address)
        self.set_reg(self.i2c_commandIdReg,self.i2c_address)
        
        if(module_ID == self.i2c_OEM_mode):
            self.i2c.send(0x48,self.i2c_address)       
        else:
            self.i2c.send((module_ID & 0x0f),self.i2c_address)
        
        ##send the command to the module
        self.i2c.send((((command_ID<<2) & 0xfc)|(command&0x03)),self.i2c_address)
        
        
    ##This function enables AGC mode for automatic histogram equilization    
    def AGC_enable(self):
         
         self.i2c.send(0x01,self.i2c_address)
         self.i2c.send(0x05,self.i2c_address) 
         self.i2c.send(0x00,self.i2c_address)
         self.i2c.send(0x01,self.i2c_address)  
         
    
    #This function selects the register passed into the function
    # i.e If you want to write to the data register, you must first pass the data register
    # address into this function and call it.
    def set_reg(self,reg):
    
         buff = []
         buff[0]=(reg >> 8 & 0xff)
         buff[1]=(reg&0xff)
         self.i2c.send(buff,self.i2c_address)

        #self.i2c.send(reg,self.i2c_address) 
        
        
    ##This function reads num_bytes of data from the register passed into this function 
    ## i.e 4 bytes from the command register   
    def read_reg(self,reg,num_bytes=2):
        
        data=[] 
        self.i2c.set_reg(reg)
        data =  self.i2c.recv(num_bytes,self.i2c_address) 
        
        print("reg:")
        print(reg)  
        print("Data:")
        print(data)
        
        return data
        
     
    ## This function reads data from the Lepton's data register    
    def read_data(self):
    
        while(int.from_bytes(read_reg(self.i2c_statusReg)) & 0x01):
            print("busy")
        
        data_length = read_reg(self.i2c_dataLengthReg)
        
        for d in range(int(data_length/2)):
            data = self.i2c.recv(2,self.i2c_address)
            print(hex(data))  
        
        
        
        
         
          
                   
        
  #####################################
  #####################################
  #LEPTON SDK VERSION OF I2C PROTOCOLS#  
  #####################################
  #####################################
  
  ## The following functions are translations from the Flir C-language SDK for the Lepton
  ## No one seems to use this exact protocol on the net, but I included them here because
  ## its from the horses mouth, albeit a little long in the tooth
  
    def lepton_command_my_version(self, module_ID, command_ID, command_type):
        
        ##points to the command register
        self.set_reg(self.i2c_commandIdReg,self.i2c_address)
        
        buff=[]
        if(module_ID == self.i2c_OEM_mode):
            buff[0] = 0x48
        else:
            buff[0] = module_ID & 0x0F
        
        buff[1] = (((command_ID<<2) & 0xFC)|(command_type&0x03))
        
        self.i2c.send(buff,self.i2c_address)
         
         
    def lep_I2C_Get_Attribute(self, module_ID, commandID, attribute_numBytes = 2, num_words=1):
        
        #poll status register for busy bit
        while(int.from_bytes(read_reg(self.i2c_statusReg)) & 0x01):
            print("Get Attribute polling status reg - pre command") 
         
         
        #Set the Lepton's DATA LENGTH REGISTER first to inform the
        #Lepton Camera how many 16-bit DATA words we want to read.
        dataLengthBuff = bytearray()
        dataLength = attribute_numBytes*num_words # each word is typically 2 bytes, but some are more
        dataLengthBuff=([(self.i2c_dataLengthReg>>8)&0xFF,self.i2c_dataLengthReg&0xFF, (dataLength>>8)&0xFF,dataLength&0xFF])
        self.i2c.send(dataLengthBuff, self.i2c_address)
        
        
            
        #Now issue the GET Attribute Command
        self.set_reg(self.i2c_commandIdReg)
        self.lepton_command_my_version(self, module_ID, command_ID, self.i2c_get)
         
        #Read the statusReg REGISTER and peek at the BUSY Bit
        while(int.from_bytes(read_reg(self.i2c_statusReg)) & 0x01):
            print("Get Attribute polling status reg - post command")    
                 
        # Check statusReg word for Errors?
        errors = int.from_bytes(read_reg(self.i2c_statusReg))
        ##lepton list status errors as signed ints so convert to signed value
        errors = ((errors >> 8) | 0xFF00) if errors > 0 else 0
        errors = - (pow(2,16) - errors)
        print("status regsters errors:")
        print((errors >> 8) & 0xFF)
        
        #If NO Errors then READ the DATA from the DATA REGISTER(s)
        data = self.read_reg(self.i2c_dataReg_0, dataLength)     
            
            
            
    def lep_I2C_Set_Attribute(self, module_ID,commandID, in_data, attribute_numBytes = 2, num_words=1):
        
        #poll status register for busy bit
        while(int.from_bytes(read_reg(self.i2c_statusReg)) & 0x01):
            print("Get Attribute polling status reg - pre command") 
         
        #Now WRITE the DATA to the DATA REGISTER(s)
        self.set_reg(self.i2c_dataReg_0)
        data = self.i2c.send(in_data, self.i2c_address)
         
        #Set the Lepton's DATA LENGTH REGISTER first to inform the
        #Lepton Camera how many 16-bit DATA words we want to read.
        dataLengthBuff = bytearray()
        dataLength = attribute_numBytes*num_words # each word is typically 2 bytes, but some are more
        dataLengthBuff=([(self.i2c_dataLengthReg>>8)&0xFF,self.i2c_dataLengthReg&0xFF, (dataLength>>8)&0xFF,dataLength&0xFF])
        self.i2c.send(dataLengthBuff, self.i2c_address)
        
        
            
        #Now issue the Set Attribute Command
        self.set_reg(self.i2c_commandIdReg)
        self.lepton_command_my_version(self, module_ID, command_ID, self.i2c_set)
         
        #Read the statusReg REGISTER and peek at the BUSY Bit
        while(int.from_bytes(read_reg(self.i2c_statusReg)) & 0x01):
            print("Get Attribute polling status reg - post command")    
                 
        # Check statusReg word for Errors?
        errors = int.from_bytes(read_reg(self.i2c_statusReg))
        ##lepton list status errors as signed ints so convert to signed value
        errors = ((errors >> 8) | 0xFF00) if errors > 0 else 0
        errors = -(pow(2,16) - errors)
        print("status regsters errors:")
        print((errors >> 8) & 0xFF)
        
        
    def lep_I2C_Run_Attribute(self, module_ID,commandID, num_words=1):
        
        #poll status register for busy bit
        while(int.from_bytes(read_reg(self.i2c_statusReg)) & 0x01):
            print("Get Attribute polling status reg - pre command") 
         
       
         
        #Set the Lepton's DATA LENGTH REGISTER first to inform the
        #Lepton Camera how many 16-bit DATA words we want to read.
        dataLengthBuff = bytearray()
        dataLength = 0 #(not sure if this should be 0 or num_words, the LEPTON SDK is unclear)
        dataLengthBuff=([(self.i2c_dataLengthReg>>8)&0xFF,self.i2c_dataLengthReg&0xFF, (dataLength>>8)&0xFF,dataLength&0xFF])
        self.i2c.send(dataLengthBuff, self.i2c_address)
        
        
            
        #Now issue the Run Attribute Command
        self.set_reg(self.i2c_commandIdReg)
        self.lepton_command_my_version(self, module_ID, command_ID, self.i2c_run)
         
        #Read the statusReg REGISTER and peek at the BUSY Bit
        while(int.from_bytes(read_reg(self.i2c_statusReg)) & 0x01):
            print("Get Attribute polling status reg - post command")    
                 
        # Check statusReg word for Errors?
        errors = int.from_bytes(read_reg(self.i2c_statusReg))
        ##lepton list status errors as signed ints so convert to signed value
        errors = ((errors >> 8) | 0xFF00) if errors > 0 else 0
        errors = - (pow(2,16) - errors)
        print("status regsters errors:")
        print((errors >> 8) & 0xFF)
        
                    
            


           
    

