#!/usr/bin/env python
"""Module generates pddl domain and problem files."""

# pip install pddl==0.4.3
import sys
import json
import time
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
from backend.aiplaning.utils.updateActuators import updateActuators
from backend.aiplaning.utils.dbUtils import save_to_database
from backend.models.models import PlanScope


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
        domain = Domain(input_dictionary['domain_name']+ f'Time{str(time.time()).replace('.','')}',
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
    use_local_pddl_service = False
    if len(sys.argv) > 3:
        over_config_file = sys.argv[1]
        config_file_name = sys.argv[2]
        use_local_pddl_service = bool(sys.argv[3] in ["True"])
        print (f"Chosen system arguments: over_config_file {over_config_file}, config_file_name {config_file_name}, use_local_pddl_service {use_local_pddl_service}")

    input_dictionary = pddl_converter_input.query_input(over_config_file,config_file_name)

    # output_path is relative to working directory
    output_path = input_dictionary['output_path']
    domaine_file_name = input_dictionary['domaine_file_name']
    problem_file_name = input_dictionary['problem_file_name']

    d, p, execution_mapper = create(input_dictionary)
    
    # Use PDDL Service to plan
    plan = None
    #if use_local_pddl_service:
    #    from backend.services.pddl_service import PDDLPlannerService
    #    from flask import Flask
    #    from backend.config import Config
    #    pddl_service = PDDLPlannerService()
    #    app = Flask(__name__)
    #    app.config.from_object(Config)
    #    pddl_service.init_app(app)
    #    solve_result = pddl_service.solve_planning_problem(str(d), str(p), "dual-bfws-ffparser")
    #    plan = solve_result.get('plan')
    execution_mapper.filter_plan(plan)

    pddl_converter_help.write_out_pddl(output_path, domaine_file_name + ".pddl", d)
    pddl_converter_help.write_out_pddl(output_path, problem_file_name + ".pddl", p)

    helper_action_names = execution_mapper.calculate_helper_actions()
    json_text = {'excludeActions': helper_action_names}
    pddl_converter_help.write_out_pddl(output_path, domaine_file_name + ".planviz.json", json.dumps(json_text))

def run_planner_with_db_data(sensor_goal_values: Optional[Dict[str, int]] = {},
                            sensor_initial_locked: Optional[List[str]] = [],
                            room_number: str = None):
    planner = "dual-bfws-ffparser"
    pddl_converter_help.check_lib_versions()

    input_dictionary = pddl_converter_input.query_input_over_db(sensor_goal_values, sensor_initial_locked, room_number)
    logging.info("Gets here")
    # logging.info(input_dictionary)
    
    d, p, execution_mapper = create(input_dictionary)
    pddl_converter_help.write_out_pddl("/backend/aiplaning/auto_generated", "d" + ".pddl", d)
    pddl_converter_help.write_out_pddl("/backend/aiplaning/auto_generated", "p" + ".pddl", p)
    solve_result = pddl_service.solve_planning_problem(str(d), str(p), planner, False)
    
    filtered_plan, cleaning_plan, increse_actuator_plans, turn_off_actuator_plans, decrese_actuator_plans, two_actuators_involved_actioin_plans = execution_mapper.filter_plan(solve_result.get('plan'))
    
    updateActuators(increse_actuator_plans, turn_off_actuator_plans, decrese_actuator_plans)
    if room_number is None:
        plan = save_to_database(solve_result, planner, cleaning_plan, filtered_plan)
    else:
        plan = save_to_database(solve_result, planner, cleaning_plan, filtered_plan, PlanScope.ROOM, room_number)

    return plan


if __name__ == '__main__':
    main()
