#!/usr/bin/env python
"""Module converts the ai plan to executable functions."""

from typing import List
from enum import Enum

class PlanerTag(Enum):
    """Class representing the possible planer tags given to actions during the creation."""
    Helper = 11 # helper actions can be ignored

    # specifies the intention of an action
    Clean_Intent = 21
    Assignment_Intent = 21
    Change_Sensor_Intent = 22
    Detect_Activity_Intent = 23
    Fulfill_Activity_Intent = 24
    Save_Energy_Intent = 25

    Actuator_Off = 31 # turn off actuator
    Actuator_Increse = 32 # increse actuator
    Actuator_Decrese = 33 # decrese actuator
    Actuator_Cancle_Out = 34 # two actuators are infolfed

class pddl_actions_to_execution_mapper():
    def __init__(self):
        self.pddl_actions_to_execution_map = {}

    def add_action(self, name: str, parametertypes: List[str], planertags: List[PlanerTag]):
        self.pddl_actions_to_execution_map.update({name:(parametertypes, planertags)})