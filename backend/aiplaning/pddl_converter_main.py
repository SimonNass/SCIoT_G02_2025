#!/usr/bin/env python
"""Module generates pddl domain and problem files."""

# pip install pddl==0.4.3
import sys
from typing import List, Dict, Optional
from pddl.logic import variables
from pddl.core import Domain, Problem
from pddl.requirements import Requirements
import logging
from backend.extensions import pddl_service

from backend.aiplaning import pddl_converter_actions
from backend.aiplaning import pddl_converter_goals
from backend.aiplaning import pddl_converter_types
from backend.aiplaning import pddl_converter_predicates
from backend.aiplaning import pddl_converter_objects
from backend.aiplaning import pddl_converter_input
from backend.aiplaning import pddl_converter_initial_state
from backend.aiplaning import pddl_converter_help
from backend.aiplaning.pddl_converter_execution import PlanerTag, pddl_actions_to_execution_mapper


def create(input_dictionary):

    try: 
        # set up variables and constants
        pddl_variable_types = pddl_converter_types.create_type_variables()

        activity_detect_mapping: Dict[str,Dict[str,str]] = input_dictionary['activity_detect_mapping']
        activity_fulfill_mapping: Dict[str,Dict[str,str]] = input_dictionary['activity_fulfill_mapping']

        predicates_dict = pddl_converter_predicates.create_predicates_variables(pddl_variable_types, activity_fulfill_mapping.keys())
        
        # set up types
        type_dict = pddl_converter_types.create_type_dict()

        # define actions
        actions_list, execution_mapper = pddl_converter_actions.create_actions(predicates_dict, pddl_variable_types, activity_detect_mapping, activity_fulfill_mapping)

        # define the domain object.
        requirements = [Requirements.STRIPS, Requirements.TYPING, Requirements.ADL]
        domain = Domain(input_dictionary['domain_name'],
                        requirements=requirements,
                        types=type_dict,
                        predicates=list(predicates_dict.values()),
                        actions=actions_list)

        #print(domain)
        
        all_objects, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, uid_to_pddl_variable_sensors,uid_to_pddl_variable_actuators, uid_to_pddl_variable_elevators, uid_to_pddl_variable_cleaning_teams, uid_to_pddl_variable_room_positions = pddl_converter_objects.create_all_obbjects(input_dictionary)
        
        # create initial state
        initial_state = pddl_converter_initial_state.create_initial_state(predicates_dict, input_dictionary, uid_to_pddl_variable_floor, uid_to_pddl_variable_rooms, uid_to_pddl_variable_sensors,uid_to_pddl_variable_actuators, uid_to_pddl_variable_elevators, uid_to_pddl_variable_cleaning_teams, uid_to_pddl_variable_room_positions)

        # TODO
        #floor_uids = input_dictionary['floor_uids']
        #room_uids_per_floor = input_dictionary['room_uids_per_floor']
        #sensor_room_mapping = input_dictionary['sensor_room_mapping']
        #sensor_goal_values = input_dictionary['sensor_goal_values']
        #assert len(sensor_goal_values) <= len(uid_to_pddl_variable_sensors)
        #individual_sensor_goals = pddl_converter_initial_state.create_sensor_values(predicates_dict, floor_uids, room_uids_per_floor, sensor_room_mapping, uid_to_pddl_variable_sensors, sensor_goal_values)
        
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

        return domain, problem, execution_mapper
    except Exception as e:
        logging.error({'Failed to create pddl': str(e)})

def main():
    pddl_converter_help.check_lib_versions()

    over_config_file = False
    config_file_name = ''
    if len(sys.argv) > 2:
        print ("Chosen system arguments: " + str(sys.argv))
        over_config_file = sys.argv[1]
        config_file_name = sys.argv[2]

    input_dictionary = pddl_converter_input.query_input(over_config_file,config_file_name)

    # output_path is relative to working directory
    output_path = input_dictionary['output_path']
    domaine_file_name = input_dictionary['domaine_file_name']
    problem_file_name = input_dictionary['problem_file_name']

    d, p, execution_mapper = create(input_dictionary)
    # Use PDDL Service to plan: pddl_service.solve_planning_problem(d, p)
    execution_mapper.filter_plan(None)

    pddl_converter_help.write_out_pddl(output_path, domaine_file_name + ".pddl", d)
    pddl_converter_help.write_out_pddl(output_path, problem_file_name + ".pddl", p)
    #json_text = '{"excludeActions": []}'
    json_text = '{"excludeActions": ["detect_all_activitys","fulfill_all_activitys","detect_no_possible_activity_sleep","detect_no_possible_activity_read","fulfill_activity_no_sleep","fulfill_activity_no_read"]}'
    pddl_converter_help.write_out_pddl_visualisation_hints(output_path, domaine_file_name + ".planviz.json", json_text)

def run_planner_with_db_data(sensor_goal_values: Optional[Dict[str, int]] = [],
                            sensor_initial_locked: Optional[List[str]] = []):
    pddl_converter_help.check_lib_versions()

    input_dictionary = pddl_converter_input.query_input_over_db(sensor_goal_values, sensor_initial_locked)
    logging.info("Gets here")
    logging.info(input_dictionary)
    
    d, p, execution_mapper = create(input_dictionary)
    pddl_converter_help.write_out_pddl("/backend/aiplaning/auto_generated", "d" + ".pddl", d)
    pddl_converter_help.write_out_pddl("/backend/aiplaning/auto_generated", "p" + ".pddl", p)
    solve_result = pddl_service.solve_planning_problem(str(d), str(p), "dual-bfws-ffparser")
    logging.info(f"Plan: {solve_result.get('plan')}")
    filtered_plan = execution_mapper.filter_plan(solve_result.get('plan'))
    logging.info(f"Filtered Plan: {filtered_plan}")
    return filtered_plan


if __name__ == '__main__':
    main()
