# main.py -- Accelerometer

import pycom
import time
from machine import I2C

BaudRate = 100000
SDA='P22'
SCL='P21'

SCALE = 8000 #Value to adjust the register read value. This value depends of the Full Scale (Is set to the FS of 4G)
FULLSCALE = 4
ACC_G_DIV = 1000 * 65536

i2c = I2C(0, I2C.MASTER, baudrate=BaudRate, pins=(SDA, SCL))
# Inicia o barramento i2c. dizendo ao lopy os pinos a que estão ligados os sensores

def lis2hh12_init():
    #Configures the CTRL1 Register at HR mode and at 10Hz readings.
    i2c.writeto_mem(0x1E, 0x20, 0b10010111)

    #Configures the CTRL4 Register to 4G Full Scale
    i2c.writeto_mem(0x1E, 0x23, 0b00100100)

    return

def lis2hh12_getX():
    x = i2c.readfrom_mem(0x1E, 0x28, 2)
    xn = (((x[1]<<8) + x[0]))*(SCALE/ACC_G_DIV)

    if(xn>=FULLSCALE):
        xn = xn-FULLSCALE*2

    return xn

def lis2hh12_getY():
    y = i2c.readfrom_mem(0x1E, 0x2A, 2)
    yn = (((y[1]<<8) + y[0]))*(SCALE/ACC_G_DIV)

    if(yn>=FULLSCALE):
        yn = yn-FULLSCALE*2

    return yn

def lis2hh12_getZ():
    z = i2c.readfrom_mem(0x1E, 0x2C, 2)
    zn = (((z[1]<<8) + z[0]))*(SCALE/ACC_G_DIV)

    if(zn>=FULLSCALE):
        zn = zn-FULLSCALE*2

    return zn


lis2hh12_init()
while 1:
    print("x:", lis2hh12_getX(), "\ty: ", lis2hh12_getY(), "\tz: ", lis2hh12_getZ())
    time.sleep_ms(20)
