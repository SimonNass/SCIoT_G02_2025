#!/usr/bin/env python
#
# GrovePi Example for using the Grove LED for LED Fade effect (http://www.seeedstudio.com/wiki/Grove_-_LED_Socket_Kit)
#
# The GrovePi connects the Raspberry Pi and Grove sensors.  You can learn more about GrovePi here:  http://www.dexterindustries.com/GrovePi


import time
import grovepi
from grovepi import *

# Connected actuators
led1 = 5 #LED blue at D5 fade
led2 = 4 #LED red at D4 on/off
led3 = 2 #LED green at D2 on/off
# Connected sensors
dht_sensor = 7 #Temperature and humidity at D7

grovepi.pinMode(led1,"OUTPUT")
grovepi.pinMode(led2,"OUTPUT")
grovepi.pinMode(led3,"OUTPUT")


time.sleep(1)
i = 0
togle = 0
while True:
    try:
        # READ sensors
        [temperature,humidity] = dht(dht_sensor,0)
        print ("--")
        print ("Temperature: {}".format(temperature))
        print ("Humidity: {}".format(humidity))
        print ("--")
        # Reset
        if i > 255:
            i = 0

        if togle == 1:
            togle = 0
        elif togle == 0:
            togle = 1

        # Current brightness
        print ("LED dim: {}".format(i))
        print ("LED togle: {}".format(togle))

        # Give PWM output to LED
        grovepi.analogWrite(led1,i)
        grovepi.digitalWrite(led2,togle)
        grovepi.digitalWrite(led3,togle)

        # Increment brightness for next iteration
        i = i + 20
        time.sleep(1)

    except KeyboardInterrupt:
        grovepi.analogWrite(led1,0)
        grovepi.digitalWrite(led2,0)
        grovepi.digitalWrite(led3,0)
        break
    except IOError:
        print ("Error")
