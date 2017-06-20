from pyb import UART
from lepton import flirLepton


uart = UART(1, 9600) 
## initialize a lepton object on micropy boards SPI1 bus at 10500000 baud, I2C2 at 100000 baud
lepton = flirLepton()

##enable automatic histogram equalization on the Lepton module
lepton.AGC_enable()


## read a frames-worth of data into frame_data field
lepton.leptonReadFrame()

## write each pixel to the serial bus


for x in range(lepton.frame_width):
    for y in range(lepton.frame_height):
        
        uart.write(lepton.leptonReadPixel(x,y))
        





