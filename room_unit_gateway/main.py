#!/usr/bin/env python
#
# GrovePi Example for using the Grove LED for LED Fade effect (http://www.seeedstudio.com/wiki/Grove_-_LED_Socket_Kit)
#
# The GrovePi connects the Raspberry Pi and Grove sensors.  You can learn more about GrovePi here:  http://www.dexterindustries.com/GrovePi


import time
import sys
from typing import List
import json

import config_reader
from networking import MQTTendpoint
from sensors.sensor import SensorInterface
from actuators.actuator import Actuator
from actuators.display import Display

def system_info():
    print (sys.version)
    print (sys.version_info)

def read_all_sensors(sensors: List[SensorInterface]):
    for sensor in sensors:
        _ = sensor.read_sensor()

def write_all_actuators(actuators: List[Actuator], value: int):
    for actuator in actuators:
        actuator.write_actuator(value)

def write_all_displays(displays: List[Display], text: str):
    for display in displays:
        display.write_display(text)

def cyclic_read(sensors: List[SensorInterface], displays: List[Display], cycle: int):
    for sensor in sensors:
        if cycle % sensor.read_interval== 0:
            sensor_value = sensor.read_sensor()
            text = "{}: {}".format(sensor.name,str(sensor_value))
            write_all_displays(displays, text)

def send_head(sensors: List[SensorInterface],actuators: List[Actuator],displays: List[Display], network_connection: MQTTendpoint): # TODO
    s_list = [s.__dict__ for s in sensors]
    a_list = [a.__dict__ for a in actuators]
    d_list = [d.__dict__ for d in displays]
    print (s_list)
    #text = json.dumps({"sensors": s_list, "actuators":a_list, "displays": d_list})
    text = json.dumps(s_list)
    print (text)
    #network_connection.send('iot/1/1/sensor','u38.0.353.window.t.12345',text)

def execution_cycle(sensors: List[SensorInterface],actuators: List[Actuator],displays: List[Display], network_connection: MQTTendpoint):
    i = 0
    want_to_exit = False
    while not want_to_exit:
        print ("", flush=True)
        try:

            #read_all_sensors(sensors)
            #write_all_actuators(actuators, i % 2)
            #write_all_displays(displays,"12345678910131517192123252729313335")
            cyclic_read(sensors,displays,i)
            #network_connection.send('sciot.topic','u38.0.353.window.t.12345','Hello World')
            #send_head(sensors,actuators,displays,network_connection)

            # Reset
            if i > 240:
                i = 0
            # Increment
            i = i + 1
            #want_to_exit = True
            time.sleep(1)

        except KeyboardInterrupt:
            break
        except (IOError,TypeError) as e:
            print ("Error")
            print (e)

def main():
    system_info()

    if len(sys.argv) < 3 or len(sys.argv) > 3:
        print ("Error CLI arguments incorrect")
        print (sys.argv)

    config_file_name = str(sys.argv[1])
    password = str(sys.argv[2])

    print ("", flush=True)

    config_values = {}
    sensors = []
    actuators = []
    displays = []
    network_connection = None
    try:
        config_values = config_reader.read_config(config_file_name)
        sensors = config_values['sensor_class_list']
        actuators = config_values['actuator_class_list']
        displays = []#config_values['display_class_list']
    except Exception as e:
        print ("Reading config file {} was not succesfull {}".format(config_file_name,config_values))
        print (e, flush=True)

    try:
        topic_prefix = "iot/" + config_values['floor_id'] * config_values['max_rooms_per_floor'] + config_values['room_id'] + "/"
        network_connection = MQTTendpoint(host=config_values['mqtt_host'],port=config_values['mqtt_port'],username=config_values['mqtt_username'],password=password,topic_prefix=topic_prefix)
    except Exception as e:
        print ("MQTT broker not connected.")
        print (e, flush=True)

    execution_cycle(sensors,actuators,displays,network_connection)

    for sensor in sensors:
        del sensor
    for actuator in actuators:
        del actuator
    for display in displays:
        del display


# __name__
if __name__=="__main__":
    main()
