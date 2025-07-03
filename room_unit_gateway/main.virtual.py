#!/usr/bin/env python

import time
import sys
import logging
import os
import threading

logger = logging.getLogger(__name__)

import config_reader
from networking.networking_domain import GatewayNetwork
import help_methods

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
    help_methods.execution_cycle(sensors, actuators, gw, None, 240)
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