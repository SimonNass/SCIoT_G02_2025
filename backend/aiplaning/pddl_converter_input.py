#!/usr/bin/env python
"""Module specifies the data input to generate the pddl domain and problem based on the data in the backend DB."""

import logging
import json
import os
import configparser
from backend.aiplaning.utils.dbUtils import get_floor_uids, get_room_uids_per_floor, get_room_occupied_initial_values, get_sensor_room_mapping, get_actuator_room_mapping, get_sensor_types, get_sensor_initial_values, get_actuator_initial_values
from backend.mqtt.utils.mappingParserUtils import get_actuator_sensor_matrices
from typing import List, Dict, Optional

def query_input_over_db(sensor_goal_values: Optional[Dict[str, int]] = {}, sensor_initial_locked: Optional[List[str]] = [], room_number: str = None, plan_cleaning: bool = False, plan_activitys: bool = True):
    domain_name = "test_SCIoT_G02_2025"
    problem_name = 'test'
    output_path = 'auto_generated/'
    domaine_file_name = 'test_domain'
    problem_file_name = 'test_problem'

    # floor_uids = ['f0','f1']
    floor_uids = get_floor_uids(room_number)
    # room_uids_per_floor = {'f0':['r0','r1','r3'],'f1':['r2']}
    room_uids_per_floor = get_room_uids_per_floor(room_number)
    
    # TODO what if sensor with room is not part of anny floor?
    # room_occupied_initial_values = {'r0':False, 'r1': True, 'r2':False, 'r3': True}
    room_occupied_initial_values = get_room_occupied_initial_values(room_number)
    #floor_list = db.list_all_floors()
    #floor_uids = [floor['id'] for floor in floor_list]
    #room_uids_per_floor = {floor['id']:floor['rooms'] for floor in floor_list}
    #for floor in floor_list:
    #    room_occupied_initial_values = {room['id']:room['is_occupied'] for room in room_uids_per_floor[floor]}

    # sensor_room_mapping = {'r0':['s1'], 'r2':['s2'], 'r3':['s3', 's4']}
    # actuator_room_mapping = {'r0':['a1'], 'r2':['a2']}
    sensor_room_mapping = get_sensor_room_mapping(room_number)
    logging.info(f"sensor_room_mapping: {sensor_room_mapping}")
    actuator_room_mapping = get_actuator_room_mapping(room_number)
    logging.info(f"actuator_room_mapping: {actuator_room_mapping}")
    #for floor in floor_uids:
    #    for room in room_uids_per_floor[floor]:
    #        device_list = db.list_devices_in_room(floor,room)['devices']
    #        sensor_uids = []
    #        actuator_uids = []
    #        for device in device_list:
    #            if device is_sensor():
    #                sensor_uids.append(device)
    #            elif device is_actuator():
    #                actuator_uids.append(device)
    #        sensor_room_mapping.update({room:sensor_uids})
    #        actuator_room_mapping.update({room:actuator_uids})

    # sensor_types = {'s1':'light_s', 's2':'humidity_s', 's3':'temperature_s', 's4':'temperature_s'}
    sensor_types = get_sensor_types(room_number)

    # TODO get info from db
    # actuator_increases_sensor_mapping_matrix = {'a1':['s1','s2'], 'a2':['s2']}
    # actuator_decreases_sensor_mapping_matrix = {'a1':['s1']}
    actuator_increases_sensor_mapping_matrix, actuator_decreases_sensor_mapping_matrix = get_actuator_sensor_matrices(None, room_number)
    logging.info(f"actuator_increases_sensor_mapping_matrix: {actuator_increases_sensor_mapping_matrix}")
    logging.info(f"actuator_decreases_sensor_mapping_matrix: {actuator_decreases_sensor_mapping_matrix}")

    # sensor_initial_values = {'s1': -1, 's2':1, 's3':-1}
    sensor_initial_values = get_sensor_initial_values(room_number)
    logging.info(f"sensor_initial_values: {sensor_initial_values}")
    # sensor_goal_values = {'s1': -1, 's2':1}

    # actuator_initial_values = {'a1': True, 'a2':False}
    actuator_initial_values = get_actuator_initial_values(room_number)
    logging.info(f"actuator_initial_values: {actuator_initial_values}")
    #for floor in floor_uids:
    #    for room in room_uids_per_floor[floor]:
    #        for device in sensor_room_mapping[room]:
    #            curent_value = db.request_current_value_hierarchical(floor,room,device)
    #            sensor_initial_values.update({device:curent_value})
    #        for device in actuator_room_mapping[room]:
    #            curent_value = db.request_current_value_hierarchical(floor,room,device)
    #            sensor_initial_values.update({device:curent_value})

    # potential to make stuff unchangable for the ai as long as the room is occupied
    # sensor_initial_locked = ['s4']

    # below this not set by db use these hardcoded ones for now
    elevator_uids = ['e0','e1']
    cleaning_team_uids = ['cleaning_team_1','cleaning_team_2']
    names_room_positions = ['overall_room']
    #['overall_room', 'bed', 'closet', 'window']

    use_defoult_sensor_goals = True
    use_activity_sensor_goals = True

    sensor_goal_state_mapping = {}
    if use_defoult_sensor_goals:
        sensor_goal_state_mapping = {"temperature_s":"is_ok",
                                    "humidity_s":"is_ok",
                                    #"window_rotation_s":"is_low",
                                    "light_s":"is_high",
                                    "TV_volume_s":"is_ok",
                                    "sound_s":"is_ok"}

    # TODO make 'requests_service':{'button_s':'is_sensing' -> request text displayed
    # TODO in r_dress > assign_lock_for_sensor TV_volume_s_s6_TV_volume_s
    # TODO activity sleep do the blinds not work decrease mapping
    activity_detect_mapping = {}
    activity_fulfill_mapping = {}
    if use_activity_sensor_goals:
        activity_detect_mapping = {"read":{"chair_s":"is_sensing", "power_consumption_s":"is_low"},
                                    "button_pressed":{"button_s":"is_sensing", "chair_s":"~is_sensing", "bed_s":"is_sensing", "TV_volume_s":"~is_high"},
                                    "on_the_phone":{"chair_s":"is_sensing", "power_consumption_s":"is_ok"},
                                    "work":{"chair_s":"is_sensing", "power_consumption_s":"is_high", "bed_s":"~is_sensing"},
                                    "sleep":{"bed_s":"is_sensing", "button_s":"~is_sensing", "TV_volume_s":"~is_high"},
                                    "bath":{"shower_s":"is_sensing", "chair_s":"~is_sensing", "bed_s":"~is_sensing"},
                                    "dress":{"chair_s":"~is_sensing", "bed_s":"~is_sensing", "shower_s":"~is_sensing", "motion_s":"is_sensing"},
                                    "watch_TV":{"TV_volume_s":"is_high", "button_s":"~is_sensing", "bed_s":"is_sensing"}}
        activity_fulfill_mapping = {"read":{"temperature_s":"is_ok", "light_s":"is_high", "sound_s":"is_ok"},
                                    "button_pressed":{"light_s":"is_high", "light_s":"is_high"},
                                    "on_the_phone":{"light_s":"is_high", "sound_s":"is_low"},
                                    "work":{"light_s":"is_high", "sound_s":"is_ok"},
                                    "sleep":{"light_s":"is_low", "sound_s":"is_low"},
                                    "bath":{"temperature_s":"is_high", "humidity_s":"is_low"},
                                    #"bath":{"light_s":"is_ok", "temperature_s":"is_high", "humidity_s":"is_low"}, # TODO not working r_bath with lights inittial 1
                                    "dress":{"light_s":"is_ok"},
                                    "watch_TV":{"light_s":"is_ok", "TV_volume_s":"is_high", "sound_s":"is_high"}}


    return {'domain_name':domain_name,
            'problem_name':problem_name,
            'output_path':output_path,
            'domaine_file_name':domaine_file_name,
            'problem_file_name':problem_file_name,

            'plan_cleaning': plan_cleaning,
            'plan_activitys': plan_activitys,

            'floor_uids':floor_uids,
            'room_uids_per_floor':room_uids_per_floor,
            'elevator_uids':elevator_uids,

            'cleaning_team_uids':cleaning_team_uids,
            'names_room_positions':names_room_positions,

            'sensor_room_mapping':sensor_room_mapping,
            'actuator_room_mapping':actuator_room_mapping,

            'sensor_types':sensor_types,

            'actuator_increases_sensor_mapping_matrix':actuator_increases_sensor_mapping_matrix,
            'actuator_decreases_sensor_mapping_matrix':actuator_decreases_sensor_mapping_matrix,

            'sensor_initial_values':sensor_initial_values,
            'sensor_initial_locked':sensor_initial_locked,
            'sensor_goal_values':sensor_goal_values,
            'actuator_initial_values':actuator_initial_values,

            'room_occupied_initial_values':room_occupied_initial_values,

            'activity_detect_mapping':activity_detect_mapping,
            'activity_fulfill_mapping':activity_fulfill_mapping,
            'sensor_goal_state_mapping':sensor_goal_state_mapping,
            }

