"""Module executes the impact virtual actuators have on virtual sensors to emulate the physical environment for virtual IoT."""

from typing import List, Dict, Union
import uuid

from sensors.sensor import SensorInterface
from actuators.actuator import ActuatorInterface
import logging
logger = logging.getLogger(__name__)

class Virtual_environment():
    def __init__(self, sensors: List[SensorInterface], actuators: List[ActuatorInterface], mapping: List[Dict[str,str]]):
        self.sensors = sensors
        self.actuators = actuators

        self.mapping: Dict[(uuid,uuid):Dict[str,Union[float,bool]]] = {} # ('<uuid_actuator>','<uuid_sensor>'):{impact_factor:0, only_physical:False, 'active_influences':0}
        self.convert_environment_map(mapping)

    def __str__(self):
        return str(self.__dict__())

    def __dict__(self):
        return [{"uuid_actuator":str(a),"uuid_sensor":str(s), "impact_factor":value['impact_factor'], "only_physical":value['only_physical'], "active_influences":value['active_influences']} for (a,s),value in self.mapping.items()]

    def check_if_actuators_has_influenc(self, actuator_uuid: uuid):
        for actuator in self.actuators:
            if actuator.id == actuator_uuid:
                return not actuator.is_off()
        logger.warning('Environment bug check_if_actuators_has_influenc')
        return False

    def calculate_actuators_impact(self, actuator_uuid: str):
        for actuator in self.actuators:
            if actuator.id == actuator_uuid:
                if isinstance(actuator.last_value, str):
                    return 1
                return float(actuator.last_value)
        logger.warning('Environment bug check_if_actuators_has_influenc')
        return 0

    def calculate_next_active_influences_amount(self):
        for key, value in self.mapping.items():
            actuator = key[0]
            next_impact = 0
            if self.check_if_actuators_has_influenc(actuator) and not value['only_physical']:
                next_impact = value['impact_factor'] * self.calculate_actuators_impact(actuator)
            self.mapping.update({key:{'impact_factor':value['impact_factor'],'only_physical':value['only_physical'],'active_influences':next_impact}})

    def aggregate_impact_per_sensor(self):
        sensor_dict: Dict[SensorInterface, int] = {}

        for key, value in self.mapping.items():
            sensor = key[1]
            impact_factor = 0
            if sensor in sensor_dict:
                impact_factor = sensor_dict.get(sensor)
            impact_factor = impact_factor + value['active_influences']
            sensor_dict.update({sensor:impact_factor})

        return sensor_dict

    def apply_active_influences_amount(self):
        sensor_dict: Dict[SensorInterface, int] = self.aggregate_impact_per_sensor()

        for sensor in self.sensors:
            impact = 0
            if sensor.id in sensor_dict:
                impact = sensor_dict.get(sensor.id)
            sensor.virtual_environment_impact = impact

    def performe_environment_step(self):
        logger.info('Environment step is starting')
        self.calculate_next_active_influences_amount()
        self.apply_active_influences_amount()

    def convert_environment_map(self, mapping: List[Dict[str,str]]):
        for dictionary_map in mapping:
            try:
                actuator_name = str(dictionary_map['actuator_name'])
                sensor_name = str(dictionary_map['sensor_name'])
                impact_factor = float(dictionary_map['impact_factor'])
                only_physical = bool(dictionary_map['only_physical'] in ['True'])
            except Exception as e:
                print (e, flush=True)
                logger.error(f"{e}")

            actuator_uuid = self.find_uuid(actuator_name, self.actuators)
            sensor_uuid = self.find_uuid(sensor_name, self.sensors)
            key_pair = (actuator_uuid,sensor_uuid)
            self.mapping.update({key_pair:{'impact_factor':impact_factor,'only_physical':only_physical, 'active_influences':0}})

    def find_uuid(self, name: str, object_list: List[Union[SensorInterface,ActuatorInterface]]):
        for element in object_list:
            if element.name == name:
                return element.id
        raise LookupError
