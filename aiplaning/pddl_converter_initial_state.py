#!/usr/bin/env python
"""Module specifies the initial state of a pddl problem file."""

# pip install pddl==0.4.3
from typing import Dict, List
from pddl.logic import constants, base
import pddl_converter_help

def create_initial_state_room_topology(room_is_part_of_floor, is_next_to, is_cleaned, floor_uids, room_uids_per_floor, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, uid_to_pddl_variable_elevators: Dict):
    initial_state = []

    # assigns each rooms to one floor they are a part of
    for floor in floor_uids:
        for room in room_uids_per_floor[floor]:
            next_room_floor_mapping = room_is_part_of_floor(uid_to_pddl_variable_rooms[room], uid_to_pddl_variable_floor[floor])
            initial_state.append(next_room_floor_mapping)

    # connects rooms that are next to each other on the same floor
    # defaults to a line topology
    for floor in floor_uids:
        for i in range(len(room_uids_per_floor[floor]) - 1):
            current_room = uid_to_pddl_variable_rooms[room_uids_per_floor[floor][i]]
            next_room = uid_to_pddl_variable_rooms[room_uids_per_floor[floor][i + 1]]

            next_room_room_mapping = is_next_to(current_room, next_room)
            initial_state.append(next_room_room_mapping)
            next_room_room_mapping = is_next_to(next_room, current_room)
            initial_state.append(next_room_room_mapping)

    for elevator in uid_to_pddl_variable_elevators.values():
        for floor in floor_uids:
            # connect the elevators to all floors
            next_elevator_floor_mapping = room_is_part_of_floor(elevator,uid_to_pddl_variable_floor[floor])
            initial_state.append(next_elevator_floor_mapping)

            # connect the elevators to a room in each floor
            room_near_elevator = uid_to_pddl_variable_rooms[room_uids_per_floor[floor][i % len(room_uids_per_floor[floor])]]

            next_elevator_room_mapping = is_next_to(elevator,room_near_elevator)
            initial_state.append(next_elevator_room_mapping)
            next_elevator_room_mapping = is_next_to(room_near_elevator,elevator)
            initial_state.append(next_elevator_room_mapping)

        # elevators do not have to be cleaned
        next_elevator_is_clean = is_cleaned(elevator)
        initial_state.append(next_elevator_is_clean)

    return initial_state

def create_cleaning_teams_starting_position(uid_to_pddl_variable_cleaning_teams: Dict, uid_to_pddl_variable_elevators: Dict, is_at):
    initial_state = []

    cleaning_teams = list(uid_to_pddl_variable_cleaning_teams.values())
    elevators = list(uid_to_pddl_variable_elevators.values())
    for i, cleaning_team in enumerate(cleaning_teams):
        next_is_at = is_at(cleaning_team, elevators[i % len(elevators)])
        initial_state.append(next_is_at)

    return initial_state

def create_iot_room_mapping(floor_uids: List[str], room_uids_per_floor:Dict[str,List[str]], uids_to_object: Dict[str,constants], uids_to_room: Dict[str,constants], room_mapping: Dict[str,List[str]], iot_is_part_of_room):
    initial_state = []

    for room in pddl_converter_help.iterator_ofer_dict_list_elements(floor_uids,room_uids_per_floor):
        sensor_room = uids_to_room[room]
        if room not in room_mapping:
            continue
        for device in room_mapping[room]:
            object_instance = uids_to_object[device]
            next_part_of_room = iot_is_part_of_room(object_instance, sensor_room)
            initial_state.append(next_part_of_room)

    return initial_state

def create_iot_position_mapping(uid_to_pddl_variable_room_positions, uid_to_pddl_variable_sensors: Dict, uid_to_pddl_variable_actuators: Dict, positioned_at):
    initial_state = []

    # TODO
    room_positions_default = list(uid_to_pddl_variable_room_positions.values())[0]
    for sensor_object in uid_to_pddl_variable_sensors.values():
        next_pos = positioned_at(sensor_object, room_positions_default)
        initial_state.append(next_pos)

    for actuator_object in uid_to_pddl_variable_actuators.values():
        next_pos = positioned_at(actuator_object, room_positions_default)
        initial_state.append(next_pos)

    return initial_state