def query_input_over_config_file(config_file_name: os.path = "aiplaning/config/ai_planer_test_example.ini"):

    print (f"reading in {config_file_name}", flush=True)
    try:
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_file_name, encoding='utf-8')
    except Exception as e:
        print(e)

    # General
    _ = int(config.get('General', 'version', fallback=0))
    domain_name = str(config.get('General', 'domain_name', fallback="test_SCIoT_G02_2025"))
    problem_name = str(config.get('General', 'problem_name', fallback="test"))
    output_path = str(config.get('General', 'output_path', fallback="auto_generated/"))
    domaine_file_name = str(config.get('General', 'domaine_file_name', fallback="test_domain"))
    problem_file_name = str(config.get('General', 'problem_file_name', fallback="test_problem"))
    plan_cleaning = bool(config.get('General', 'plan_cleaning', fallback=True) in [True, 'True'])
    plan_activitys = bool(config.get('General', 'plan_activitys', fallback=True) in [True, 'True'])

    # Topology
    floor_uids = json.loads(config.get('Topology', 'floor_uids', fallback='[]'))
    room_uids_per_floor = json.loads(config.get('Topology', 'room_uids_per_floor', fallback='{}'))
    # TODO what if sensor with room is not part of anny floor?
    room_occupied_initial_values = {key:bool(value in [True, 'True']) for key,value in json.loads(config.get('Topology', 'room_occupied_initial_values', fallback='{}')).items()}
    elevator_uids = json.loads(config.get('Topology', 'elevator_uids', fallback='[]'))
    names_room_positions = json.loads(config.get('Topology', 'names_room_positions', fallback='[]'))
    sensor_room_mapping = json.loads(config.get('Topology', 'sensor_room_mapping', fallback='{}'))
    actuator_room_mapping = json.loads(config.get('Topology', 'actuator_room_mapping', fallback='{}'))
    cleaning_team_uids = json.loads(config.get('Topology', 'cleaning_team_uids', fallback='[]'))

    # IoT
    sensor_types = json.loads(config.get('IoT', 'sensor_types', fallback='{}'))
    actuator_increases_sensor_mapping_matrix = json.loads(config.get('IoT', 'actuator_increases_sensor_mapping_matrix', fallback='{}'))
    actuator_decreases_sensor_mapping_matrix = json.loads(config.get('IoT', 'actuator_decreases_sensor_mapping_matrix', fallback='{}'))
    sensor_initial_values = {key:int(value) for key,value in json.loads(config.get('IoT', 'sensor_initial_values', fallback='{}')).items()}
    sensor_goal_values = {key:int(value) for key,value in json.loads(config.get('IoT', 'sensor_goal_values', fallback='{}')).items()}
    actuator_initial_values = {key:bool(value in [True, 'True']) for key,value in json.loads(config.get('IoT', 'actuator_initial_values', fallback='{}')).items()}
    sensor_initial_locked = json.loads(config.get('IoT', 'sensor_initial_locked', fallback='[]'))
    sensor_goal_state_mapping = json.loads(config.get('IoT', 'sensor_goal_state_mapping', fallback='{}'))

    # Activity
    # TODO make 'requests_service':{'button_s':'is_sensing' -> request text displayed
    # TODO fine tune sensor ideal position for the activitys
    activity_detect_mapping = json.loads(config.get('Activity', 'activity_detect_mapping', fallback='{}'))
    activity_fulfill_mapping = json.loads(config.get('Activity', 'activity_fulfill_mapping', fallback='{}'))

    input_dictionary =  {'domain_name':domain_name,
            'problem_name':problem_name,
            'output_path':output_path,
            'domaine_file_name':domaine_file_name,
            'problem_file_name':problem_file_name,

            'plan_cleaning':plan_cleaning,
            'plan_activitys':plan_activitys,

            'floor_uids':floor_uids,
            'room_uids_per_floor':room_uids_per_floor,
            'elevator_uids':elevator_uids,

            'cleaning_team_uids':cleaning_team_uids,
            'names_room_positions':names_room_positions,

            'sensor_room_mapping':sensor_room_mapping,
            'actuator_room_mapping':actuator_room_mapping,

            'sensor_types':sensor_types,

            'actuator_increases_sensor_mapping_matrix':actuator_increases_sensor_mapping_matrix,
            'actuator_decreases_sensor_mapping_matrix':actuator_decreases_sensor_mapping_matrix,

            'sensor_initial_values':sensor_initial_values,
            'sensor_initial_locked':sensor_initial_locked,
            'sensor_goal_values':sensor_goal_values,
            'actuator_initial_values':actuator_initial_values,

            'room_occupied_initial_values':room_occupied_initial_values,

            'activity_detect_mapping':activity_detect_mapping,
            'activity_fulfill_mapping':activity_fulfill_mapping,
            'sensor_goal_state_mapping':sensor_goal_state_mapping,
            }
    #print (input_dictionary)
    return input_dictionary

