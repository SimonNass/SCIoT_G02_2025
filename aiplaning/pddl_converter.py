#!/usr/bin/env python

# pip install pddl==0.4.3
from typing import Any, Dict, List
from pddl.logic import Predicate, constants, variables, base
from pddl.core import Domain, Problem
from pddl.requirements import Requirements
from pddl import parse_domain, parse_problem
import os

import pddl_converter_actions
import pddl_converter_goals
import pddl_converter_types
import pddl_converter_predicates
import pddl_converter_objects
import pddl_converter_input

def iterator_rooms_per_floor(floor_uids: List[str], room_uids_per_floor: Dict[str,List[str]]):
    for floor in floor_uids:
        for room in room_uids_per_floor[floor]:
            yield room

def create_objects(name_list: List[str], type_name: str):
    names = ''
    for i in range(len(name_list)):
        names = names + str(f'{type_name}_{name_list[i]} ')

    objects = constants(names, type_=type_name + '_type')
    #print (objects)
    return objects

def create_initial_state_room_topology(floor_uids, room_uids_per_floor, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, elevators):
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
    
    for room in iterator_rooms_per_floor(floor_uids,room_uids_per_floor):
        sensor_room = uids_to_room[room]
        if room not in room_mapping:
            continue
        for device in room_mapping[room]:
            object_instance = uids_to_object[device]
            next_part_of_room = iot_is_part_of_room(object_instance, sensor_room)
            initial_state.append(next_part_of_room)

    return initial_state

def create_sensor_values(floor_uids: List[str], room_uids_per_floor:Dict[str,List[str]], sensor_room_mapping:Dict[str,List[str]], uid_to_pddl_variable_sensors: Dict[str,constants], sensor_initial_values: List[int]):
    state_list = []

    for room in iterator_rooms_per_floor(floor_uids,room_uids_per_floor):
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

