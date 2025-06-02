#!/usr/bin/env python
#
# GrovePi Example for using the Grove LED for LED Fade effect (http://www.seeedstudio.com/wiki/Grove_-_LED_Socket_Kit)
#
# The GrovePi connects the Raspberry Pi and Grove sensors.  You can learn more about GrovePi here:  http://www.dexterindustries.com/GrovePi


import time
import sys
from typing import List
import grovepi
import numpy as np

import config_reader
from networking.networking_domain import GatewayNetwork
from sensors.sensor import SensorInterface
from actuators.actuator import ActuatorInterface
from enumdef import Connectortype

def system_info():
    print (sys.version)
    print (sys.version_info)
    print ("grovepi version: " + str(grovepi.version()))
    print ("numpy version:" + str(np.version.version))

def read_all_sensors(sensors: List[SensorInterface]):
    for sensor in sensors:
        _ = sensor.read_sensor()

def write_all_actuators(actuators: List[ActuatorInterface], value: int):
    for actuator in actuators:
        actuator.write_actuator(value)

def write_all_displays(displays: List[ActuatorInterface], text: str):
    for display in displays:
        if display.connector_types != Connectortype.I2C_display:
            continue
        display.write_actuator(text)

def send_sensors(sensors: List[SensorInterface], network_connection: GatewayNetwork):
    for sensor in sensors:
        print ("--", flush=True)
        network_connection.send_all_data_sensor(sensor,True)

def send_actuators(actuators: List[ActuatorInterface], network_connection: GatewayNetwork):
    for actuator in actuators:
        print ("--", flush=True)
        network_connection.send_all_data_actuator(actuator)

def cyclic_read(sensors: List[SensorInterface], displays: List[ActuatorInterface], cycle: int, network_connection: GatewayNetwork):
    for sensor in sensors:
        if cycle % sensor.read_interval== 0:
            old_value = sensor.last_value
            read_dict = sensor.read_sensor()
            if abs(old_value - sensor.last_value) >= sensor.notify_change_precision:
                network_connection.send_all_data_sensor(sensor,True)
            text = "{}: {}".format(sensor.name,str(read_dict["last_value"]))
            write_all_displays(displays, text)

def execution_cycle(sensors: List[SensorInterface],actuators: List[ActuatorInterface], network_connection: GatewayNetwork):
    print ("", flush=True)
    #send_sensors(sensors,network_connection)
    #send_actuators(actuators,network_connection)
    cycle = 0
    max_cycle_time = 240
    want_to_exit = False
    while not want_to_exit:
        print ("", flush=True)
        try:

            read_all_sensors(sensors)
            #write_all_actuators(actuators, cycle % 2)
            #write_all_displays(actuators,"12345678910131517192123252729313335")
            #cyclic_read(sensors,actuators,cycle,network_connection)

            # Reset
            if cycle > max_cycle_time:
                cycle = 0
                #send_sensors(sensors,network_connection)
                #send_actuators(actuators,network_connection)

            # Increment
            cycle = cycle + 1
            want_to_exit = True
            time.sleep(1)

        except KeyboardInterrupt:
            want_to_exit = True
            break
        except (IOError,TypeError) as e:
            print ("Error")
            print (e)
            want_to_exit = True

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
    gateway_network = None
    try:
        config_values = config_reader.read_config(config_file_name)
        sensors = config_values['sensor_class_list']
        actuators = config_values['actuator_class_list']
    except Exception as e:
        print ("Reading config file {} was not succesfull {}".format(config_file_name,config_values))
        print (e, flush=True)

    try:
        gateway_network = GatewayNetwork(host=config_values['mqtt_host'],port=config_values['mqtt_port'],username=config_values['mqtt_username'],password=password,floor_id=config_values['floor_id'],max_rooms_per_floor=config_values['max_rooms_per_floor'],room_id=config_values['room_id'])
    except Exception as e:
        print ("MQTT broker not connected.")
        print (e, flush=True)

    execution_cycle(sensors,actuators,gateway_network)

    for sensor in sensors:
        del sensor
    for actuator in actuators:
        del actuator


# __name__
if __name__=="__main__":
    main()
