#!/usr/bin/env python
"""Module specifies the initial state of a pddl problem file."""

# pip install pddl==0.4.3
from typing import Dict, List
from pddl.logic import variables, constants, base
import pddl_converter_help

def create_initial_state_room_topology(predicates_dict: Dict[str,variables], floor_uids, room_uids_per_floor, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms):
    initial_state = []

    room_is_part_of_floor = predicates_dict["room_is_part_of_floor"]
    is_next_to = predicates_dict["is_next_to"]

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

    return initial_state

def create_initial_state_elevator_topology(predicates_dict: Dict[str,variables], floor_uids, room_uids_per_floor, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, uid_to_pddl_variable_elevators: Dict, uid_to_pddl_variable_room_positions: Dict):
    initial_state = []

    room_is_part_of_floor = predicates_dict["room_is_part_of_floor"]
    is_next_to = predicates_dict["is_next_to"]
    is_cleaned = predicates_dict["is_cleaned"]
    checked_all_activitys = predicates_dict["checked_all_activitys"]
    fulfilled_activitys = predicates_dict["fulfilled_activitys"]

    for i, elevator in enumerate(uid_to_pddl_variable_elevators.values()):
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

        for position in uid_to_pddl_variable_room_positions.values():
            # exclude elevators from activity search
            next_elevator_checked = checked_all_activitys(elevator, position)
            initial_state.append(next_elevator_checked)
            next_elevator_fulfilled = fulfilled_activitys(elevator, position)
            initial_state.append(next_elevator_fulfilled)

    return initial_state

def create_cleaning_teams_starting_position(predicates_dict: Dict[str,variables], uid_to_pddl_variable_cleaning_teams: Dict, uid_to_pddl_variable_elevators: Dict):
    initial_state = []

    is_at = predicates_dict["is_at"]

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

def create_iot_position_mapping(predicates_dict: Dict[str,variables], uid_to_pddl_variable_room_positions, uid_to_pddl_variable_sensors: Dict, uid_to_pddl_variable_actuators: Dict):
    initial_state = []

    positioned_at = predicates_dict["positioned_at"]

    # TODO map input positions
    room_positions_default = list(uid_to_pddl_variable_room_positions.values())[0]
    for sensor_object in uid_to_pddl_variable_sensors.values():
        next_pos = positioned_at(sensor_object, room_positions_default)
        initial_state.append(next_pos)

    for actuator_object in uid_to_pddl_variable_actuators.values():
        next_pos = positioned_at(actuator_object, room_positions_default)
        initial_state.append(next_pos)

    return initial_state

def create_iot_influences_iot_mapping(predicates_dict: Dict[str,variables], actuator_increases_sensor_mapping_matrix, actuator_decreases_sensor_mapping_matrix, uid_to_pddl_variable_actuators, uid_to_pddl_variable_sensors):
    initial_state = []

    actuator_increases_sensor = predicates_dict["actuator_increases_sensor"]
    actuator_decreases_sensor = predicates_dict["actuator_decreases_sensor"]

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

def create_sensor_values(predicates_dict: Dict[str,variables], floor_uids: List[str], room_uids_per_floor:Dict[str,List[str]], sensor_room_mapping:Dict[str,List[str]], uid_to_pddl_variable_sensors: Dict[str,constants], sensor_initial_values: List[int]):
    state_list = []

    is_low = predicates_dict["is_low"]
    is_ok = predicates_dict["is_ok"]
    is_high = predicates_dict["is_high"]

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

def create_sensor_locks(predicates_dict: Dict[str,variables], sensor_initial_locked: List[str], uid_to_pddl_variable_sensors: Dict[str,constants]):
    state_list = []

    is_locked = predicates_dict["is_locked"]

    for s in sensor_initial_locked:
        sensor_object = uid_to_pddl_variable_sensors[s]
        state = is_locked(sensor_object)
        state_list.append(state)

    return state_list

def create_actuator_values(predicates_dict: Dict[str,variables], floor_uids: List[str], room_uids_per_floor:Dict[str,List[str]], actuator_room_mapping:Dict[str,List[str]], uid_to_pddl_variable_actuators: Dict[str,constants], actuator_initial_values: List[int]):
    initial_state = []

    is_activated = predicates_dict["is_activated"]

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