def create_objects_and_initial_state(input: Dict[str,Any]):
        # create objects / constants
    all_objects = []

    floor_uids = input['floor_uids']
    room_uids_per_floor = input['room_uids_per_floor']
    elevator_uids = input['elevator_uids']
    assert 1 <= len(elevator_uids)

    sensor_room_mapping = input['sensor_room_mapping']
    actuator_room_mapping = input['actuator_room_mapping']
    cleaning_team_uids = input['cleaning_team_uids']
    names_room_positions = input['names_room_positions']
    
    floors, rooms, elevators, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms = pddl_converter_objects.create_objects_room_topology(floor_uids, room_uids_per_floor, elevator_uids)
    all_objects = all_objects + floors + rooms + elevators

    cleaning_teams = create_objects(cleaning_team_uids, "cleaning_team")
    all_objects = all_objects + cleaning_teams

    sensors, actuators, uid_to_pddl_variable_sensors, uid_to_pddl_variable_actuators = pddl_converter_objects.create_sensors_and_actuators(floor_uids, room_uids_per_floor, sensor_room_mapping, actuator_room_mapping)
    all_objects = all_objects + sensors + actuators

    room_positions = create_objects(names_room_positions, "room_position")
    all_objects = all_objects + room_positions

    # create initial state
    initial_state = []
    
    initial_state_topology = create_initial_state_room_topology(floor_uids, room_uids_per_floor, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, elevators,)
    initial_state = initial_state + initial_state_topology

    # cleaning teams starting at different elevators
    for i in range(len(cleaning_teams)):
        next_is_at = is_at(cleaning_teams[i], elevators[i % len(elevators)])
        initial_state.append(next_is_at)

    # iot to room papping
    sm = create_iot_room_mapping(floor_uids, room_uids_per_floor, uid_to_pddl_variable_sensors, uid_to_pddl_variable_rooms, sensor_room_mapping, sensor_is_part_of_room)
    initial_state = initial_state + sm
    am = create_iot_room_mapping(floor_uids, room_uids_per_floor, uid_to_pddl_variable_actuators, uid_to_pddl_variable_rooms, actuator_room_mapping, actuator_is_part_of_room)
    initial_state = initial_state + am

    # iot position mapping
    # TODO
    room_positions_default = room_positions[0]
    for sensor_object in sensors:
        next_pos = positioned_at(sensor_object, room_positions_default)
        initial_state.append(next_pos)

    for actuator_object in actuators:
        next_pos = positioned_at(actuator_object, room_positions_default)
        initial_state.append(next_pos)

    # sensor actuator mapping
    actuator_increases_sensor_mapping_matrix = input['actuator_increases_sensor_mapping_matrix']
    actuator_decreases_sensor_mapping_matrix = input['actuator_decreases_sensor_mapping_matrix']

    assert len(actuator_increases_sensor_mapping_matrix.keys()) <= len(actuators)
    for _, sensor_list_mapping in actuator_increases_sensor_mapping_matrix.items():
        assert len(sensor_list_mapping) <= len(sensors)
    assert len(actuator_decreases_sensor_mapping_matrix.keys()) <= len(actuators)
    for _, sensor_list_mapping in actuator_decreases_sensor_mapping_matrix.items():
        assert len(sensor_list_mapping) <= len(sensors)

    for a, s_list in actuator_increases_sensor_mapping_matrix.items():
        for s in s_list:
            next_influence = actuator_increases_sensor(uid_to_pddl_variable_actuators[a], uid_to_pddl_variable_sensors[s])
            initial_state.append(next_influence)
    for a, s_list in actuator_decreases_sensor_mapping_matrix.items():
        for s in s_list:
            next_influence = actuator_decreases_sensor(uid_to_pddl_variable_actuators[a], uid_to_pddl_variable_sensors[s])
            initial_state.append(next_influence)

    # context
    # raw sensor data
    sensor_initial_values = input['sensor_initial_values']
    # TODO
    sensor_goal_values = input['sensor_goal_values']
    actuator_initial_values = input['actuator_initial_values']

    individual_sensor_goals = []

    assert len(sensor_initial_values) <= len(sensors)
    assert len(sensor_goal_values) <= len(sensors)
    assert len(actuator_initial_values) <= len(actuators)

    initial_sensor_state = create_sensor_values(floor_uids, room_uids_per_floor, sensor_room_mapping, uid_to_pddl_variable_sensors, sensor_initial_values)
    initial_state = initial_state + initial_sensor_state

    individual_sensor_goals = create_sensor_values(floor_uids, room_uids_per_floor, sensor_room_mapping, uid_to_pddl_variable_sensors, sensor_goal_values)

    for room in iterator_rooms_per_floor(floor_uids,room_uids_per_floor):
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

    # context room occupied
    room_occupied_actuator_initial_values = input['room_occupied_actuator_initial_values']

    assert len(room_occupied_actuator_initial_values) <= len(rooms)

    for room in iterator_rooms_per_floor(floor_uids,room_uids_per_floor):
        object_state = room_occupied_actuator_initial_values[room]
        state = base.Not(is_occupied(rooms[i]))
        if object_state:
            state = is_occupied(rooms[i])
        else:
            state = base.Not(is_occupied(rooms[i]))
        initial_state.append(state)
    return all_objects, initial_state, individual_sensor_goals

def create_domain(domain_name: str, predicates_list: List[variables]):
    # set up types
    type_dict = pddl_converter_types.create_type_dict()

    # define actions
    actions_list = []
    actions_list = actions_list + pddl_converter_actions.create_cleaning_actions(is_cleaned, will_become_occupied, is_occupied, is_at, is_next_to, room_is_part_of_floor, cleaning_team_type, room_type, room2_type, room3_type, floor_type, floor2_type)
    actions_list = actions_list + pddl_converter_actions.create_assign_actions(positioned_at, room_is_part_of_floor, iot_type, room_position_type, room_type, floor_type, floor2_type)
    actions_list = actions_list + pddl_converter_actions.create_actuator_actions(fulfilled_activity, is_activated, is_high, is_ok, is_low, is_sensing, positioned_at, actuator_decreases_sensor, actuator_increases_sensor, sensor_is_part_of_room, sensor_type, actuator_type, room_position_type, room_type)
    actions_list = actions_list + pddl_converter_actions.create_activity_actions(fulfilled_activity, is_doing_activitys_at, has_specified_activity_at, positioned_at, sensor_is_part_of_room, sensor_type, room_position_type, room_type)
    actions_list = actions_list + pddl_converter_actions.create_energy_saving_actions(is_activated, will_become_occupied, is_occupied, actuator_decreases_sensor, actuator_increases_sensor, actuator_is_part_of_room, sensor_is_part_of_room, sensor_type, actuator_type, actuator2_type, room_type)

    # define the domain object.
    requirements = [Requirements.STRIPS, Requirements.TYPING, Requirements.ADL]
    domain = Domain(domain_name,
                    requirements=requirements,
                    types=type_dict,
                    predicates=predicates_list,
                    actions=actions_list)

    #print(domain)

    return domain

