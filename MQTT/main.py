# main.py - MQTT

#General Imports
import time
import machine
import pycom

#Pycom Library Related Imports
from pysense import Pysense
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE

#NETWORK Imports
from network import WLAN

#MQTT Related Imports
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

#FORMAT: v1/username/things/clientID/data/channel
TOPIC_PUBLISH = 'v1/'+MQTT_USERNAME+'/things/'+MQTT_CLIENT_ID+'/data/'
TOPIC_SUBSCRIBE = 'v1/'+MQTT_USERNAME+'/things/'+MQTT_CLIENT_ID+'/cmd/'

BTN_INT_PIN = 'P14'

TEMP_CH = '0'
HUMI_CH = '1'

LIGHT0_CH = '10'
LIGHT1_CH = '11'

ALTI_CH = '50'
REGION_ALT_OFFSET = 125
PRESS_CH = '51'

RGB_SWITCH_CH = '100'
RGB_PHYSICAL_BTN = 'P14'
RGB_RED_CH = '101'
RGB_GREEN_CH = '102'
RGB_BLUE_CH = '103'

ACCEL_X_CH = '201'
ACCEL_Y_CH = '202'
ACCEL_Z_CH = '203'

BATTERY_CH = '500'

#Global Vars/Flags
switchRGB = '0'
actualRGB = ['00','00','00']

def RgbLedFlash(n_times,hex_color,delay_ms):
    for i in range(0, n_times):
        pycom.rgbled(hex_color) # Dark Green - Connected to WLAN
        time.sleep_ms(delay_ms)
        pycom.rgbled(0x0) # LED OFF
        time.sleep_ms(delay_ms)
    return

def sub_cb(topic, msg):
    global actualRGB
    global switchRGB
    ch = MQTT_getTopicChannel(topic)
    value = MQTT_getMsgValue(msg)
    #print('Channel: ', ch, 'Value: ', value)

    #Updates the RGB Values
    if(ch==RGB_RED_CH):
        actualRGB[0] = hex(int(value))
        formatRgbValues(0)
    elif(ch==RGB_GREEN_CH):
        actualRGB[1] = hex(int(value))
        formatRgbValues(1)
    elif(ch==RGB_BLUE_CH):
        actualRGB[2] = hex(int(value))
        formatRgbValues(2)
    #Virtual Switch Pressed
    elif(ch==RGB_SWITCH_CH):
        switchRGB = value
        client.publish(topic=TOPIC_PUBLISH+RGB_SWITCH_CH, msg=value)

    print('RGB Value: ', actualRGB[0]+actualRGB[1]+actualRGB[2], 'SWITCH: ', switchRGB)


#Formats the received value
def formatRgbValues(index):
    global actualRGB
    if(index<-1 or index>len(actualRGB)):
        return -1

    #Formats All
    if(index==-1):
        for i in range(0, 3):
            aux = str(actualRGB[i]).split('x')
            actualRGB[i] = aux[len(aux)-1]
            if(len(actualRGB[i])==1):
                actualRGB[i]='0'+actualRGB[i]

    #Formats a Specific Index
    else:
        aux = str(actualRGB[index]).split('x')
        actualRGB[index] = aux[len(aux)-1]
        if(len(actualRGB[index])==1):
            actualRGB[index]='0'+actualRGB[index]

    return

def MQTT_getTopicChannel(topic):
    topic = str(topic)
    topic_split = topic.split('/')
    return (topic_split[len(topic_split)-1].replace('\'',''))

def MQTT_getMsgValue(msg):
    msg = str(msg)
    msg_split = msg.split(',')
    return (msg_split[len(msg_split)-1].replace('\'',''))

def MQTT_subscribeAndSetInitState():
    #Initial Subscribe to Actuators Widgets
    client.subscribe(TOPIC_SUBSCRIBE+RGB_SWITCH_CH)
    client.subscribe(TOPIC_SUBSCRIBE+RGB_RED_CH)
    client.subscribe(TOPIC_SUBSCRIBE+RGB_GREEN_CH)
    client.subscribe(TOPIC_SUBSCRIBE+RGB_BLUE_CH)

    #Initial Publish to Actuators Widgets to Set Initial Value
    client.publish(topic=TOPIC_PUBLISH+RGB_SWITCH_CH, msg='0')
    client.publish(topic=TOPIC_PUBLISH+RGB_RED_CH, msg='0')
    client.publish(topic=TOPIC_PUBLISH+RGB_GREEN_CH, msg='0')
    client.publish(topic=TOPIC_PUBLISH+RGB_BLUE_CH, msg='0')

    #LED flash Dark Blue to notify user that MQTT connection has succefull
    RgbLedFlash(5,0x000055,50)

