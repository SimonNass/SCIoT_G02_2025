#!/usr/bin/env python
"""Module specifies the data input to generate the pddl domain and problem based on the data in the backend DB."""

def query_input_over_db():
    domain_name = "test_SCIoT_G02_2025"
    problem_name = 'test'

    floor_uids = ['f0','f1']
    room_uids_per_floor = {'f0':['r0','r1','r3'],'f1':['r2']}
    # TODO what if sensor with room is not part of anny floor?
    room_occupied_initial_values = {'r0':False, 'r1': True, 'r2':False, 'r3': True}
    #floor_list = db.list_all_floors()
    #floor_uids = [floor['id'] for floor in floor_list]
    #room_uids_per_floor = {floor['id']:floor['rooms'] for floor in floor_list}
    #for floor in floor_list:
    #    room_occupied_initial_values = {room['id']:room['is_occupied'] for room in room_uids_per_floor[floor]}

    elevator_uids = ['e0','e1']
    cleaning_team_uids = ['cleaning_team_1','cleaning_team_2']
    names_room_positions = ['overall_room']
    #['overall_room', 'bed', 'closet', 'window']

    sensor_room_mapping = {'r0':['s1'], 'r2':['s2'], 'r3':['s3', 's4']}
    actuator_room_mapping = {'r0':['a1'], 'r2':['a2']}
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

    sensor_types = {'s1':'light_s', 's2':'humidity_s', 's3':'temperature_s', 's4':'temperature_s'}

    # TODO get info from db
    actuator_increases_sensor_mapping_matrix = {'a1':['s1','s2'], 'a2':['s2']}
    actuator_decreases_sensor_mapping_matrix = {'a1':['s1']}

    sensor_initial_values = {'s1': -1, 's2':1, 's3':-1}
    sensor_goal_values = {'s1': -1, 's2':1}
    actuator_initial_values = {'a1': True, 'a2':False}
    #for floor in floor_uids:
    #    for room in room_uids_per_floor[floor]:
    #        for device in sensor_room_mapping[room]:
    #            curent_value = db.request_current_value_hierarchical(floor,room,device)
    #            sensor_initial_values.update({device:curent_value})
    #        for device in actuator_room_mapping[room]:
    #            curent_value = db.request_current_value_hierarchical(floor,room,device)
    #            sensor_initial_values.update({device:curent_value})

    sensor_initial_locked = ['s4']

    sensor_goal_state_mapping = {'temperature_s':'is_ok',
                                 'humidity_s':'is_ok',
                                 'window_rotation_s':'is_low',
                                 'light_s':'is_high',
                                 'sound_s':'is_ok'
                                 }

    # TODO make 'requests_service':{'button_s':'is_sensing' -> request text displayed
    # TODO fine tune sensor ideal position for the activitys
    activity_mapping = {'bath':{'temperature_s':'is_ok'},
                        'read':{'temperature_s':'is_ok', 'light_s':'is_high', 'sound_s':'is_ok'},
                        'sleep':{'light_s':'is_low', 'sound_s':'is_low'},
                        }


    return {'domain_name':domain_name,
            'problem_name':problem_name,

            'plan_cleaning':False,

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

            'activity_mapping':activity_mapping,
            'sensor_goal_state_mapping':sensor_goal_state_mapping,
            }

def query_input_over_config_file():
    domain_name = "test_SCIoT_G02_2025"
    problem_name = 'test'

    floor_uids = ['f0','f1']
    room_uids_per_floor = {'f0':['r0','r1','r3'],'f1':['r2']}
    # TODO what if sensor with room is not part of anny floor?
    room_occupied_initial_values = {'r0':False, 'r1': True, 'r2':False, 'r3': True}
    #floor_list = db.list_all_floors()
    #floor_uids = [floor['id'] for floor in floor_list]
    #room_uids_per_floor = {floor['id']:floor['rooms'] for floor in floor_list}
    #for floor in floor_list:
    #    room_occupied_initial_values = {room['id']:room['is_occupied'] for room in room_uids_per_floor[floor]}

    elevator_uids = ['e0','e1']
    cleaning_team_uids = ['cleaning_team_1','cleaning_team_2']
    names_room_positions = ['overall_room']
    #['overall_room', 'bed', 'closet', 'window']

    sensor_room_mapping = {'r0':['s1'], 'r2':['s2'], 'r3':['s3', 's4']}
    actuator_room_mapping = {'r0':['a1'], 'r2':['a2']}
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

    sensor_types = {'s1':'light_s', 's2':'humidity_s', 's3':'temperature_s', 's4':'temperature_s'}

    # TODO get info from db
    actuator_increases_sensor_mapping_matrix = {'a1':['s1','s2'], 'a2':['s2']}
    actuator_decreases_sensor_mapping_matrix = {'a1':['s1']}

    sensor_initial_values = {'s1': -1, 's2':1, 's3':-1}
    sensor_goal_values = {'s1': -1, 's2':1}
    actuator_initial_values = {'a1': True, 'a2':False}
    #for floor in floor_uids:
    #    for room in room_uids_per_floor[floor]:
    #        for device in sensor_room_mapping[room]:
    #            curent_value = db.request_current_value_hierarchical(floor,room,device)
    #            sensor_initial_values.update({device:curent_value})
    #        for device in actuator_room_mapping[room]:
    #            curent_value = db.request_current_value_hierarchical(floor,room,device)
    #            sensor_initial_values.update({device:curent_value})

    sensor_initial_locked = ['s4']

    sensor_goal_state_mapping = {'temperature_s':'is_ok',
                                 'humidity_s':'is_ok',
                                 'window_rotation_s':'is_low',
                                 'light_s':'is_high',
                                 'sound_s':'is_ok'
                                 }

    # TODO make 'requests_service':{'button_s':'is_sensing' -> request text displayed
    # TODO fine tune sensor ideal position for the activitys
    activity_mapping = {'bath':{'temperature_s':'is_ok'},
                        'read':{'temperature_s':'is_ok', 'light_s':'is_high', 'sound_s':'is_ok'},
                        'sleep':{'light_s':'is_low', 'sound_s':'is_low'},
                        }


    return {'domain_name':domain_name,
            'problem_name':problem_name,

            'plan_cleaning':False,

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

            'activity_mapping':activity_mapping,
            'sensor_goal_state_mapping':sensor_goal_state_mapping,
            }

def query_input(over_config_file: bool = False):
    if over_config_file:
        input_dictionary = query_input_over_config_file()
    else:
        input_dictionary = query_input_over_db()
    return input_dictionary

# input_dictionary desctiption
#   {'domain_name':domain_name, > str
#   'problem_name':problem_name, > str
#   'plan_cleaning':False, > bool
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
#   'activity_mapping':activity_mapping,
#   'sensor_goal_state_mapping':sensor_goal_state_mapping,
#   }