def create():

    input = pddl_converter_input.query_input()

    # set up variables and constants
    global floor_type, floor2_type, room_type, room2_type, room3_type, room_position_type
    global iot_type, cleaning_team_type, sensor_type, actuator_type, actuator2_type
    global binary_s_type, numerical_s_type, textual_s_type, binary_a_type, numerical_a_type, textual_a_type

    floor_type, floor2_type, room_type, room2_type, room3_type, room_position_type, iot_type, cleaning_team_type, sensor_type, actuator_type, actuator2_type, binary_s_type, numerical_s_type, textual_s_type, binary_a_type, numerical_a_type, textual_a_type = pddl_converter_types.create_type_variables()

    global room_is_part_of_floor, sensor_is_part_of_room, actuator_is_part_of_room, positioned_at, actuator_increases_sensor, actuator_decreases_sensor, is_next_to, is_at, is_occupied, will_become_occupied, is_cleaned, has_specified_activity_at, activity_names, is_doing_activitys_at
    global is_sensing, is_low, is_ok, is_high, is_activated
    global fulfilled_activity

    predicates_list, room_is_part_of_floor, sensor_is_part_of_room, actuator_is_part_of_room, positioned_at, actuator_increases_sensor, actuator_decreases_sensor, is_next_to, is_at, is_occupied, will_become_occupied, is_cleaned, has_specified_activity_at, activity_names, is_doing_activitys_at, is_sensing, is_low, is_ok, is_high, is_activated, fulfilled_activity = pddl_converter_predicates.create_predicates_variables(floor_type, room_type, room2_type, room_position_type, cleaning_team_type, iot_type, sensor_type, actuator_type, numerical_s_type)

    domain = create_domain(input['domain_name'], predicates_list)

    all_objects, initial_state, individual_sensor_goals = create_objects_and_initial_state(input)

    # create goal
    goal_state = None
    goal_state = pddl_converter_goals.create_goal(fulfilled_activity, is_activated, is_cleaned, is_occupied, actuator_is_part_of_room, room_type, room_position_type, actuator_type, input['plan_cleaning'])

    problem = Problem(
        input['problem_name'],
        domain=domain,
        requirements=domain.requirements,
        
        objects=all_objects,
        init=initial_state,
        goal=goal_state
    )
    
    #print(problem)
    return domain, problem

def reading_in_pddl():
    domaine_file_name = 'domain.pddl'
    problem_file_name = 'problem.pddl'

    domain = parse_domain(domaine_file_name)
    print(domain)
    problem = parse_problem(problem_file_name)
    print(problem)

def check_lib_versions():
    import pddl
    version_pddl = pddl.__version__
    print(version_pddl)
    # make sure that it is above 0.4.2

def main():
    check_lib_versions()

    # output_path is relative to working directory
    output_path = "auto_generated/"
    os.makedirs(output_path, exist_ok=True)
    domaine_file_name = 'test_domain.pddl'
    problem_file_name = 'test_problem.pddl'

    d, p = create()
    
    with open(os.path.join(output_path, domaine_file_name),'w') as f:
        f.write(d.__str__())
    
    with open(os.path.join(output_path, problem_file_name),'w') as f:
        f.write(p.__str__())

if __name__ == '__main__':
    main()