#NETWORK connection
pycom.heartbeat(False)
pycom.rgbled(0x550000) # Dark Red - Not Connected to WLAN

wlan = WLAN(mode=WLAN.STA)
wlan.connect(WIFI_NAME, auth=(WLAN.WPA2, WIFI_PW), timeout=5000)
while not wlan.isconnected():
    pycom.rgbled(0x550000) # Dark Red - Not Connected to WLAN
    machine.idle() # save power while waiting

#LED flash Dark Green to notify user that WLAN connection has succefull
RgbLedFlash(5,0x005500,50)

#MQTT Connection Client
client = MQTTClient(MQTT_CLIENT_ID, MQTT_PROVIDER, user=MQTT_USERNAME, password=MQTT_PW , port=MQTT_PORT)

client.set_callback(sub_cb)
time.sleep_ms(200)
client.connect()

MQTT_subscribeAndSetInitState()

#Pysense Button Configuration
def IsrCallback(p):
    global switchRGB
    print('External Interrupt: ', p)

    if(p.id()==BTN_INT_PIN):
        if(switchRGB=='1'):
            switchRGB='0'
            client.publish(topic=TOPIC_PUBLISH+RGB_SWITCH_CH, msg=switchRGB)
        else:
            switchRGB='1'
            client.publish(topic=TOPIC_PUBLISH+RGB_SWITCH_CH, msg=switchRGB)
    return

btn = machine.Pin(BTN_INT_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
btn.callback(trigger=machine.Pin.IRQ_RISING , handler=IsrCallback)

#Init
py = Pysense()
si = SI7006A20(py)
li = LIS2HH12(py)
lt = LTR329ALS01(py)
mpp = MPL3115A2(py,mode=PRESSURE)

#Main Cycle
while 1:
    client.check_msg() #Checks if there is data to receive

    #Temperature Publish
    client.publish(topic=TOPIC_PUBLISH+TEMP_CH, msg="temp,c="+str(si.temperature()))

    time.sleep_ms(10) #Limpar barramento I2C
    #Humidity Publish
    client.publish(topic=TOPIC_PUBLISH+HUMI_CH, msg="rel_hum,p="+str(si.humidity()))

    time.sleep_ms(10) #Limpar barramento I2C
    #Accelerometer Publish
    x,y,z = li.acceleration()
    client.publish(topic=TOPIC_PUBLISH+ACCEL_X_CH, msg="analog_sensor="+str(x))
    client.publish(topic=TOPIC_PUBLISH+ACCEL_Y_CH, msg="analog_sensor="+str(y))
    client.publish(topic=TOPIC_PUBLISH+ACCEL_Z_CH, msg="analog_sensor="+str(z))

    time.sleep_ms(10) #Limpar barramento I2C
    #Light Publish - Different Channels = Different sensitivity for wavelenght (ch0 ~450nm violet-blue and ch1 ~770nm red)
    lux_ch0, lux_ch1 = lt.light()
    client.publish(topic=TOPIC_PUBLISH+LIGHT0_CH, msg="lum,lux="+str(lux_ch0))
    client.publish(topic=TOPIC_PUBLISH+LIGHT1_CH, msg="lum,lux="+str(lux_ch1))

    time.sleep_ms(10) #Limpar barramento I2C
    #Altitude and Pressure
    press = mpp.pressure()
    client.publish(topic=TOPIC_PUBLISH+PRESS_CH, msg="bp,pa="+str(press))
    alt = 44330.77*(1-((press/101326)**0.1902632))+REGION_ALT_OFFSET
    client.publish(topic=TOPIC_PUBLISH+ALTI_CH, msg="analog_sensor,m="+str(alt))

    time.sleep_ms(10) #Limpar barramento I2C
    #Battery
    client.publish(topic=TOPIC_PUBLISH+BATTERY_CH, msg="analog_sensor,v="+str(py.read_battery_voltage()))

    if(switchRGB=='1'):
        pycom.rgbled(int((actualRGB[0]+actualRGB[1]+actualRGB[2]), 16))

    else: #LED Flash to each time a complete write on MQTT has done if RGB LED switch is OFF
        RgbLedFlash(1,0x005555,50)
