#!/usr/bin/env python
"""Module generates pddl domain and problem files."""

# pip install pddl==0.4.3
from typing import List, Dict
from pddl.logic import variables
from pddl.core import Domain, Problem
from pddl.requirements import Requirements

import pddl_converter_actions
import pddl_converter_goals
import pddl_converter_types
import pddl_converter_predicates
import pddl_converter_objects
import pddl_converter_input
import pddl_converter_initial_state
import pddl_converter_help


def create_domain(domain_name: str, predicates_dict: Dict[str,variables], pddl_variable_types: Dict[str,List[variables]], activity_mapping):
    # set up types
    type_dict = pddl_converter_types.create_type_dict()

    # define actions
    actions_list = []
    actions_list = actions_list + pddl_converter_actions.create_cleaning_actions(predicates_dict, pddl_variable_types)
    actions_list = actions_list + pddl_converter_actions.create_assign_actions(predicates_dict, pddl_variable_types)
    actions_list = actions_list + pddl_converter_actions.create_actuator_actions(predicates_dict, pddl_variable_types)
    actions_list = actions_list + pddl_converter_actions.create_activity_detection_actions(predicates_dict, pddl_variable_types)
    actions_list = actions_list + pddl_converter_actions.create_activity_fulfilled_actions(predicates_dict, pddl_variable_types, activity_mapping)
    actions_list = actions_list + pddl_converter_actions.create_energy_saving_actions(predicates_dict, pddl_variable_types)

    # define the domain object.
    requirements = [Requirements.STRIPS, Requirements.TYPING, Requirements.ADL]
    domain = Domain(domain_name,
                    requirements=requirements,
                    types=type_dict,
                    predicates=list(predicates_dict.values()),
                    actions=actions_list)

    #print(domain)
    return domain

