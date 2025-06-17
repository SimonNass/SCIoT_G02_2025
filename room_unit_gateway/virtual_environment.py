from typing import List, Dict

from sensors.sensor import SensorInterface
from actuators.actuator import ActuatorInterface

class Virtual_environment():
    def __init__(self, sensors: List[SensorInterface], actuator: List[ActuatorInterface], mapping: Dict):
        self.sensors = sensors
        self.actuator = actuator
        # TODO make this code more efficient?
        self.mapping_actuators_to_sensors = {} # '<uuid_actuator>':'<uuid_sensor>'
        self.mapping_values = {} # ('<uuid_actuator>','<uuid_sensor>'):(0,0,0,0)

        self.active_influences_cycle = {} # ('<uuid_actuator>','<uuid_sensor>'):0
        self.active_influences_amount = {} # ('<uuid_actuator>','<uuid_sensor>'):0

    def check_all_actuators_for_intraced_influences(self):
        for actuator in self.actuator:
            if (actuator.last_value == actuator.off_value):
                # the actuator is off and therefore it is not influencing sensors
                continue
            for sensor in self.mapping_actuators_to_sensors.at(actuator):
                if self.active_influences_cycle.contains((actuator,sensor)):
                    # the actuator sensor pair is already in the active_influences_cycle
                    continue
                # add them to active_influences_cycle
                self.active_influences_cycle.update({(actuator,sensor):0})

    def calculate_next_active_influences_amount(self):
        for (key, value) in self.active_influences_cycle:
            impact = self.mapping.at(key)[0]
            fade_in = self.mapping.at(key)[1]
            impact_duration = self.mapping.at(key)[2]
            fade_out = self.mapping.at(key)[3]

            if value + 1 > fade_in + impact_duration + fade_out:
                # impact of actuator ended
                self.active_influences_cycle.pop(key, "Key not found")
                # TODO turn Actuator off?
                continue

            next_impact = 0
            if value + 1 <= fade_in:
                # fade_in
                step_impact = impact / fade_in
                next_impact = step_impact * value + 1
            elif value + 1 <= fade_in + impact_duration:
                # impact_duration
                next_impact = impact
            elif value + 1 <= fade_in + impact_duration + fade_out:
                # fade_out
                step_impact = impact / fade_out
                next_impact = step_impact * (value + 1 - fade_in - impact_duration)
            else:
                raise ArithmeticError('Environment bug')
            self.active_influences_cycle.update({key:value+1})
            self.active_influences_amount.update({key:next_impact})

    def apply_active_influences_amount(self):
        for (key, value) in self.active_influences_amount:
            pass
        # TODO

    def performe_environment_step(self):
        self.check_all_actuators_for_intraced_influences()
        self.calculate_next_active_influences_amount()
        self.apply_active_influences_amount()
