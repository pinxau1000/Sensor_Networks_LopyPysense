# main.py -- Humidity & Temperature

import pycom
import time
from machine import Pin
from machine import I2C

BaudRate = 100000
SDA='P22'
SCL='P21'

i2c = I2C(0, I2C.MASTER, baudrate=BaudRate, pins=(SDA, SCL))
#Inicia o barramento i2c. dizendo ao lopy os pinos a que estão ligados os sensores

def Si7006_init():
    i2c.writeto(64, 0xFE) 	#Reset
    time.sleep_ms(100) 		#setling time
    #resolution by default(E7 register): 12bit for RH and 14bit to Temp
    #heater off
    return

def Si7006_getHumTemp():
    i2c.writeto(64, 0xF5)	#relative humidity no hold
    time.sleep_ms(20)		#conversion time(max is 12ms)
	
    readH = i2c.readfrom(64, 2)
    H = (readH[0]<<8)+readH[1]
    H = (125*H/65536)-6

    readT = i2c.readfrom_mem(64, 0xE0, 2)
    T = (readT[0]<<8)+readT[1]
    T = (175.72*T/65536)-46.85
	
    return(H,T)


Si7006_init()
while 1:

    H, T = Si7006_getHumTemp()
    print("Humidity: ", H, ' (%RH)', "\tTemperature: ", T, ' (*C)')
    time.sleep_ms(500)
