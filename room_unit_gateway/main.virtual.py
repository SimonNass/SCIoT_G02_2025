#!/usr/bin/env python

import time
import sys
from typing import List
import numpy as np
import logging
import os
import threading

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

def execution_cycle(sensors: List[SensorInterface],actuators: List[ActuatorInterface], network_connection: GatewayNetwork):
    print ("", flush=True)
    help_methods.send_sensors(sensors,network_connection)
    help_methods.send_actuators(actuators,network_connection)
    cycle = 0
    max_cycle_time = 240
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

def run_gateway_for_config(config_file: str, password: str):
    """
    Thread target: read one INI, build sensor/actuator lists,
    create a GatewayNetwork, and run execution_cycle().
    """
    try:
        config_values = config_reader.read_config(config_file)
    except Exception as e:
        print(f"[{config_file}] Failed to read config: {e}", file=sys.stderr)
        return

    sensors   = config_values['sensor_class_list']
    actuators = config_values['actuator_class_list']
    mqtt_host     = config_values['mqtt_host']
    mqtt_port     = config_values['mqtt_port']
    mqtt_username = config_values['mqtt_username']
    floor_id      = config_values['floor_id']
    max_rooms     = config_values['max_rooms_per_floor']
    room_id       = config_values['room_id']

    try:
        gw = GatewayNetwork(
            host=mqtt_host,
            port=mqtt_port,
            username=mqtt_username,
            password=password,
            floor_id=floor_id,
            max_rooms_per_floor=max_rooms,
            room_id=room_id,
            actuators=[]
        )
    except Exception as e:
        print(f"[{config_file}] MQTT connection failed: {e}", file=sys.stderr)
        return

    logger.info(f"[{config_file}] Starting execution cycle for floor {floor_id}, room {room_id}")
    execution_cycle(sensors, actuators, gw)
    logger.info(f"[{config_file}] Execution cycle ended.")


def main():
    """
    Usage:
      python main.py <config_folder> <mqtt_password>
    It will scan <config_folder> for all “*.ini” files and spawn one thread per file.
    """
    logging.basicConfig(filename='pi_room_gateway.log', level=logging.INFO)

    if len(sys.argv) != 3:
        print("Usage: python main.py <config_folder> <mqtt_password>")
        sys.exit(1)

    config_folder, password = sys.argv[1], sys.argv[2]

    if not os.path.isdir(config_folder):
        print(f"Error: '{config_folder}' is not a directory or does not exist.", file=sys.stderr)
        sys.exit(1)

    # Find all .ini files in the folder (non‐recursive)
    ini_files = [
        os.path.join(config_folder, f)
        for f in os.listdir(config_folder)
        if f.lower().endswith(".ini")
    ]

    if not ini_files:
        print(f"No .ini files found in '{config_folder}'.", file=sys.stderr)
        sys.exit(1)

    threads = []
    for cfg in ini_files:
        t = threading.Thread(
            target=run_gateway_for_config,
            args=(cfg, password),
            daemon=True
        )
        t.start()
        threads.append(t)

    try:
        # Keep main thread alive while child threads run indefinitely
        while any(t.is_alive() for t in threads):
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down all gateway threads...")

if __name__ == "__main__":
    main()