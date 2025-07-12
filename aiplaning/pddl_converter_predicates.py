#!/usr/bin/env python
"""Module specifies the predicates of a pddl domain file."""

# pip install pddl==0.4.3
from pddl.logic import Predicate

def create_predicates_variables(floor_type, room_type, room2_type, room_position_type, cleaning_team_type, iot_type, sensor_type, actuator_type, numerical_s_type):
    # define predicates
    predicates_dict = {}

    # topology
    room_is_part_of_floor = Predicate("room_is_part_of_floor", room_type, floor_type)
    predicates_dict.update({"room_is_part_of_floor":room_is_part_of_floor})

    sensor_is_part_of_room = Predicate("sensor_is_part_of_room", sensor_type, room_type)
    predicates_dict.update({"sensor_is_part_of_room":sensor_is_part_of_room})
    actuator_is_part_of_room = Predicate("actuator_is_part_of_room", actuator_type, room_type)
    predicates_dict.update({"actuator_is_part_of_room":actuator_is_part_of_room})
    # problem to lock down a sensor that is part of two room positions
    positioned_at = Predicate("positioned_at", iot_type, room_position_type)
    predicates_dict.update({"positioned_at":positioned_at})

    actuator_increases_sensor = Predicate("actuator_increases_sensor", actuator_type, sensor_type)
    predicates_dict.update({"actuator_increases_sensor":actuator_increases_sensor})
    actuator_decreases_sensor = Predicate("actuator_decreases_sensor", actuator_type, sensor_type)
    predicates_dict.update({"actuator_decreases_sensor":actuator_decreases_sensor})

    is_next_to = Predicate("is_next_to", room_type, room2_type)
    predicates_dict.update({"is_next_to":is_next_to})

    is_at = Predicate("is_at", cleaning_team_type, room_type)
    predicates_dict.update({"is_at":is_at})

    # meta context

    is_occupied = Predicate("is_occupied", room_type)
    predicates_dict.update({"is_occupied":is_occupied})

    will_become_occupied = Predicate("will_become_occupied", room_type)
    predicates_dict.update({"will_become_occupied":will_become_occupied})

    is_cleaned = Predicate("is_cleaned", room_type)
    predicates_dict.update({"is_cleaned":is_cleaned})

    # activity
    activity_names = ['read','sleep','bath']
    is_doing_activitys_at = {}
    for activity in activity_names:
        is_doing_a_at = Predicate(f"is_doing_{activity}_at", room_type, room_position_type)
        is_doing_activitys_at.update({f"{activity}":is_doing_a_at})
        predicates_dict.update({f"is_doing_{activity}_at":is_doing_a_at})

    # force checks predicate
    checked_activity_x = {}
    for activity in activity_names:
        checked_a = Predicate(f"checked_activity_{activity}", room_type, room_position_type)
        checked_activity_x.update({f"{activity}":checked_a})
        predicates_dict.update({f"checked_activity_{activity}":checked_a})

    fulfilled_activity_x = {}
    for activity in activity_names:
        fulfilled_a = Predicate(f"fulfilled_activity_{activity}", room_type, room_position_type)
        fulfilled_activity_x.update({f"{activity}":fulfilled_a})
        predicates_dict.update({f"fulfilled_activity_{activity}":fulfilled_a})

    checked_all_activitys = Predicate("checked_activitys", room_type, room_position_type)
    predicates_dict.update({"checked_all_activitys":checked_all_activitys})

    fulfilled_activitys = Predicate("fulfilled_activitys", room_type, room_position_type)
    predicates_dict.update({"fulfilled_activitys":fulfilled_activitys})

    # sensors
    is_locked = Predicate("is_locked", sensor_type)
    predicates_dict.update({"is_locked":is_locked})

    is_sensing = Predicate("is_sensing", sensor_type)
    predicates_dict.update({"is_sensing":is_sensing})

    is_low = Predicate("is_low", numerical_s_type)
    predicates_dict.update({"is_low":is_low})
    is_ok = Predicate("is_ok", numerical_s_type)
    predicates_dict.update({"is_ok":is_ok})
    is_high = Predicate("is_high", numerical_s_type)
    predicates_dict.update({"is_high":is_high})

    # actuators
    is_activated = Predicate("is_activated", actuator_type)
    predicates_dict.update({"is_activated":is_activated})
    is_changed = Predicate("is_changed", actuator_type)
    predicates_dict.update({"is_changed":is_changed})


    return predicates_dict, activity_names, is_doing_activitys_at, checked_activity_x, fulfilled_activity_x
