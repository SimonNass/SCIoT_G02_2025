#!/usr/bin/env python
"""Module specifies the predicates of a pddl domain file."""

# pip install pddl==0.4.3
from typing import List, Dict
from pddl.logic import Predicate, variables

def create_predicates_variables_topology(pddl_variable_types: Dict[str,List[variables]]):
    predicates_dict = {}

    floor_type = pddl_variable_types["floor"][0]
    room_type = pddl_variable_types["room"][0]
    room2_type = pddl_variable_types["room"][1]
    room_position_type = pddl_variable_types["room_position"][0]
    iot_type = pddl_variable_types["iot"][0]
    sensor_type = pddl_variable_types["sensor"][0]
    actuator_type = pddl_variable_types["actuator"][0]

    # topology
    room_is_part_of_floor = Predicate("room_is_part_of_floor", room_type, floor_type)
    predicates_dict.update({"room_is_part_of_floor":room_is_part_of_floor})

    sensor_is_part_of_room = Predicate("sensor_is_part_of_room", sensor_type, room_type)
    predicates_dict.update({"sensor_is_part_of_room":sensor_is_part_of_room})
    actuator_is_part_of_room = Predicate("actuator_is_part_of_room", actuator_type, room_type)
    predicates_dict.update({"actuator_is_part_of_room":actuator_is_part_of_room})
    # problem to lock down a sensor that is part of two room positions
    positioned_at = Predicate("positioned_at", iot_type, room_position_type)
    predicates_dict.update({"positioned_at":positioned_at})

    actuator_increases_sensor = Predicate("actuator_increases_sensor", actuator_type, sensor_type)
    predicates_dict.update({"actuator_increases_sensor":actuator_increases_sensor})
    actuator_decreases_sensor = Predicate("actuator_decreases_sensor", actuator_type, sensor_type)
    predicates_dict.update({"actuator_decreases_sensor":actuator_decreases_sensor})

    is_next_to = Predicate("is_next_to", room_type, room2_type)
    predicates_dict.update({"is_next_to":is_next_to})

    return predicates_dict

def create_predicates_variables_meta_context(pddl_variable_types: Dict[str,List[variables]]):
    predicates_dict = {}

    room_type = pddl_variable_types["room"][0]
    cleaning_team_type = pddl_variable_types["cleaning_team"][0]

    is_at = Predicate("is_at", cleaning_team_type, room_type)
    predicates_dict.update({"is_at":is_at})

    is_occupied = Predicate("is_occupied", room_type)
    predicates_dict.update({"is_occupied":is_occupied})

    will_become_occupied = Predicate("will_become_occupied", room_type)
    predicates_dict.update({"will_become_occupied":will_become_occupied})

    is_cleaned = Predicate("is_cleaned", room_type)
    predicates_dict.update({"is_cleaned":is_cleaned})

    return predicates_dict

def create_predicates_variables_activitys(pddl_variable_types: Dict[str,List[variables]], activity_names: List[str]):
    predicates_dict = {}

    room_type = pddl_variable_types["room"][0]
    room_position_type = pddl_variable_types["room_position"][0]

    for activity in activity_names:
        is_doing_a_at = Predicate(f"is_doing_{activity}_at", room_type, room_position_type)
        predicates_dict.update({f"is_doing_{activity}_at":is_doing_a_at})

    # force checks predicate
    for activity in activity_names:
        checked_a = Predicate(f"checked_activity_{activity}", room_type, room_position_type)
        predicates_dict.update({f"checked_activity_{activity}":checked_a})

    for activity in activity_names:
        fulfilled_a = Predicate(f"fulfilled_activity_{activity}", room_type, room_position_type)
        predicates_dict.update({f"fulfilled_activity_{activity}":fulfilled_a})

    checked_all_activitys = Predicate("checked_activitys", room_type, room_position_type)
    predicates_dict.update({"checked_all_activitys":checked_all_activitys})

    fulfilled_activitys = Predicate("fulfilled_activitys", room_type, room_position_type)
    predicates_dict.update({"fulfilled_activitys":fulfilled_activitys})

    return predicates_dict

def create_predicates_variables_sensors(pddl_variable_types: Dict[str,List[variables]]):
    predicates_dict = {}

    sensor_type = pddl_variable_types["sensor"][0]
    numerical_s_type = pddl_variable_types["numerical_s"][0]
    iot_type = pddl_variable_types["iot"][0]

    has_initial_state = Predicate("has_initial_state", iot_type)
    predicates_dict.update({"has_initial_state":has_initial_state})

    is_locked = Predicate("is_locked", sensor_type)
    predicates_dict.update({"is_locked":is_locked})

    is_sensing = Predicate("is_sensing", sensor_type)
    predicates_dict.update({"is_sensing":is_sensing})

    is_low = Predicate("is_low", numerical_s_type)
    predicates_dict.update({"is_low":is_low})
    is_ok = Predicate("is_ok", numerical_s_type)
    predicates_dict.update({"is_ok":is_ok})
    is_high = Predicate("is_high", numerical_s_type)
    predicates_dict.update({"is_high":is_high})

    return predicates_dict

def create_predicates_variables_actuators(pddl_variable_types: Dict[str,List[variables]]):
    predicates_dict = {}

    actuator_type = pddl_variable_types["actuator"][0]

    is_activated = Predicate("is_activated", actuator_type)
    predicates_dict.update({"is_activated":is_activated})
    is_changed = Predicate("is_changed", actuator_type)
    predicates_dict.update({"is_changed":is_changed})

    return predicates_dict

def create_predicates_variables(pddl_variable_types: Dict[str,List[variables]], activity_names: List[str]):
    # define predicates
    predicates_dict = {}

    predicates_dict.update(create_predicates_variables_topology(pddl_variable_types))
    predicates_dict.update(create_predicates_variables_meta_context(pddl_variable_types))
    predicates_dict.update(create_predicates_variables_activitys(pddl_variable_types, activity_names))
    predicates_dict.update(create_predicates_variables_sensors(pddl_variable_types))
    predicates_dict.update(create_predicates_variables_actuators(pddl_variable_types))

    return predicates_dict
