#!/usr/bin/env python

# pip install pddl==0.4.3
from pddl.logic import variables


def create_type_variables():
    # set up variables
    floor_type, floor2_type = variables("floor_type floor2_type", types=["floor_type"])
    room_type, room2_type, room3_type = variables("room_type room2_type room3_type", types=["room_type"])
    room_position_type = variables("room_position_type", types=["room_position_type"])[0]
    iot_type = variables("iot_type", types=["iot_type"])[0]
    cleaning_team_type = variables("cleaning_team_type", types=["cleaning_team_type"])[0]

    sensor_type = variables("sensor_type", types=["sensor_type"])[0]
    actuator_type, actuator2_type = variables("actuator_type actuator2_type", types=["actuator_type"])
    
    binary_s_type, numerical_s_type, textual_s_type = variables("binary_s_type numerical_s_type textual_s_type", types=["sensor_type"])
    binary_a_type, numerical_a_type, textual_a_type = variables("binary_a_type numerical_a_type textual_a_type", types=["actuator_type"])

    return floor_type, floor2_type, room_type, room2_type, room3_type, room_position_type, iot_type, cleaning_team_type, sensor_type, actuator_type, actuator2_type, binary_s_type, numerical_s_type, textual_s_type, binary_a_type, numerical_a_type, textual_a_type


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
        "virtual_switch_s_type": "binary_s_type",

        "temperature_s_type": "numerical_s_type",
        "humidity_s_type": "numerical_s_type",
        "light_s_type": "numerical_s_type",
        "sound_s_type": "numerical_s_type",
        "rotation_s_type": "numerical_s_type",
        "virtual_dimmer_s_type": "numerical_s_type",

        "switch_a_type": "binary_a_type",
        "light_switch_a_type": "binary_a_type",
        "virtual_switch_a_type": "binary_a_type",

        "light_dimmer_a_type": "numerical_a_type",
        "virtual_dimmer_a_type": "numerical_a_type",

        "display_a_type": "textual_a_type",
    }
    return type_dict
