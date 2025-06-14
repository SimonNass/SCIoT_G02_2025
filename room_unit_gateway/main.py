#!/usr/bin/env python

import time
import sys
from typing import List
import numpy as np
import logging
logger = logging.getLogger(__name__)

try:
    import grovepi
except ImportError:
    grovepi = None

import config_reader
from networking.networking_domain import GatewayNetwork
from sensors.sensor import SensorInterface
from actuators.actuator import ActuatorInterface
from enumdef import Connectortype
import help_methods

def system_info():
    print (sys.version)
    #print (sys.version_info)
    logger.info(sys.version)
    logger.info(sys.version_info)
    try:
        #print ("grovepi version: " + str(grovepi.version()))
        logger.info("grovepi version: " + str(grovepi.version()))
    except AttributeError:
        pass
    #print ("numpy version:" + str(np.version.version))
    logger.info("numpy version:" + str(np.version.version))

def execution_cycle(sensors: List[SensorInterface],actuators: List[ActuatorInterface], network_connection: GatewayNetwork, max_cycle_time: int = 100):
    logger.info("max_cycle_time: " + max_cycle_time)
    print ("", flush=True)
    help_methods.send_sensors(sensors,network_connection)
    help_methods.send_actuators(actuators,network_connection)
    cycle = 0
    want_to_exit = False
    while not want_to_exit:
        print ("", flush=True)
        try:

            help_methods.read_all_sensors(sensors)
            #help_methods.write_all_actuators(actuators, cycle % 2)
            #help_methods.write_all_displays(actuators,"12345678910131517192123252729313335")
            #help_methods.cyclic_read(sensors,actuators,cycle,network_connection)

            # Reset
            if cycle > max_cycle_time:
                cycle = 0
                help_methods.send_sensors(sensors,network_connection)
                help_methods.send_actuators(actuators,network_connection)

            # Increment
            cycle = cycle + 1
            #want_to_exit = True
            time.sleep(1)

        except KeyboardInterrupt:
            want_to_exit = True
            break
        except (IOError,TypeError) as e:
            print ("Error")
            #print (e)
            logger.info(e)
            want_to_exit = True

def main():
    """
    Usage:
      python main.py <config_folder>/<config_file.ini> <mqtt_password>
    """
    logging.basicConfig(filename='pi_room_gateway.log', level=logging.INFO)
    logger.info("xxxx Started new execution.")
    system_info()

    if len(sys.argv) < 3 or len(sys.argv) > 3:
        print ("Error CLI arguments incorrect")
        print("Usage: python main.py <config_folder>/<config_file.ini> <mqtt_password>")
        print (sys.argv)
        logger.info("Error CLI arguments incorrect {}".format(sys.argv))
        sys.exit(1)

    config_file_name = str(sys.argv[1])
    password = str(sys.argv[2])

    print ("", flush=True)

    config_values = {}
    try:
        config_values = config_reader.read_config(config_file_name)
    except Exception as e:
        print ("Reading config file {} was not succesfull {}".format(config_file_name,config_values))
        print (e, flush=True)
        logger.info("Reading config file {} was not succesfull {}, {}".format(config_file_name,config_values, e))

    max_cycle_time = 100
    sensors = []
    actuators = []
    mqtt_host = None
    mqtt_port = None
    mqtt_username = None
    floor_id = None
    max_rooms = None
    room_id = None
    ardoino_serial = None
    try:
        max_cycle_time   = config_values['max_cycle_time']
        sensors   = config_values['sensor_class_list']
        actuators = config_values['actuator_class_list']
        mqtt_host     = config_values['mqtt_host']
        mqtt_port     = config_values['mqtt_port']
        mqtt_username = config_values['mqtt_username']
        floor_id      = config_values['floor_id']
        max_rooms     = config_values['max_rooms_per_floor']
        room_id       = config_values['room_id']
        ardoino_serial = config_values['ardoino_serial']
    except Exception as e:
        print ("Reading config_values {} was not succesfull {}".format(config_file_name,config_values))
        print (e, flush=True)
        logger.info("Reading config_values {} was not succesfull {}, {}".format(config_file_name,config_values, e))

    gateway_network = None
    try:
        gateway_network = GatewayNetwork(
            host=mqtt_host,
            port=mqtt_port,
            username=mqtt_username,
            password=password,
            floor_id=floor_id,
            max_rooms_per_floor=max_rooms,
            room_id=room_id
        )
    except Exception as e:
        print ("MQTT broker not connected.")
        print (e, flush=True)
        logger.info("MQTT broker not connected. {}".format(e))

    logger.info(f"Starting execution cycle for floor {floor_id}, room {room_id}")
    execution_cycle(sensors,actuators,gateway_network, max_cycle_time)
    logger.info(f"Execution cycle ended.")

    del ardoino_serial
    for sensor in sensors:
        del sensor
    for actuator in actuators:
        del actuator


# __name__
if __name__=="__main__":
    main()