def create_iot_influences_iot_mapping(actuator_increases_sensor_mapping_matrix, actuator_decreases_sensor_mapping_matrix, uid_to_pddl_variable_actuators, uid_to_pddl_variable_sensors, actuator_increases_sensor, actuator_decreases_sensor):
    initial_state = []

    assert len(actuator_increases_sensor_mapping_matrix.keys()) <= len(uid_to_pddl_variable_actuators)
    for _, sensor_list_mapping in actuator_increases_sensor_mapping_matrix.items():
        assert len(sensor_list_mapping) <= len(uid_to_pddl_variable_sensors)
    assert len(actuator_decreases_sensor_mapping_matrix.keys()) <= len(uid_to_pddl_variable_actuators)
    for _, sensor_list_mapping in actuator_decreases_sensor_mapping_matrix.items():
        assert len(sensor_list_mapping) <= len(uid_to_pddl_variable_sensors)

    for a, s_list in actuator_increases_sensor_mapping_matrix.items():
        for s in s_list:
            next_influence = actuator_increases_sensor(uid_to_pddl_variable_actuators[a], uid_to_pddl_variable_sensors[s])
            initial_state.append(next_influence)
    for a, s_list in actuator_decreases_sensor_mapping_matrix.items():
        for s in s_list:
            next_influence = actuator_decreases_sensor(uid_to_pddl_variable_actuators[a], uid_to_pddl_variable_sensors[s])
            initial_state.append(next_influence)

    return initial_state

def create_sensor_values(is_high, is_ok, is_low, floor_uids: List[str], room_uids_per_floor:Dict[str,List[str]], sensor_room_mapping:Dict[str,List[str]], uid_to_pddl_variable_sensors: Dict[str,constants], sensor_initial_values: List[int]):
    state_list = []

    for room in pddl_converter_help.iterator_ofer_dict_list_elements(floor_uids,room_uids_per_floor):
        if room not in sensor_room_mapping:
            continue
        for s in sensor_room_mapping[room]:
            sensor_object = uid_to_pddl_variable_sensors[s]
            object_state = 0
            state = is_ok(sensor_object)
            if s in sensor_initial_values:
                object_state = sensor_initial_values[s]
            if object_state == -1:
                state = is_low(sensor_object)
            elif object_state == 0:
                state = is_ok(sensor_object)
            elif object_state == 1:
                state = is_high(sensor_object)
            state_list.append(state)

    return state_list

def create_actuator_values(is_activated, floor_uids: List[str], room_uids_per_floor:Dict[str,List[str]], actuator_room_mapping:Dict[str,List[str]], uid_to_pddl_variable_actuators: Dict[str,constants], actuator_initial_values: List[int]):
    initial_state = []

    for room in pddl_converter_help.iterator_ofer_dict_list_elements(floor_uids,room_uids_per_floor):
        if room not in actuator_room_mapping:
            continue
        for a in actuator_room_mapping[room]:
            actuator_object = uid_to_pddl_variable_actuators[a]
            object_state = False
            if a in actuator_initial_values:
                object_state = actuator_initial_values[a]
            state = base.Not(is_activated(actuator_object))
            if object_state:
                state = is_activated(actuator_object)
            initial_state.append(state)

    return initial_state

def create_room_occupied_values(is_occupied, room_occupied_actuator_initial_values, floor_uids: List[str], room_uids_per_floor:Dict[str,List[str]], uid_to_pddl_variable_rooms):
    initial_state = []

    for room in pddl_converter_help.iterator_ofer_dict_list_elements(floor_uids,room_uids_per_floor):
        object_state = room_occupied_actuator_initial_values[room]
        if object_state:
            state = is_occupied(uid_to_pddl_variable_rooms[room])
        else:
            state = base.Not(is_occupied(uid_to_pddl_variable_rooms[room]))
        initial_state.append(state)

    return initial_state
