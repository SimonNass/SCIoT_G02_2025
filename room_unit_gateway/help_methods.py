import sys
import time
import numpy as np
from typing import List
import logging
logger = logging.getLogger(__name__)
try:
    import grovepi
except ImportError:
    grovepi = None

from networking.networking_domain import GatewayNetwork
from sensors.sensor import SensorInterface
from actuators.actuator import ActuatorInterface
from enumdef import Connectortype
from virtual_environment import Virtual_environment

def read_all_sensors(sensors: List[SensorInterface]):
    for sensor in sensors:
        _ = sensor.read_sensor()

def read_all_actuators(actuators: List[ActuatorInterface]):
    for actuator in actuators:
        print (f'{actuator.name} has value {actuator.last_value}', flush=True)

def write_all_actuators(actuators: List[ActuatorInterface], value: int):
    for actuator in actuators:
        actuator.write_actuator(value)

def write_all_displays(displays: List[ActuatorInterface], text: str):
    for display in displays:
        if display.connector_type != Connectortype.I2C_display:
            continue
        display.write_actuator(text)

def send_sensors(sensors: List[SensorInterface], network_connection: GatewayNetwork):
    for sensor in sensors:
        network_connection.send_all_data_sensor(sensor,True)

def send_actuators(actuators: List[ActuatorInterface], network_connection: GatewayNetwork):
    for actuator in actuators:
        network_connection.send_all_data_actuator(actuator)

def cyclic_read(sensors: List[SensorInterface], displays: List[ActuatorInterface], cycle: int, network_connection: GatewayNetwork):
    for sensor in sensors:
        if cycle % sensor.read_interval== 0:
            old_value = sensor.last_value
            read_dict = sensor.read_sensor()
            if abs(old_value - sensor.last_value) >= sensor.notify_change_precision:
                network_connection.send_all_data_sensor(sensor,True)
            text = f"{sensor.name}: {str(read_dict['last_value'])}"
            write_all_displays(displays, text)

def execution_cycle(sensors: List[SensorInterface],actuators: List[ActuatorInterface], network_connection: GatewayNetwork, virtual_environment: Virtual_environment, max_cycle_time: int = 100):
    logger.info("max_cycle_time: " + str(max_cycle_time))
    print ("", flush=True)
    send_sensors(sensors,network_connection)
    send_actuators(actuators,network_connection)
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

            # Reset
            if cycle > max_cycle_time:
                cycle = 0
                send_sensors(sensors,network_connection)
                send_actuators(actuators,network_connection)

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
