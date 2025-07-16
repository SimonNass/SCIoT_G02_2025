#!/usr/bin/env python
"""Module specifies the objects in the initial state of a pddl problem file."""

# pip install pddl==0.4.3
from typing import Dict, List
from pddl.logic import constants
from backend.aiplaning import pddl_converter_help

def create_objects(name_list: List[str], type_name: str):
    names = ''
    for name in name_list:
        names = names + str(f'{type_name}_{name} ')

    objects = constants(names, type_=type_name + '_type')
    #print (objects)
    return objects

def create_objects_room_topology(floor_uids: List[str], room_uids_per_floor: Dict[str,List[str]], elevator_uids: List[str]):
    floors = create_objects(floor_uids, "floor")
    uid_to_pddl_variable_floor = {floor_uids[i]:floors[i] for i in range(len(floors))}
    rooms = []
    uid_to_pddl_variable_rooms = {}
    for room_uids in room_uids_per_floor.values():
        new_rooms = create_objects(room_uids, "room")
        rooms = rooms + new_rooms
        uid_to_pddl_variable_rooms.update({room_uids[i]:new_rooms[i] for i in range(len(new_rooms))})
    elevators = create_objects(elevator_uids, "room")
    uid_to_pddl_variable_elevators = {elevator_uids[i]:elevators[i] for i in range(len(elevator_uids))}

    return floors, rooms, elevators, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, uid_to_pddl_variable_elevators

def create_sensors_and_actuators(floor_uids, room_uids_per_floor, sensor_room_mapping, actuator_room_mapping, sensor_types):
    sensors = []
    uid_to_pddl_variable_sensors = {}
    for room in pddl_converter_help.iterator_ofer_dict_list_elements(floor_uids,room_uids_per_floor):
        if room not in sensor_room_mapping:
            continue
        for sensor_name in sensor_room_mapping[room]:
            new_sensors = create_objects([sensor_name], sensor_types[sensor_name])
            sensors = sensors + new_sensors
            uid_to_pddl_variable_sensors.update({[sensor_name][i]:new_sensors[i] for i in range(len(new_sensors))})

    actuators = []
    uid_to_pddl_variable_actuators = {}
    for room in pddl_converter_help.iterator_ofer_dict_list_elements(floor_uids,room_uids_per_floor):
        if room not in actuator_room_mapping:
            continue
        new_actuators = create_objects(actuator_room_mapping[room], "actuator")
        actuators = actuators + new_actuators
        uid_to_pddl_variable_actuators.update({actuator_room_mapping[room][i]:new_actuators[i] for i in range(len(new_actuators))})
    return sensors, actuators, uid_to_pddl_variable_sensors, uid_to_pddl_variable_actuators

def create_all_obbjects(input_dictionary: Dict):
    # create objects / constants
    all_objects = []

    floor_uids = input_dictionary['floor_uids']
    room_uids_per_floor = input_dictionary['room_uids_per_floor']
    elevator_uids = input_dictionary['elevator_uids']
    sensor_room_mapping = input_dictionary['sensor_room_mapping']
    actuator_room_mapping = input_dictionary['actuator_room_mapping']
    cleaning_team_uids = input_dictionary['cleaning_team_uids']
    room_positions_uids = input_dictionary['names_room_positions']
    sensor_types = input_dictionary['sensor_types']
    assert 1 <= len(elevator_uids)

    floors, rooms, elevators, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, uid_to_pddl_variable_elevators = create_objects_room_topology(floor_uids, room_uids_per_floor, elevator_uids)
    all_objects = all_objects + floors + rooms + elevators

    cleaning_teams = create_objects(cleaning_team_uids, "cleaning_team")
    uid_to_pddl_variable_cleaning_teams = {cleaning_team_uids[i]:cleaning_teams[i] for i in range(len(cleaning_team_uids))}
    all_objects = all_objects + cleaning_teams

    sensors, actuators, uid_to_pddl_variable_sensors, uid_to_pddl_variable_actuators = create_sensors_and_actuators(floor_uids, room_uids_per_floor, sensor_room_mapping, actuator_room_mapping, sensor_types)
    all_objects = all_objects + sensors + actuators

    room_positions = create_objects(room_positions_uids, "room_position")
    uid_to_pddl_variable_room_positions = {room_positions_uids[i]:room_positions[i] for i in range(len(room_positions_uids))}
    all_objects = all_objects + room_positions

    return all_objects, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, uid_to_pddl_variable_sensors,uid_to_pddl_variable_actuators, uid_to_pddl_variable_elevators, uid_to_pddl_variable_cleaning_teams, uid_to_pddl_variable_room_positions
