#!/usr/bin/env python

# pip install pddl==0.4.3
from typing import Dict, List
from pddl.logic import constants
import pddl_converter_help

def create_objects(name_list: List[str], type_name: str):
    names = ''
    for i in range(len(name_list)):
        names = names + str(f'{type_name}_{name_list[i]} ')

    objects = constants(names, type_=type_name + '_type')
    #print (objects)
    return objects

def create_objects_room_topology(floor_uids: List[str], room_uids_per_floor: Dict[str,List[str]], elevator_uids: List[str]):
    floors = create_objects(floor_uids, "floor")
    uid_to_pddl_variable_floor = {floor_uids[i]:floors[i] for i in range(len(floors))}
    rooms = []
    uid_to_pddl_variable_rooms = {}
    for _, room_uids in room_uids_per_floor.items():
        new_rooms = create_objects(room_uids, "room")
        rooms = rooms + new_rooms
        uid_to_pddl_variable_rooms.update({room_uids[i]:new_rooms[i] for i in range(len(new_rooms))})
    elevators = create_objects(elevator_uids, "room")

    return floors, rooms, elevators, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms

def create_sensors_and_actuators(floor_uids, room_uids_per_floor, sensor_room_mapping, actuator_room_mapping):
    sensors = []
    uid_to_pddl_variable_sensors = {}
    for room in pddl_converter_help.iterator_ofer_dict_list_elements(floor_uids,room_uids_per_floor):
        if room not in sensor_room_mapping:
            continue
        new_sensors = create_objects(sensor_room_mapping[room], "numerical_s")
        sensors = sensors + new_sensors
        uid_to_pddl_variable_sensors.update({sensor_room_mapping[room][i]:new_sensors[i] for i in range(len(new_sensors))})

    actuators = []
    uid_to_pddl_variable_actuators = {}
    for room in pddl_converter_help.iterator_ofer_dict_list_elements(floor_uids,room_uids_per_floor):
        if room not in actuator_room_mapping:
            continue
        new_actuators = create_objects(actuator_room_mapping[room], "actuator")
        actuators = actuators + new_actuators
        uid_to_pddl_variable_actuators.update({actuator_room_mapping[room][i]:new_actuators[i] for i in range(len(new_actuators))})
    return sensors, actuators, uid_to_pddl_variable_sensors, uid_to_pddl_variable_actuators
