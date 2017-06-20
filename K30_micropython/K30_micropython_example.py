from K30_micropython import K30
import pyb

mac_address = 123456789

#create a K30 instance with mac address
# and default i2c_addr= 0x68, I2C_bus_number=1, baud_rate = 100000 Hz (100 kHz)
CO2_sensor = K30(mac_address)

# Loop forever
while(True):

    # aquire and print a CO2 reading from the K30 sensor
    CO2_sensor.printCO2()
    
    #delay 200ms
    pyb.delay(200)