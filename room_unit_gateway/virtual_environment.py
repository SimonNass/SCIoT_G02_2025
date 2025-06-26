from typing import List, Dict
import logging
logger = logging.getLogger(__name__)

from sensors.sensor import SensorInterface
from actuators.actuator import ActuatorInterface

class Virtual_environment():
    def __init__(self, sensors: List[SensorInterface], actuators: List[ActuatorInterface], mapping: List[str]):
        self.sensors = sensors
        self.actuator = actuators
        self.mapping_values = {} # ('<uuid_actuator>','<uuid_sensor>'):{impact_amount:0, fade_in:0, impact_duration:0, fade_out:0}

        self.active_influences = {} # ('<uuid_actuator>','<uuid_sensor>'):{cycle:0, amount:0}
        self.convert_environment_map(mapping)

    def check_if_actuators_has_influenc(self, actuator_name: str):
        for actuator in self.actuator:
            if actuator.name != actuator_name:
                continue
            else:
                return actuator.last_value != actuator.off_value
        logger.info('Environment bug check_if_actuators_has_influenc')
        return False

    def calculate_next_active_influences_amount(self):
        for key, value in self.mapping_values.items():
            actuator = key[0]
            next_impact = 0
            next_cycle = 1
            if self.check_if_actuators_has_influenc(actuator):
                next_impact = int(value['impact_amount'])
            

            #fade_in = int(value['fade_in'])
            #impact_duration = int(value['impact_duration'])
            #fade_out = int(value['fade_out'])

            #cycle = self.active_influences.get(key)['cycle']
            #_ = self.active_influences.get(key)['amount']

            #if cycle + 1 > fade_in + impact_duration + fade_out:
            #    # impact of actuator ended
            #    self.active_influences.update({key:{'cycle':0, 'amount':0}})
            #    continue

            #next_impact = 0
            #if cycle + 1 <= fade_in:
            #    # fade_in
            #    step_impact = impact / fade_in
            #    next_impact = step_impact * cycle + 1
            #elif cycle + 1 <= fade_in + impact_duration:
            #    # impact_duration
            #    next_impact = impact
            #elif cycle + 1 <= fade_in + impact_duration + fade_out:
            #    # fade_out
            #    step_impact = impact / fade_out
            #    next_impact = step_impact * (cycle + 1 - fade_in - impact_duration)
            #else:
            #    logger.info('Environment bug')
            #    raise ArithmeticError('Environment bug calculate_next_active_influences_amount')
            self.active_influences.update({key:{'cycle':next_cycle, 'amount':next_impact}})

    def aggregate_impact_per_sensor(self):
        sensor_dict: Dict[SensorInterface, int] = {}

        for key, value in self.active_influences.items():
            sensor = key[1]
            impact_amount = 0
            if sensor in sensor_dict:
                impact_amount = int(sensor_dict.get(sensor))
            impact_amount = impact_amount + value['amount']
            sensor_dict.update({sensor:impact_amount})

        return sensor_dict

    def apply_active_influences_amount(self):
        sensor_dict: Dict[SensorInterface, int] = self.aggregate_impact_per_sensor()

        for sensor in self.sensors:
            impact = 0
            if sensor.name in sensor_dict:
                impact = sensor_dict.get(sensor.name)
            sensor.virtual_environment_impact = impact

    def performe_environment_step(self):
        logger.info('Environment step is starting')
        self.calculate_next_active_influences_amount()
        self.apply_active_influences_amount()

    def convert_environment_map(self, mapping: List[str]):
        for dictionary_map in mapping:
            try:
                actuator_name = str(dictionary_map['actuator_name'])
                sensor_name = str(dictionary_map['sensor_name'])
                impact_amount = int(dictionary_map['impact_amount'])
                #fade_in = int(dictionary_map['fade_in'])
                #impact_duration = int(dictionary_map['impact_duration'])
                #fade_out = int(dictionary_map['fade_out'])
                dictionary = {
                    'impact_amount':impact_amount, 
                    #'fade_in':fade_in, 
                    #'impact_duration':impact_duration, 
                    #'fade_out':fade_out
                }
            except Exception as e:
                print (e, flush=True)
                logger.info("{}".format(e))

            self.mapping_values.update({(actuator_name,sensor_name):dictionary})
            self.active_influences.update({(actuator_name,sensor_name):{'cycle':0, 'amount':0}})