def create():
    input_dictionary = pddl_converter_input.query_input()

    # set up variables and constants
    pddl_variable_types = pddl_converter_types.create_type_variables()

    activity_mapping: Dict[str,Dict[str,str]] = input_dictionary['activity_mapping']

    predicates_dict = pddl_converter_predicates.create_predicates_variables(pddl_variable_types, activity_mapping.keys())

    domain = create_domain(input_dictionary['domain_name'], predicates_dict, pddl_variable_types, activity_mapping)

    floor_uids = input_dictionary['floor_uids']
    room_uids_per_floor = input_dictionary['room_uids_per_floor']
    elevator_uids = input_dictionary['elevator_uids']
    assert 1 <= len(elevator_uids)

    sensor_room_mapping = input_dictionary['sensor_room_mapping']
    actuator_room_mapping = input_dictionary['actuator_room_mapping']

    actuator_increases_sensor_mapping_matrix = input_dictionary['actuator_increases_sensor_mapping_matrix']
    actuator_decreases_sensor_mapping_matrix = input_dictionary['actuator_decreases_sensor_mapping_matrix']

    sensor_types = input_dictionary['sensor_types']

    sensor_initial_values = input_dictionary['sensor_initial_values']
    # TODO
    sensor_goal_values = input_dictionary['sensor_goal_values']
    sensor_initial_locked = input_dictionary['sensor_initial_locked']
    actuator_initial_values = input_dictionary['actuator_initial_values']
    room_occupied_actuator_initial_values = input_dictionary['room_occupied_actuator_initial_values']

    all_objects, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, uid_to_pddl_variable_sensors,uid_to_pddl_variable_actuators, uid_to_pddl_variable_elevators, uid_to_pddl_variable_cleaning_teams, uid_to_pddl_variable_room_positions = pddl_converter_objects.create_all_obbjects(floor_uids, room_uids_per_floor, elevator_uids, sensor_room_mapping, actuator_room_mapping, input_dictionary['cleaning_team_uids'], input_dictionary['names_room_positions'], sensor_types)

    # create initial state
    initial_state = []

    initial_state = initial_state + pddl_converter_initial_state.create_initial_state_room_topology(predicates_dict, floor_uids, room_uids_per_floor, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms)
    initial_state = initial_state + pddl_converter_initial_state.create_initial_state_elevator_topology(predicates_dict, floor_uids, room_uids_per_floor, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, uid_to_pddl_variable_elevators, uid_to_pddl_variable_room_positions)

    initial_state = initial_state + pddl_converter_initial_state.create_cleaning_teams_starting_position(predicates_dict, uid_to_pddl_variable_cleaning_teams, uid_to_pddl_variable_elevators)

    sensor_is_part_of_room = predicates_dict["sensor_is_part_of_room"]
    initial_state = initial_state + pddl_converter_initial_state.create_iot_room_mapping(floor_uids, room_uids_per_floor, uid_to_pddl_variable_sensors, uid_to_pddl_variable_rooms, sensor_room_mapping, sensor_is_part_of_room)
    actuator_is_part_of_room = predicates_dict["actuator_is_part_of_room"]
    initial_state = initial_state + pddl_converter_initial_state.create_iot_room_mapping(floor_uids, room_uids_per_floor, uid_to_pddl_variable_actuators, uid_to_pddl_variable_rooms, actuator_room_mapping, actuator_is_part_of_room)

    initial_state = initial_state + pddl_converter_initial_state.create_iot_position_mapping(predicates_dict, uid_to_pddl_variable_room_positions, uid_to_pddl_variable_sensors, uid_to_pddl_variable_actuators)

    initial_state = initial_state + pddl_converter_initial_state.create_iot_influences_iot_mapping(predicates_dict, actuator_increases_sensor_mapping_matrix, actuator_decreases_sensor_mapping_matrix, uid_to_pddl_variable_actuators, uid_to_pddl_variable_sensors)

    # context
    # raw sensor data
    assert len(sensor_initial_values) <= len(uid_to_pddl_variable_sensors)
    assert len(sensor_goal_values) <= len(uid_to_pddl_variable_sensors)
    assert len(actuator_initial_values) <= len(uid_to_pddl_variable_actuators)

    initial_state = initial_state + pddl_converter_initial_state.create_sensor_values(predicates_dict, floor_uids, room_uids_per_floor, sensor_room_mapping, uid_to_pddl_variable_sensors, sensor_initial_values)
    initial_state = initial_state + pddl_converter_initial_state.create_sensor_locks(predicates_dict, sensor_initial_locked, uid_to_pddl_variable_sensors)
    individual_sensor_goals = pddl_converter_initial_state.create_sensor_values(predicates_dict, floor_uids, room_uids_per_floor, sensor_room_mapping, uid_to_pddl_variable_sensors, sensor_goal_values)
    initial_state = initial_state + pddl_converter_initial_state.create_actuator_values(predicates_dict, floor_uids, room_uids_per_floor, actuator_room_mapping, uid_to_pddl_variable_actuators, actuator_initial_values)

    # context room occupied
    assert len(room_occupied_actuator_initial_values) <= len(uid_to_pddl_variable_rooms)
    initial_state = initial_state + pddl_converter_initial_state.create_room_occupied_values(predicates_dict, room_occupied_actuator_initial_values, floor_uids, room_uids_per_floor, uid_to_pddl_variable_rooms)

    # create goal
    goal_state = pddl_converter_goals.create_goal(predicates_dict, pddl_variable_types, input_dictionary['sensor_goal_state_mapping'], input_dictionary['plan_cleaning'])

    # define the problem object.
    problem = Problem(
        input_dictionary['problem_name'],
        domain=domain,
        requirements=domain.requirements,
        objects=all_objects,
        init=initial_state,
        goal=goal_state
    )
    #print(problem)

    return domain, problem

def main():
    pddl_converter_help.check_lib_versions()

    # output_path is relative to working directory
    output_path = "auto_generated/"
    domaine_file_name = 'test_domain'
    problem_file_name = 'test_problem'

    d, p = create()

    pddl_converter_help.write_out_pddl(output_path, domaine_file_name + ".pddl", d)
    pddl_converter_help.write_out_pddl(output_path, problem_file_name + ".pddl", p)
    #json_text = '{"excludeActions": []}'
    json_text = '{"excludeActions": ["detect_all_activitys","fulfill_all_activitys","detect_no_possible_activity_sleep","detect_no_possible_activity_read","fulfill_activity_no_sleep","fulfill_activity_no_read"]}'
    pddl_converter_help.write_out_pddl_visualisation_hints(output_path, domaine_file_name + ".planviz.json", json_text)

if __name__ == '__main__':
    main()
