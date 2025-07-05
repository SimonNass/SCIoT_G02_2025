#!/usr/bin/env python

# pip install pddl==0.4.3
from typing import List
from pddl.logic import Predicate, constants, variables, base

def create_goal(fulfilled_activity, is_activated, is_cleaned, is_occupied, actuator_is_part_of_room, room_type, room_position_type, actuator_type, plan_cleaning: bool = True):
    goal_state = None

    # individual_sensor_goals TODO
    #goal_for_occupied_rooms = None

    if_case1 = base.And(base.Not(is_occupied(room_type)))
    then_clean_case = is_cleaned(room_type)
    clean_unoccupied_rooms = base.ForallCondition(base.Imply(if_case1, then_clean_case), [room_type])

    if_case2 = base.And(base.Not(is_occupied(room_type)), actuator_is_part_of_room(actuator_type, room_type))
    then_turn_off_actuator = base.Not(is_activated(actuator_type))
    actuator_off_unoccupied_rooms = base.ForallCondition(base.Imply(if_case2, then_turn_off_actuator), [room_type, actuator_type])

    enforce_checks = base.ForallCondition(fulfilled_activity(room_type, room_position_type), [room_type, room_position_type])

    if plan_cleaning:
        goal_state = base.And(clean_unoccupied_rooms, actuator_off_unoccupied_rooms, enforce_checks)
    else:
        goal_state = base.And(actuator_off_unoccupied_rooms, enforce_checks)
    return goal_state
