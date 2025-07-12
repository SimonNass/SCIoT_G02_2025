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
    floor_type = pddl_variable_types["floor"][0]
    room_type = pddl_variable_types["room"][0]
    room2_type = pddl_variable_types["room"][1]
    room_position_type = pddl_variable_types["room_position"][0]
    iot_type = pddl_variable_types["iot"][0]
    cleaning_team_type = pddl_variable_types["cleaning_team"][0]
    sensor_type = pddl_variable_types["sensor"][0]
    actuator_type = pddl_variable_types["actuator"][0]
    numerical_s_type = pddl_variable_types["numerical_s"][0]

    predicates_dict, activity_names, is_doing_activitys_at, checked_activity_x, fulfilled_activity_x = pddl_converter_predicates.create_predicates_variables(floor_type, room_type, room2_type, room_position_type, cleaning_team_type, iot_type, sensor_type, actuator_type, numerical_s_type)

    room_is_part_of_floor = predicates_dict["room_is_part_of_floor"]
    sensor_is_part_of_room = predicates_dict["sensor_is_part_of_room"]
    actuator_is_part_of_room = predicates_dict["actuator_is_part_of_room"]
    positioned_at = predicates_dict["positioned_at"]
    actuator_increases_sensor = predicates_dict["actuator_increases_sensor"]
    actuator_decreases_sensor = predicates_dict["actuator_decreases_sensor"]
    is_next_to = predicates_dict["is_next_to"]
    is_at = predicates_dict["is_at"]
    is_occupied = predicates_dict["is_occupied"]
    will_become_occupied = predicates_dict["will_become_occupied"]
    is_cleaned = predicates_dict["is_cleaned"]
    is_sensing = predicates_dict["is_sensing"]
    is_low = predicates_dict["is_low"]
    is_ok = predicates_dict["is_ok"]
    is_high = predicates_dict["is_high"]
    is_activated = predicates_dict["is_activated"]
    is_locked = predicates_dict["is_locked"]
    checked_all_activitys = predicates_dict["checked_all_activitys"]
    fulfilled_activitys = predicates_dict["fulfilled_activitys"]

    domain = create_domain(input_dictionary['domain_name'], predicates_dict, pddl_variable_types, input_dictionary['activity_mapping'])

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

    initial_state = initial_state + pddl_converter_initial_state.create_initial_state_room_topology(room_is_part_of_floor, is_next_to, floor_uids, room_uids_per_floor, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms)
    initial_state = initial_state + pddl_converter_initial_state.create_initial_state_elevator_topology(room_is_part_of_floor, is_next_to, is_cleaned, floor_uids, room_uids_per_floor, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, uid_to_pddl_variable_elevators, uid_to_pddl_variable_room_positions, checked_all_activitys, fulfilled_activitys)

    initial_state = initial_state + pddl_converter_initial_state.create_cleaning_teams_starting_position(uid_to_pddl_variable_cleaning_teams, uid_to_pddl_variable_elevators, is_at)

    initial_state = initial_state + pddl_converter_initial_state.create_iot_room_mapping(floor_uids, room_uids_per_floor, uid_to_pddl_variable_sensors, uid_to_pddl_variable_rooms, sensor_room_mapping, sensor_is_part_of_room)
    initial_state = initial_state + pddl_converter_initial_state.create_iot_room_mapping(floor_uids, room_uids_per_floor, uid_to_pddl_variable_actuators, uid_to_pddl_variable_rooms, actuator_room_mapping, actuator_is_part_of_room)

    initial_state = initial_state + pddl_converter_initial_state.create_iot_position_mapping(uid_to_pddl_variable_room_positions, uid_to_pddl_variable_sensors, uid_to_pddl_variable_actuators, positioned_at)

    initial_state = initial_state + pddl_converter_initial_state.create_iot_influences_iot_mapping(actuator_increases_sensor_mapping_matrix, actuator_decreases_sensor_mapping_matrix, uid_to_pddl_variable_actuators, uid_to_pddl_variable_sensors, actuator_increases_sensor, actuator_decreases_sensor)

    # context
    # raw sensor data
    assert len(sensor_initial_values) <= len(uid_to_pddl_variable_sensors)
    assert len(sensor_goal_values) <= len(uid_to_pddl_variable_sensors)
    assert len(actuator_initial_values) <= len(uid_to_pddl_variable_actuators)

    initial_state = initial_state + pddl_converter_initial_state.create_sensor_values(is_high, is_ok, is_low, floor_uids, room_uids_per_floor, sensor_room_mapping, uid_to_pddl_variable_sensors, sensor_initial_values)
    initial_state = initial_state + pddl_converter_initial_state.create_sensor_locks(sensor_initial_locked, is_locked, uid_to_pddl_variable_sensors)
    individual_sensor_goals = pddl_converter_initial_state.create_sensor_values(is_high, is_ok, is_low, floor_uids, room_uids_per_floor, sensor_room_mapping, uid_to_pddl_variable_sensors, sensor_goal_values)
    initial_state = initial_state + pddl_converter_initial_state.create_actuator_values(is_activated, floor_uids, room_uids_per_floor, actuator_room_mapping, uid_to_pddl_variable_actuators, actuator_initial_values)

    # context room occupied
    assert len(room_occupied_actuator_initial_values) <= len(uid_to_pddl_variable_rooms)
    initial_state = initial_state + pddl_converter_initial_state.create_room_occupied_values(is_occupied, room_occupied_actuator_initial_values, floor_uids, room_uids_per_floor, uid_to_pddl_variable_rooms)

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