def query_input(over_config_file: bool = False, config_file_name: os.path = ''):
    if over_config_file:
        input_dictionary = query_input_over_config_file(config_file_name)
    else:
        input_dictionary = query_input_over_db()
    return input_dictionary

# input_dictionary desctiption
#   {'domain_name':domain_name, > str
#   'problem_name':problem_name, > str
#   'output_path':output_path, > str
#   'domaine_file_name':domaine_file_name, > str
#   'problem_file_name':problem_file_name, > str
#   'plan_cleaning':False, > bool
#   'plan_activitys':False, > bool
#   'floor_uids':floor_uids, > List[uuid as str]
#   'room_uids_per_floor':room_uids_per_floor, > Dict[uuid as str, List[uuid as str]]
#   'elevator_uids':elevator_uids, > List[uuid as str]
#   'cleaning_team_uids':cleaning_team_uids, > List[uuid as str]
#   'names_room_positions':names_room_positions, > List[uuid as str]
#   'sensor_room_mapping':sensor_room_mapping, > Dict[uuid as str, List[uuid as str]]
#   'actuator_room_mapping':actuator_room_mapping, > Dict[uuid as str, List[uuid as str]]
#   'sensor_types':sensor_types, > Dict[uuid as str, str]
#   'actuator_increases_sensor_mapping_matrix':actuator_increases_sensor_mapping_matrix, > Dict[uuid as str, List[uuid as str]]
#   'actuator_decreases_sensor_mapping_matrix':actuator_decreases_sensor_mapping_matrix, > Dict[uuid as str, List[uuid as str]]
#   'sensor_initial_values':sensor_initial_values, > Dict[uuid as str, simplified value]
#   'sensor_initial_locked':sensor_initial_locked, > Dict[uuid as str, bool]
#   'sensor_goal_values':sensor_goal_values, > Dict[uuid as str, simplified value]
#   'actuator_initial_values':actuator_initial_values, > Dict[uuid as str, bool]
#   'room_occupied_initial_values':room_occupied_initial_values, > Dict[uuid as str, bool]
#   'activity_detect_mapping':activity_detect_mapping, > Dict[str, Dict[str,str]]
#   'activity_fulfill_mapping':activity_fulfill_mapping, > Dict[str, Dict[str,str]]
#   'sensor_goal_state_mapping':sensor_goal_state_mapping, > Dict[str, str]
#   }
