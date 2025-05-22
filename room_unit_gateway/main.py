#!/usr/bin/env python
#
# GrovePi Example for using the Grove LED for LED Fade effect (http://www.seeedstudio.com/wiki/Grove_-_LED_Socket_Kit)
#
# The GrovePi connects the Raspberry Pi and Grove sensors.  You can learn more about GrovePi here:  http://www.dexterindustries.com/GrovePi


import time
import sys

import config_reader
from networking import MQTTendpoint
from sensor import Sensor
from actuator import Actuator
from display import Display

time.sleep(1)
i = 0
togle = 0

if len(sys.argv) != 2:
    print ("Error CLI arguments incorrect")

config_file_name = str(sys.argv[1])
password = str(sys.argv[2])
try:
    config_values = config_reader.read_config(config_file_name)
except:
    Print ("Reading config file {} was not succesfull")
network_connection = MQTTendpoint(host=config_values['rabitMQ_host'],port=config_values['rabitMQ_port'],username=config_values['rabitMQ_username'],password=password)

sensors = config_values['sensor_class_list']
actuators = config_values['actuator_class_list']
displays = config_values['display_class_list']

while True:
    try:
        # READ sensors
        for sensor in sensors:
            _ = sensor.read_sensor()

        for actuator in actuators:
            actuator.write_actuator(i)

        for display in displays:
            display.write_display("Test")

        # Reset
        if i > 250:
            i = 0

        if togle == 1:
            togle = 0
        elif togle == 0:
            togle = 1

        # Increment brightness for next iteration
        i = i + 1
        time.sleep(1)

        network_connection.send()

    except KeyboardInterrupt:
        # TODO delete all sensors, actuators and displays
        break
    except (IOError,TypeError):
        print ("Error")
