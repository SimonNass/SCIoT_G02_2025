"""Module has al high level methodes to manage the gateway.
In this file is the execution_cycle methode that runns indefinetely."""

import sys
import time
from typing import List
import logging
import numpy as np
try:
    import grovepi
except ImportError:
    grovepi = None
import config_reader
from networking.networking_domain import GatewayNetwork
from sensors.sensor import SensorInterface
from actuators.actuator import ActuatorInterface
from enumdef import Connectortype
from virtual_environment import Virtual_environment
from room_info import Room_Info
logger = logging.getLogger(__name__)

def read_all_sensors(sensors: List[SensorInterface]):
    for sensor in sensors:
        _ = sensor.read_sensor()

def read_all_actuators(actuators: List[ActuatorInterface]):
    for actuator in actuators:
        print (f'{actuator.general_iot_device.name} has value {actuator.last_value}', flush=True)

def write_all_actuators(actuators: List[ActuatorInterface], value: int):
    for actuator in actuators:
        actuator.write_actuator(value)

def write_all_displays(displays: List[ActuatorInterface], text: str):
    for display in displays:
        if display.general_iot_device.connector_type != Connectortype.I2C_display:
            continue
        display.write_actuator(text)

def send_sensors(sensors: List[SensorInterface], network_connection: GatewayNetwork):
    try:
        for sensor in sensors:
            network_connection.send_all_data_sensor(sensor,True)
    except Exception as e:
        logger.warning(f"send_sensors failed {e}")

def send_actuators(actuators: List[ActuatorInterface], network_connection: GatewayNetwork):
    try:
        for actuator in actuators:
            network_connection.send_all_data_actuator(actuator)
    except Exception as e:
        logger.warning(f"send_actuators failed {e}")

def send_actuator_sensor_mapping(virtual_environment: Virtual_environment, network_connection: GatewayNetwork):
    try:
        network_connection.send_actuator_sensor_mapping(virtual_environment.__dict__())
    except Exception as e:
        logger.error(f"virtual_environment not sending data. {e}")


def cyclic_read(sensors: List[SensorInterface], displays: List[ActuatorInterface], cycle: int, network_connection: GatewayNetwork):
    for sensor in sensors:
        if cycle % sensor.read_interval== 0:
            old_value = sensor.last_value
            read_dict = sensor.read_sensor()
            if abs(old_value - sensor.last_value) >= sensor.notify_change_precision:
                try:
                    network_connection.send_all_data_sensor(sensor,True)
                except Exception as e:
                    logger.warning(f"cyclic_read failed {str(sensor.general_iot_device.id)} {sensor.general_iot_device.name} {e}")
            text = f"{sensor.general_iot_device.name}: {str(read_dict['last_value'])}"
            write_all_displays(displays, text)

def cyclic_actuator_read(actuators: List[ActuatorInterface], network_connection: GatewayNetwork):
    for actuator in actuators:
        if actuator.value_has_changed:
            try:
                network_connection.send_all_data_actuator(actuator)
                actuator.value_has_changed = False
            except Exception as e:
                logger.warning(f"cyclic_actuator_read failed {str(actuator.general_iot_device.id)} {actuator.general_iot_device.name} {e}")

def execution_cycle(sensors: List[SensorInterface],actuators: List[ActuatorInterface], network_connection: GatewayNetwork, virtual_environment: Virtual_environment, max_cycle_time: int = 100, sleeping_time: int = 1):
    logger.info("max_cycle_time: " + str(max_cycle_time))
    logger.info(f"sleeping_time: {str(sleeping_time)} seconds")
    print ("", flush=True)
    network_connection.send_delete_ald_IoT()
    time.sleep(1)
    send_sensors(sensors,network_connection)
    send_actuators(actuators,network_connection)
    send_actuator_sensor_mapping(virtual_environment,network_connection)
    cycle = 0
    want_to_exit = False
    while not want_to_exit:
        print ("", flush=True)
        try:

            #read_all_sensors(sensors)
            #write_all_actuators(actuators, cycle % 2)
            #write_all_displays(actuators,"12345678910131517192123252729313335")
            #read_all_actuators(actuators)
            cyclic_read(sensors,actuators,cycle,network_connection)
            cyclic_actuator_read(actuators, network_connection)

            # Reset
            if cycle > max_cycle_time:
                cycle = 0
                send_sensors(sensors,network_connection)
                send_actuators(actuators,network_connection)
                send_actuator_sensor_mapping(virtual_environment,network_connection)

            # Increment
            try:
                virtual_environment.performe_environment_step()
            except Exception as e:
                logger.error(f"virtual_environment not ececuting step. {e}")
            cycle = cycle + 1
            #want_to_exit = True
            time.sleep(sleeping_time)

        except KeyboardInterrupt:
            want_to_exit = True
            break
        except (IOError,TypeError) as e:
            print ("Error")
            #print (e)
            logger.error(e)
            want_to_exit = True

def system_info():
    print (sys.version)
    #print (sys.version_info)
    logger.info(sys.version)
    logger.info(sys.version_info)
    try:
        #print ("grovepi version: " + str(grovepi.version()))
        logger.info(f"grovepi version: {str(grovepi.version())}")
    except AttributeError:
        pass
    #print ("numpy version:" + str(np.version.version))
    logger.info(f"numpy version: {str(np.version.version)}")

def run_gateway_for_config(config_file_name: str, password: str, host: str=None):
    config_values = {}
    try:
        config_values = config_reader.read_config(config_file_name, password, host)
    except Exception as e:
        print (f"Reading config file {config_file_name} was not succesfull {config_values}")
        print (e, flush=True)
        logger.error(f"Reading config file {config_file_name} was not succesfull {config_values}, {e}")

    max_cycle_time = 100
    sleeping_time = 1
    sensors = []
    actuators = []
    gateway_network = None
    room_info = None
    ardoino_serial = None
    virtual_environment = None
    try:
        max_cycle_time: int = int(config_values['max_cycle_time'])
        sleeping_time: int = int(config_values['sleeping_time'])
        sensors: List[SensorInterface] = config_values['sensor_class_list']
        actuators: List[ActuatorInterface] = config_values['actuator_class_list']
        room_info: Room_Info = config_values['room_info']
        ardoino_serial = config_values['ardoino_serial']
        virtual_environment: Virtual_environment = config_values['virtual_environment']
        gateway_network: GatewayNetwork = config_values['gateway_network']
    except Exception as e:
        print (f"Reading config_values {config_file_name} was not succesfull {config_values}")
        print (e, flush=True)
        logger.error(f"Reading config_values {config_file_name} was not succesfull {config_values}, {e}")

    logger.info(f"Starting execution cycle for floor {room_info.floor_id}, room {room_info.room_id}")
    execution_cycle(sensors,actuators,gateway_network, virtual_environment, max_cycle_time, sleeping_time)
    logger.info("Execution cycle ended.")

    del ardoino_serial
    for sensor in sensors:
        del sensor
    for actuator in actuators:
        del actuator
