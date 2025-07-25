#!/usr/bin/env python
"""Module specifies the types of a pddl domain file."""

# pip install pddl==0.4.3
from pddl.logic import variables

def create_type_variable_by_name(name: str, amount):
    names = "".join(f"{name}{i}_type " for i in range(amount))
    pddl_variables =  variables(names, types=[f"{name}_type"])
    #print (var)
    return pddl_variables

def create_type_variables():
    # set up variables
    type_names = {"floor": 2,
                  "room": 3,
                  "room_position": 2,
                  "iot": 2,
                  "cleaning_team": 2,
                  "sensor": 2,
                  "actuator": 2,
                  "binary_s": 2,
                  "numerical_s": 2,
                  "textual_s": 2,
                  "binary_a": 2,
                  "numerical_a": 2,
                  "textual_a": 2,
                  "temperature_s": 2,
                  "humidity_s": 2,
                  "light_s": 2,
                  "sound_s": 2,
                  "window_rotation_s": 2,
                  "power_consumption_s": 2,
                  "TV_volume_s": 2,
                  "motion_s": 2,
                  "button_s": 2,
                  "bed_s": 2,
                  "chair_s": 2,
                  "shower_s": 2,
                }

    pddl_variables = {}
    for name, amount in type_names.items():
        pddl_variables.update({name:create_type_variable_by_name(name, amount)})

    return pddl_variables

def create_type_dict():
    # set up types
    type_dict = {
        "object_type": None,

        "floor_type": "object_type",
        "room_type": "object_type",
        "room_position_type": "object_type",
        "iot_type": "object_type",
        "cleaning_team_type": "object_type",

        "sensor_type": "iot_type",
        "actuator_type": "iot_type",

        "binary_s_type": "sensor_type",
        "numerical_s_type": "sensor_type",
        "textual_s_type": "sensor_type",

        "binary_a_type": "actuator_type",
        "numerical_a_type": "actuator_type",
        "textual_a_type": "actuator_type",

        "button_s_type": "binary_s_type",
        "motion_s_type": "binary_s_type",
        "pressure_s_type": "binary_s_type",

        "temperature_s_type": "numerical_s_type",
        "humidity_s_type": "numerical_s_type",
        "light_s_type": "numerical_s_type",
        "sound_s_type": "numerical_s_type",
        "window_rotation_s_type": "numerical_s_type",
        "power_consumption_s_type": "numerical_s_type",
        
        "TV_volume_s_type": "sound_s_type",

        "bed_s_type": "pressure_s_type",
        "chair_s_type": "pressure_s_type",
        "shower_s_type": "pressure_s_type",

        "switch_a_type": "binary_a_type",
        "light_switch_a_type": "binary_a_type",

        "light_dimmer_a_type": "numerical_a_type",

        "display_a_type": "textual_a_type",
    }
    return type_dict
