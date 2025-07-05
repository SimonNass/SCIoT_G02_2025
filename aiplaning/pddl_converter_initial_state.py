#!/usr/bin/env python

# pip install pddl==0.4.3
from typing import Dict, List
from pddl.logic import constants
import pddl_converter_help

def create_initial_state_room_topology(room_is_part_of_floor, is_next_to, is_cleaned, floor_uids, room_uids_per_floor, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, elevators):
    initial_state = []

    #comulative_rooms_bevore = [sum(rooms_per_floor[:i]) for i in range(len(rooms_per_floor))]
    #print (comulative_rooms_bevore)

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

    for i in range(len(elevators)):
        for floor in floor_uids:
            # connect the elevators to all floors
            next_elevator_floor_mapping = room_is_part_of_floor(elevators[i],uid_to_pddl_variable_floor[floor])
            initial_state.append(next_elevator_floor_mapping)
        
            # connect the elevators to a room in each floor
            room_near_elevator = uid_to_pddl_variable_rooms[room_uids_per_floor[floor][i % len(room_uids_per_floor[floor])]]

            next_elevator_room_mapping = is_next_to(elevators[i],room_near_elevator)
            initial_state.append(next_elevator_room_mapping)
            next_elevator_room_mapping = is_next_to(room_near_elevator,elevators[i])
            initial_state.append(next_elevator_room_mapping)

        # elevators do not have to be cleaned
        next_elevator_is_clean = is_cleaned(elevators[i])
        initial_state.append(next_elevator_is_clean)

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
