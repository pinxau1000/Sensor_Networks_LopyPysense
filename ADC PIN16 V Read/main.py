# main.py - ADC Readings

#Imports
import time
import pycom
import machine
from machine import ADC
from network import WLAN
from simple import MQTTClient

#NETWORK Related Variables/Definitions
WIFI_NAME='droid_wlan'
WIFI_PW='WlanDr01d16'

#MQTT Related Variables/Definitions
MQTT_CLIENT_ID = '05152740-ff6d-11e7-8412-27102f4df5be'
MQTT_PROVIDER = 'mqtt.mydevices.com'
MQTT_USERNAME = '8fe103e0-d9a1-11e7-b67f-67bba9556416'
MQTT_PW = '36e678f20f27ac8fd15985d201a15e5fbe89a282'
MQTT_PORT = 1883
TOPIC_PUBLISH = 'v1/'+MQTT_USERNAME+'/things/'+MQTT_CLIENT_ID+'/data/'

MQTT_CHANNEL_BAT = '2000'

ADC_BITS = 12
MAX_SAMPLES = 1000

#NETWORK connection
pycom.heartbeat(False)
pycom.rgbled(0x550000) #Dark Red - Not Connected to WLAN

wlan = WLAN(mode=WLAN.STA)
wlan.connect(WIFI_NAME, auth=(WLAN.WPA2, WIFI_PW), timeout=5000)
while not wlan.isconnected():
    pycom.rgbled(0x550000) #Dark Red - Not Connected to WLAN
    machine.idle() #save power while waiting

for i in range(0, 5):
    pycom.rgbled(0x005500) #Dark Green - Connected to WLAN
    time.sleep_ms(100)
    pycom.rgbled(0x0) #LED OFF
    time.sleep_ms(100)

#MQTT Connection Client
client = MQTTClient(MQTT_CLIENT_ID, MQTT_PROVIDER, user=MQTT_USERNAME, password=MQTT_PW , port=MQTT_PORT)
time.sleep_ms(200)
client.connect()

for i in range(0, 5):
    pycom.rgbled(0x000055) #Dark Blue - Connected to MQTT
    time.sleep_ms(100)
    pycom.rgbled(0x0) #LED OFF
    time.sleep_ms(100)

adc = ADC()                   # Create an ADC object
adc.init(bits=ADC_BITS)       # Enables the ADC block with 12 bits width samples
apin = adc.channel(pin='P16', attn=ADC.ATTN_11DB)   # Create an analog pin on P16, with 11 db Attenuation so the V range is 0 to 3.3V

#Main Cycle
while 1:
    val = 0;
    for i in range(0,MAX_SAMPLES):
        val += apin.value()

    val = (val/MAX_SAMPLES)     		#Mean of 1000 Samples to reduce the noise/glitches
    val = (3.3/((2**ADC_BITS)-1))*val   #Scale/Mapping of the value to voltage
    #3.3V is the maximum value of the input for a 11dB Attenuation

    #Battery
    client.publish(topic=TOPIC_PUBLISH+MQTT_CHANNEL_BAT, msg="voltage,v="+str(val))
    print('My Battery: ', val, ' (V)')
    time.sleep_ms(200)
