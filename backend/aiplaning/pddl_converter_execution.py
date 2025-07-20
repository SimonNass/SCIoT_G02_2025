#!/usr/bin/env python
"""Module converts the ai plan to executable functions."""

from typing import List
from enum import Enum
import logging

class PlanerTag(Enum):
    """Class representing the possible planer tags given to actions during the creation."""
    Helper = 11 # helper actions can be ignored
    Detected_Activity = 12 # helper actions can be ignored

    # specifies the intention of an action
    Clean_Intent = 21
    Assignment_Intent = 21
    Change_Sensor_Intent = 22
    Detect_Activity_Intent = 23
    Fulfill_Activity_Intent = 24
    Save_Energy_Intent = 25

    Actuator_Off = 31 # turn off actuator
    Actuator_Increse = 32 # increse actuator
    Actuator_Decrese = 33 # decrese actuator
    Actuator_Cancle_Out = 34 # two actuators are infolfed

class pddl_actions_to_execution_mapper():
    def __init__(self):
        self.pddl_actions_to_execution_map = {}

    def __str__(self):
        return str(self.pddl_actions_to_execution_map)

    def add_action(self, name: str, parametertypes: List[str], planertags: List[PlanerTag]):
        self.pddl_actions_to_execution_map.update({name.lower():(parametertypes, planertags)})

    def calculate_helper_actions(self):
        helper_action_names = []
        for action_name, action_values in self.pddl_actions_to_execution_map.items():
            if PlanerTag.Helper in action_values[1]:
                helper_action_names.append(action_name)
        return helper_action_names

    def filter_plan(self, plan: List[str]):
        if plan == None:
            logging.warning(f"Plan is None.")
            return
        try: 
        # test example
        # # plan = ["0.00000: (ASSIGN_LOCK_FOR_SENSOR TEMPERATURE_S_S3)",
        #         "0.00100: (SAVE_ENERGY ACTUATOR_A1 ROOM_R0)",
        #         "0.00200: (DETECT_NO_POSSIBLE_ACTIVITY_READ ROOM_R0 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.00300: (DETECT_ALL_ACTIVITYS ROOM_R0 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.00400: (DETECT_NO_POSSIBLE_ACTIVITY_READ ROOM_R2 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.00500: (DETECT_ALL_ACTIVITYS ROOM_R2 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.00600: (DETECT_NO_POSSIBLE_ACTIVITY_READ ROOM_R3 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.00700: (DETECT_ALL_ACTIVITYS ROOM_R3 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.00800: (DETECT_NO_POSSIBLE_ACTIVITY_READ ROOM_R1 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.00900: (DETECT_ALL_ACTIVITYS ROOM_R1 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.01000: (FULFILL_ACTIVITY_NO_SLEEP ROOM_R3 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.01100: (FULFILL_ACTIVITY_NO_READ ROOM_R3 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.01200: (FULFILL_ALL_ACTIVITYS ROOM_R3 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.01300: (FULFILL_ACTIVITY_NO_SLEEP ROOM_R2 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.01400: (FULFILL_ACTIVITY_NO_READ ROOM_R2 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.01500: (FULFILL_ALL_ACTIVITYS ROOM_R2 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.01600: (FULFILL_ACTIVITY_NO_SLEEP ROOM_R1 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.01700: (FULFILL_ACTIVITY_NO_READ ROOM_R1 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.01800: (FULFILL_ALL_ACTIVITYS ROOM_R1 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.01900: (FULFILL_ACTIVITY_NO_SLEEP ROOM_R0 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.02000: (FULFILL_ACTIVITY_NO_READ ROOM_R0 ROOM_POSITION_OVERALL_ROOM)",
        #         "0.02100: (FULFILL_ALL_ACTIVITYS ROOM_R0 ROOM_POSITION_OVERALL_ROOM)"]
        #(REACH-GOAL)

            # transform to workable substructure instead of just a streing
            # remove timestamps
            # filtered_plan = [planed_action.split(':')[1] for planed_action in plan]
            # remove whitespace borders, (, and )
            # filtered_plan = [planed_action.strip().replace('(','').replace(')','').lower() for planed_action in filtered_plan]
            # split action name and parameters into a list
            filtered_plan = [planed_action.lower() for planed_action in plan]
            filtered_plan = [planed_action for planed_action in filtered_plan if planed_action not in ['REACH-GOAL','(REACH-GOAL)','REACH-GOAL'.lower(),'(REACH-GOAL)'.lower()]]
            filtered_plan = [planed_action.split(' ') for planed_action in filtered_plan]

            get_tags = lambda planed_action : self.pddl_actions_to_execution_map[planed_action[0]][1]
            filter_plans_positive = lambda filtered_plan, filter : [planed_action for planed_action in filtered_plan if filter in get_tags(planed_action)]
            filter_plans_negative = lambda filtered_plan, filter : [planed_action for planed_action in filtered_plan if filter not in get_tags(planed_action)]
            
            # remove all helper methodes
            detected_activity_plan = filter_plans_positive(filtered_plan, PlanerTag.Detected_Activity)
            filtered_plan = filter_plans_negative(filtered_plan, PlanerTag.Helper)
            filtered_plan = filter_plans_negative(filtered_plan, PlanerTag.Detected_Activity)
            #print (list(filtered_plan))

            # make a list of all cleaning actions without other actions in between
            cleaning_plan = filter_plans_positive(filtered_plan, PlanerTag.Clean_Intent)

            # make a list of all one actuator actions without other actions in between
            one_actuators_involved_actioin_plans = filter_plans_negative(filtered_plan, PlanerTag.Actuator_Cancle_Out)
            #print (list(one_actuators_involved_actioin_plans))
            turn_off_actuator_plans = filter_plans_positive(one_actuators_involved_actioin_plans, PlanerTag.Actuator_Off)
            increse_actuator_plans = filter_plans_positive(one_actuators_involved_actioin_plans, PlanerTag.Actuator_Increse)
            decrese_actuator_plans = filter_plans_positive(one_actuators_involved_actioin_plans, PlanerTag.Actuator_Decrese)
            
            # make a list of all two actuator actions without other actions in between
            two_actuators_involved_actioin_plans = filter_plans_positive(filtered_plan, PlanerTag.Actuator_Cancle_Out)
            
            logging.info(f"Cleaning plan: {cleaning_plan}")
            logging.info(f"Detected activitys plan: {detected_activity_plan}")
            print(f"Detected activitys plan: {detected_activity_plan}")
            logging.info(f"Increase actuator plans: {increse_actuator_plans}")
            logging.info(f"Turn off actuator plans: {turn_off_actuator_plans}")
            logging.info(f"Decrese Actuator actuator plans: {decrese_actuator_plans}")
            logging.info(f"Two Actuators Involved Actioin Plans: {two_actuators_involved_actioin_plans}")
            return filtered_plan, cleaning_plan, increse_actuator_plans, turn_off_actuator_plans, decrese_actuator_plans, two_actuators_involved_actioin_plans
        except Exception as e:
            logging.error({'Error parsing plan to usable information': str(e)})