def create_room_occupied_values(predicates_dict: Dict[str,variables], room_occupied_initial_values, floor_uids: List[str], room_uids_per_floor:Dict[str,List[str]], uid_to_pddl_variable_rooms):
    initial_state = []

    is_occupied = predicates_dict["is_occupied"]

    for room in pddl_converter_help.iterator_ofer_dict_list_elements(floor_uids,room_uids_per_floor):
        object_state = room_occupied_initial_values[room]
        if object_state:
            state = is_occupied(uid_to_pddl_variable_rooms[room])
        else:
            state = base.Not(is_occupied(uid_to_pddl_variable_rooms[room]))
        initial_state.append(state)

    return initial_state

def create_initial_state(predicates_dict: Dict[str,variables], input_dictionary: Dict, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, uid_to_pddl_variable_sensors,uid_to_pddl_variable_actuators, uid_to_pddl_variable_elevators, uid_to_pddl_variable_cleaning_teams, uid_to_pddl_variable_room_positions):
    initial_state = []

    floor_uids = input_dictionary['floor_uids']
    room_uids_per_floor = input_dictionary['room_uids_per_floor']
    elevator_uids = input_dictionary['elevator_uids']
    assert 1 <= len(elevator_uids)

    sensor_room_mapping = input_dictionary['sensor_room_mapping']
    actuator_room_mapping = input_dictionary['actuator_room_mapping']

    actuator_increases_sensor_mapping_matrix = input_dictionary['actuator_increases_sensor_mapping_matrix']
    actuator_decreases_sensor_mapping_matrix = input_dictionary['actuator_decreases_sensor_mapping_matrix']

    sensor_initial_values = input_dictionary['sensor_initial_values']
    # TODO
    sensor_initial_locked = input_dictionary['sensor_initial_locked']
    actuator_initial_values = input_dictionary['actuator_initial_values']
    room_occupied_initial_values = input_dictionary['room_occupied_initial_values']

    initial_state = initial_state + create_initial_state_room_topology(predicates_dict, floor_uids, room_uids_per_floor, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms)
    initial_state = initial_state + create_initial_state_elevator_topology(predicates_dict, floor_uids, room_uids_per_floor, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, uid_to_pddl_variable_elevators, uid_to_pddl_variable_room_positions)

    initial_state = initial_state + create_cleaning_teams_starting_position(predicates_dict, uid_to_pddl_variable_cleaning_teams, uid_to_pddl_variable_elevators)

    sensor_is_part_of_room = predicates_dict["sensor_is_part_of_room"]
    initial_state = initial_state + create_iot_room_mapping(floor_uids, room_uids_per_floor, uid_to_pddl_variable_sensors, uid_to_pddl_variable_rooms, sensor_room_mapping, sensor_is_part_of_room)
    actuator_is_part_of_room = predicates_dict["actuator_is_part_of_room"]
    initial_state = initial_state + create_iot_room_mapping(floor_uids, room_uids_per_floor, uid_to_pddl_variable_actuators, uid_to_pddl_variable_rooms, actuator_room_mapping, actuator_is_part_of_room)

    initial_state = initial_state + create_iot_position_mapping(predicates_dict, uid_to_pddl_variable_room_positions, uid_to_pddl_variable_sensors, uid_to_pddl_variable_actuators)

    initial_state = initial_state + create_iot_influences_iot_mapping(predicates_dict, actuator_increases_sensor_mapping_matrix, actuator_decreases_sensor_mapping_matrix, uid_to_pddl_variable_actuators, uid_to_pddl_variable_sensors)

    assert len(sensor_initial_values) <= len(uid_to_pddl_variable_sensors)
    assert len(actuator_initial_values) <= len(uid_to_pddl_variable_actuators)

    initial_state = initial_state + create_sensor_values(predicates_dict, floor_uids, room_uids_per_floor, sensor_room_mapping, uid_to_pddl_variable_sensors, sensor_initial_values)
    initial_state = initial_state + create_sensor_locks(predicates_dict, sensor_initial_locked, uid_to_pddl_variable_sensors)

    initial_state = initial_state + create_actuator_values(predicates_dict, floor_uids, room_uids_per_floor, actuator_room_mapping, uid_to_pddl_variable_actuators, actuator_initial_values)

    # context room occupied
    assert len(room_occupied_initial_values) <= len(uid_to_pddl_variable_rooms)
    initial_state = initial_state + create_room_occupied_values(predicates_dict, room_occupied_initial_values, floor_uids, room_uids_per_floor, uid_to_pddl_variable_rooms)

    return initial_state
