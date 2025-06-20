from typing import List
import logging
logger = logging.getLogger(__name__)

from networking.networking_domain import GatewayNetwork
from sensors.sensor import SensorInterface
from actuators.actuator import ActuatorInterface
from enumdef import Connectortype

def read_all_sensors(sensors: List[SensorInterface]):
    for sensor in sensors:
        _ = sensor.read_sensor()

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