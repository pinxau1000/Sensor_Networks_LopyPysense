# main.py -- Light Sensor

import pycom
import time
from machine import Pin
from machine import I2C

BaudRate = 100000
SDA='P22'
SCL='P21'

#Inicia o barramento i2c. Dizendo ao lopy os pinos a que estão ligados os sensores
i2c = I2C(0, I2C.MASTER, baudrate=BaudRate, pins=(SDA, SCL))

def LTR_329ALS_init():
    i2c.writeto_mem(0x29, 0x80, 0b00000001)	#config sensor, no gain, active mode
    time.sleep_ms(10)	#Tempo para "limpar" o barramento
    return
	
def LTR_329ALS_getLux():
    readLux = i2c.readfrom_mem(0x29, 0x88, 4)
    ch1 = (readLux[1]<<8)+readLux[0]	#ch1
    ch0 = (readLux[3]<<8)+readLux[2]	#ch0
    return(ch0, ch1)

LTR_329ALS_init()
while 1:
    ch0, ch1 = LTR_329ALS_getLux()
    print("CH0: ", ch0, "\tCH1: ", ch1)
    time.sleep_ms(500)
