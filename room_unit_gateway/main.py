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
from virtual_environment import Virtual_environment
from sensors.sensor import SensorInterface
from actuators.actuator import ActuatorInterface
from enumdef import Connectortype
from networking.discovery import find_mqtt_broker_ip
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

def execution_cycle(sensors: List[SensorInterface],actuators: List[ActuatorInterface], network_connection: GatewayNetwork, virtual_environment: Virtual_environment, max_cycle_time: int = 100):
    logger.info("max_cycle_time: " + str(max_cycle_time))
    print ("", flush=True)
    help_methods.send_sensors(sensors,network_connection)
    help_methods.send_actuators(actuators,network_connection)
    cycle = 0
    want_to_exit = False
    while not want_to_exit:
        print ("", flush=True)
        try:

            #help_methods.read_all_sensors(sensors)
            #help_methods.write_all_actuators(actuators, cycle % 2)
            #help_methods.write_all_displays(actuators,"12345678910131517192123252729313335")
            #help_methods.read_all_actuators(actuators)
            help_methods.cyclic_read(sensors,actuators,cycle,network_connection)

            # Reset
            if cycle > max_cycle_time:
                cycle = 0
                help_methods.send_sensors(sensors,network_connection)
                help_methods.send_actuators(actuators,network_connection)

            # Increment
            virtual_environment.performe_environment_step()
            cycle = cycle + 1
            #want_to_exit = True
            time.sleep(1)

        except KeyboardInterrupt:
            want_to_exit = True
            break
        except (IOError,TypeError) as e:
            print ("Error")
            #print (e)
            logger.error(e)
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
        logger.warning(f"Error CLI arguments incorrect {sys.argv}")
        sys.exit(1)

    config_file_name = str(sys.argv[1])
    password = str(sys.argv[2])

    print ("", flush=True)

    config_values = {}
    try:
        config_values = config_reader.read_config(config_file_name)
    except Exception as e:
        print (f"Reading config file {config_file_name} was not succesfull {config_values}")
        print (e, flush=True)
        logger.error(f"Reading config file {config_file_name} was not succesfull {config_values}, {e}")

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
    virtual_enfironment_list = []
    try:
        max_cycle_time   = int(config_values['max_cycle_time'])
        sensors   = config_values['sensor_class_list']
        actuators = config_values['actuator_class_list']
        mqtt_host     = str(config_values['mqtt_host'])
        mqtt_port     = int(config_values['mqtt_port'])
        mqtt_username = str(config_values['mqtt_username'])
        floor_id      = int(config_values['floor_id'])
        max_rooms     = int(config_values['max_rooms_per_floor'])
        room_id       = int(config_values['room_id'])
        ardoino_serial = str(config_values['ardoino_serial'])
        virtual_enfironment_list = config_values['virtual_enfironment_list']
    except Exception as e:
        print (f"Reading config_values {config_file_name} was not succesfull {config_values}")
        print (e, flush=True)
        logger.error(f"Reading config_values {config_file_name} was not succesfull {config_values}, {e}")

    gateway_network = None
    try:
        gateway_network = GatewayNetwork(
            host=mqtt_host,
            port=mqtt_port,
            username=mqtt_username,
            password=password,
            floor_id=floor_id,
            max_rooms_per_floor=max_rooms,
            room_id=room_id,
            actuators=actuators
        )
    except Exception as e:
        print ("MQTT broker not connected.")
        print (e, flush=True)
        logger.error(f"MQTT broker not connected. {e}")
    
    virtual_environment = None
    try:
        virtual_environment = Virtual_environment(
            sensors=sensors,
            actuators=actuators,
            mapping=virtual_enfironment_list
        )
    except Exception as e:
        print ("virtual_environment not initialised.")
        print (e, flush=True)
        logger.error(f"virtual_environment not initialised. {e}")

    logger.info(f"Starting execution cycle for floor {floor_id}, room {room_id}")
    execution_cycle(sensors,actuators,gateway_network, virtual_environment, max_cycle_time)
    logger.info("Execution cycle ended.")

    del ardoino_serial
    for sensor in sensors:
        del sensor
    for actuator in actuators:
        del actuator


# __name__
if __name__=="__main__":
    main()
