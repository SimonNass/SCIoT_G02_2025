#!/usr/bin/env python
"""Module specifies the goal state of a pddl problem file."""

# pip install pddl==0.4.3
from pddl.logic import base, variables
from typing import List, Dict

def create_goal(predicates_dict: Dict[str,variables], pddl_variable_types: Dict[str,List[variables]], plan_cleaning: bool = True):

    room_type: variables = pddl_variable_types["room"][0]
    room_position_type: variables = pddl_variable_types["room_position"][0]
    actuator_type: variables = pddl_variable_types["actuator"][0]

    is_activated = predicates_dict["is_activated"]
    is_cleaned = predicates_dict["is_cleaned"]
    is_occupied = predicates_dict["is_occupied"]
    sensor_is_part_of_room = predicates_dict["sensor_is_part_of_room"]
    actuator_is_part_of_room = predicates_dict["actuator_is_part_of_room"]
    
    is_locked = predicates_dict["is_locked"]
    checked_all_activitys = predicates_dict["checked_all_activitys"]
    fulfilled_activitys = predicates_dict["fulfilled_activitys"]

    sensor_goal_state_mapping = {'temperature_s':'is_ok', 
                                 'light_s':'is_high', 
                                 'sound_s':'is_ok'}

    goal_for_sensors_default = base.And()
    for sensor_type_x, expected_value in sensor_goal_state_mapping.items():
        sensor_type_x_variable: variables = pddl_variable_types[sensor_type_x][0]
        if_sensor_is = base.And(is_occupied(room_type), sensor_is_part_of_room(sensor_type_x_variable, room_type), base.Not(is_locked(sensor_type_x_variable)))
        then_have_this_value = predicates_dict[expected_value](sensor_type_x_variable)
        goal_for_this_sensors_default = base.ForallCondition(base.Imply(if_sensor_is, then_have_this_value), [sensor_type_x_variable, room_type])
        goal_for_sensors_default = base.And(goal_for_sensors_default, goal_for_this_sensors_default)

    if_case1 = base.Not(is_occupied(room_type))
    then_clean_case = is_cleaned(room_type)
    clean_unoccupied_rooms = base.ForallCondition(base.Imply(if_case1, then_clean_case), [room_type])

    if_case2 = base.And(base.Not(is_occupied(room_type)), actuator_is_part_of_room(actuator_type, room_type))
    then_turn_off_actuator = base.Not(is_activated(actuator_type))
    actuator_off_unoccupied_rooms = base.ForallCondition(base.Imply(if_case2, then_turn_off_actuator), [room_type, actuator_type])

    enforce_checks = base.And(base.ForallCondition(checked_all_activitys(room_type, room_position_type), [room_type, room_position_type]),
                              base.ForallCondition(fulfilled_activitys(room_type, room_position_type), [room_type, room_position_type]))

    goal_state = base.And(goal_for_sensors_default, actuator_off_unoccupied_rooms, enforce_checks)
    if plan_cleaning:
        goal_state = base.And(goal_state, clean_unoccupied_rooms)
    return goal_state
