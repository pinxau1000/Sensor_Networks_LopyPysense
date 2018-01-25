#main.py -- Barometer

import pycom
import time
from machine import Pin
from machine import I2C

BaudRate = 100000
SDA='P22'
SCL='P21'

REGION_WEATHER_OFFSET = 125

i2c = I2C(0, I2C.MASTER, baudrate=BaudRate, pins=(SDA, SCL))

def MPL3115A2_init():
    #Activates the data acquisition from the sensor (Clear StandBy Mode)
    CTRL_REG1 = bytearray(1)
    i2c.readfrom_mem_into(0x60, 0x26, CTRL_REG1)
    CTRL_REG1[0] |= 0b00000001
    time.sleep_ms(50)
    i2c.writeto_mem(0x60, 0x26, CTRL_REG1)
    return

def MPL3115A2_getPress():
    #Overwrites the current value of the CTRL_REG1 and only changes the ALT bit and the !Active Bit!
    CTRL_REG1 = bytearray(1)
    i2c.readfrom_mem_into(0x60, 0x26, CTRL_REG1)
    CTRL_REG1[0] &= 0b01111111
    time.sleep_ms(50)
    i2c.writeto_mem(0x60, 0x26, CTRL_REG1)

    read = i2c.readfrom_mem(0x60, 0x01, 3)
    #Gets the integer part of the PRESSURE
    press_int = ((read[0] << 10) + (read[1] << 2) + ((read[2] >> 6)))
    #Gets the floating part of the PRESSURE
    press_float = ((read[2]>>4) & 0b00000011)

    return (press_int+(press_float*2**-2))

def MPL3115A2_getAlt():
    #Overwrites the current value of the CTRL_REG1 and only changes the ALT bit and the !Active Bit!
    CTRL_REG1 = bytearray(1)
    i2c.readfrom_mem_into(0x60, 0x26, CTRL_REG1)
    CTRL_REG1[0] |= 0b10000000
    time.sleep_ms(50)
    i2c.writeto_mem(0x60, 0x26, CTRL_REG1)

    read = i2c.readfrom_mem(0x60, 0x01, 3)
    #Int part of Altitude
    alt_int = ((read[0]<<8) + read[1])
    #Decimal part of Altitude
    alt_float = ((read[2]>>4) & 0b00001111)

    if(alt_int > 32767):
        alt_int -= 65536

    return (alt_int+(alt_float*2**-4))

def MPL3115A2_setMode(ALT):
    if(ALT!=0 and ALT!=1):
        return -1

    #Overwrites the current value of the CTRL_REG1 and only changes the ALT bit.
    CTRL_REG1 = bytearray(1)
    i2c.readfrom_mem_into(0x60, 0x26, CTRL_REG1)

    #print(bin(CTRL_REG1[0]))
    if(ALT == 1):
        CTRL_REG1[0] |= 0b10000000
    elif(ALT == 0):
        CTRL_REG1[0] &= 0b01111111
    #print(bin(CTRL_REG1[0]))

    i2c.writeto_mem(0x60, 0x26, CTRL_REG1)
    return ALT

def MPL3115A2_getALtPress(ALT):
    if(ALT!=0 and ALT!=1):
        return -1

    read = i2c.readfrom_mem(0x60, 0x01, 3)
    #print('Read: ', read, '\tRead_Bin: ', bin(read[0]), ' - ', bin(read[1]), ' - ', bin(read[2]))

    if(ALT==1):
        #Gets the integer part of the ALTITUDE
        alt_int = ((read[0]<<8) + read[1])

        #Gets the floating part of the ALTITUDE
        alt_float = ((read[2]>>4) & 0b00001111)

        #print('INTEIRA: ', alt_int, '\tDECIMAL: ', alt_float)

        if alt_int > 32767:
            alt_int -= 65536

        return (alt_int+(alt_float*2**-4))
    elif(ALT==0):
        #Gets the integer part of the PRESSURE
        press_int = ((read[0] << 10) + (read[1] << 2) + ((read[2] >> 6)))

        #Gets the floating part of the PRESSURE
        press_float = ((read[2]>>4) & 0b00000011)

        #print('INTEIRA: ', press_int, '\tDECIMAL: ', press_float)

        return (press_int+(press_float*2**-2))

def pascal_2_bar(pascal):
    return pascal/100000

def pascal_2_atm(pascal):
    return pascal/(9.86923267*(10**-6))

MPL3115A2_init()
while 1:
    pressure_pascal = MPL3115A2_getPress()
    print('PRESSURE: ', pressure_pascal, ' (pa);\t', pascal_2_bar(pressure_pascal), ' (bar);\t', pascal_2_atm(pressure_pascal), ' (atm)')
    alt = 44330.77*(1-((pressure_pascal/101326)**0.1902632))+REGION_WEATHER_OFFSET	#DATASHEET FORMULA
    print('ALTITUDE: ', alt, ' (m)')
    time.sleep_ms(500)
