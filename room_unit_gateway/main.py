#!/usr/bin/env python
#
# GrovePi Example for using the Grove LED for LED Fade effect (http://www.seeedstudio.com/wiki/Grove_-_LED_Socket_Kit)
#
# The GrovePi connects the Raspberry Pi and Grove sensors.  You can learn more about GrovePi here:  http://www.dexterindustries.com/GrovePi


import config_reader
import time
import pika
import grovepi
from grovepi import *
from grove_rgb_lcd import *


config_values = config_reader.read_config('config.ini')

# Connected actuators
led1 = 3 # LED blue at D5 fade
led2 = 6 # LED red at D4 on/off
led3 = 5 # LED green at D2 on/off

# Connected sensors
dht_sensor = 7 # Temperature and humidity at D7
light_sensor = 1 # light sensor at A1
sound_sensor = 0 # sound level sensor at A0
rotation_sensor = 2 # rotation sensor / potentiometer at A2 
button_sensor = 4 # button at D4
motion_sensor = 8 # motion sensor at D8

grovepi.pinMode(led1,"OUTPUT")
grovepi.pinMode(led2,"OUTPUT")
grovepi.pinMode(led3,"OUTPUT")

grovepi.pinMode(button_sensor,"INPUT")
grovepi.pinMode(motion_sensor,"INPUT")

time.sleep(1)
i = 0
togle = 0

ip = '127.0.0.1'
port = 5672
user = ''
password = ''
if len(sys.argv) == 5:
    ip = sys.argv[1]
    port = sys.argv[2]
    print ("Selected IP {} and Port {}".format(ip,port))
    user = sys.argv[3]
    password = sys.argv[4]
    print ("RabbitMQ user {} with passwordlength {}".format(user,len(password)))


credentials = pika.PlainCredentials(user,password)
connection = pika.BlockingConnection(pika.ConnectionParameters(ip,port,'/',credentials))
channel = connection.channel()

channel.exchange_declare(exchange='sciot.topic',exchange_type='topic',durable=True,auto_delete=False)


while True:
    try:
        # READ sensors
        [temperature,humidity] = dht(dht_sensor,0)
        #print ("--")
        #print ("Temperature: {}".format(temperature))
        #print ("Humidity: {}".format(humidity))

        print ("--")
        light = grovepi.analogRead(light_sensor)
        sound = grovepi.analogRead(sound_sensor)
        rotation = grovepi.analogRead(rotation_sensor)
        #print ("Light level: {}".format(light))
        #print ("Sound level: {}".format(sound))
        #print ("Rotation angle: {}".format(rotation))

        button_state = grovepi.digitalRead(button_sensor)
        if button_state:
            print ("Button pressed")
        else:
            print ("Button not pressed")
        motion = grovepi.digitalRead(motion_sensor)
        if motion:
            print ("Motion Detected")
        else:
            print ("No motion")

        # Room Display
        grovepi.setRGB(0,128,64)
        #setRGB(0,255,0)
        grovepi.setText("Test Temperaturt:{}".format(temperature))

        # Reset
        if i > 255:
            i = 0

        if togle == 1:
            togle = 0
        elif togle == 0:
            togle = 1

        # Current brightness
        #print ("LED dim: {}".format(i))
        #print ("LED togle: {}".format(togle))

        # Give PWM output to LED
        #grovepi.analogWrite(led1,i)
        #grovepi.digitalWrite(led2,i)
        #grovepi.digitalWrite(led3,i)

        # Increment brightness for next iteration
        i = i + 20
        time.sleep(.2)

        channel.basic_publish(exchange='sciot.topic',routing_key='u38.0.353.window.t.12345',body='Hello World')

    except KeyboardInterrupt:
        grovepi.analogWrite(led1,0)
        grovepi.digitalWrite(led2,0)
        grovepi.digitalWrite(led3,0)
        grovepi.setRGB(0,0,0)
        grovepi.setText("")
        break
    except (IOError,TypeError):
        print ("Error")
