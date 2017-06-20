import pyb
from ADS1115 import ADS1115






# Initializes an ADS1115 object in/with: 
# 1) Slave address = 0x48
# 2) I2C bus 1
# 3) Baud rate 100000 Hz 
# 4) General call supported
# 5) Single-shot ADC mode 
# 6) Comparator off (que = 0)
# 7) Data rate of 128 sps 
# 8) Programmable gain in the range of +- 4.096
# 9) Collecting data from channel 0

ads = ADS1115()

# Prints the current settings for the ADS1115 configuration register.

ads.printConfiguration()

# Sets the configuration of the current object to:
#        1) continuous sample collection 
#        2) comparator in window mode
#        3) active-low ALRT/RDY pin
#        4) active-low ALRT/RDY pin doesn't latch
#        5) comparator will assert the ALRT/RDY pin once 4 
#           consecutive samples have exceeded the window specified by
#           the Lo_thresh and Hi_thresh registers
#        6) programmable gain is set to +- 6.144 range
#        7) data rate set to 250 samples per second
#        8) The voltage reading is taken from the differential pair
#           of channel 1 (+) channel 3 (-)

ads.setConfig('contin','window','low','nolatch',4,6144,250,'chan 1_3')


# returns current object to default settings.  
ads.setConfig()


# sets channel 2 as active channel and returns all other fields to default
ads.setConfig(mux='chan 2')


#NOTE: To set one aspect of an ADS1115 object's configuration while maintaining the current settings 
#     for the others (not returning them to default) use the 'setter functions'


# Sets active channel to channel 0 (+) and channel 3 (-). 
# All other fields retain the same value prior to the function call.
ads.setChannel('chan 0_3') 

# returns active channel 
channel = ads.getChannel()

# writes the current configuration register settings to the ADS1115 configuration register
# and starts a conversion. Timeout is set to 1s (default is 5s if no parameter specified). 
# Assumes the configuration register has self.que = 0 (disable comparator). 
# Will still work if comparator is enabled but the threshold values used will be whatever was last loaded into them.

ads.startADCConversion(1000)

# returns the value held in the ADS1115 conversion register.
# currently returns a millivolt value
# sets timeout to 2s
res = ads.readConversion(2000)


# 1) Puts the comparator into traditional ('trad') mode.
# 2) Enables comparator ( que != 0) and asserts ALRT/RDY pin if 2 
#    consecutive samples rise above the high threshold.
# 3) Starts a comparator conversion with:
#                         high threshold = 1000 mv (1v)
#                         low threshold = -2000 mv (-1v)

#1)
ads.setCompMode('trad')
#2)
ads.setQue(2)
#3)
ads.startCompConversion(1000, -2000)



# Reads voltage from conversion register and returns millivolt value.
ads.readConversion()


# Reads the 'conversion ready' bit of the config register
# to determine if a conversion is in progress.
status = ads.isConversionDone()


# Clears a latched ALRT/RDY pin without reading the conversion register. 
# Reading from the conversion register accomplishes the same task, however.

# NOTE: Untested.
ads.smbusAlertResponse()


# Issues a general call, then if any device responds, issues a command to
# enter power down mode.
# Assumes self was initialized with the general call enabled (general_call = True)

# NOTE: untested.
ads.enterPowerDown()


# Configures the ALERT/RDY pin as a conversion ready pin (page 15 of ADS115 data sheet)
# Sets MSB of Hi_thresh to 1, and MSB of Lo_tresh to 0

#NOTE:untested
ads.setConvReadyPin()


#example function to read continuously from a specified channel and print value to screen 

def readChan(chan):
    
    ads = ADS1115() #instantiate object 
    
    # configure object for continuous collection
    # and activate specified channel 
    ads.setConfig(acqmode='contin',mux=chan)  
    
    # write to configuration register and start conversion
    ads.startADCConversion()
    
    # read value and print to screen
    while True:
        
        res = ads.readConversion()
        print(res)
        pyb.delay(500)

   














      
        