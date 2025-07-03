#!/usr/bin/env python

import sys
import numpy as np
import logging
logger = logging.getLogger(__name__)

import config_reader
from networking.networking_domain import GatewayNetwork
from virtual_environment import Virtual_environment
import help_methods

def main():
    """
    Usage:
      python main.py <config_folder>/<config_file.ini> <mqtt_password>
    """

    logging.basicConfig(filename='pi_room_gateway.log', level=logging.INFO)
    logger.info("xxxx Started new execution.")
    help_methods.system_info()

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
    help_methods.execution_cycle(sensors,actuators,gateway_network, virtual_environment, max_cycle_time)
    logger.info("Execution cycle ended.")

    del ardoino_serial
    for sensor in sensors:
        del sensor
    for actuator in actuators:
        del actuator


# __name__
if __name__=="__main__":
    main()
