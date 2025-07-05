#!/usr/bin/env python

# pip install pddl==0.4.3
from pddl.logic import Predicate

def create_predicates_variables(floor_type, room_type, room2_type, room_position_type, cleaning_team_type, iot_type, sensor_type, actuator_type, numerical_s_type):
    # define predicates
    predicates_list = []

    # topology
    room_is_part_of_floor = Predicate("room_is_part_of_floor", room_type, floor_type)
    predicates_list.append(room_is_part_of_floor)

    sensor_is_part_of_room = Predicate("sensor_is_part_of_room", sensor_type, room_type)
    predicates_list.append(sensor_is_part_of_room)
    actuator_is_part_of_room = Predicate("actuator_is_part_of_room", actuator_type, room_type)
    predicates_list.append(actuator_is_part_of_room)
    # problem to lock down a sensor that is part of two room positions
    positioned_at = Predicate("positioned_at", iot_type, room_position_type)
    predicates_list.append(positioned_at)

    actuator_increases_sensor = Predicate("actuator_increases_sensor", actuator_type, sensor_type)
    predicates_list.append(actuator_increases_sensor)
    actuator_decreases_sensor = Predicate("actuator_decreases_sensor", actuator_type, sensor_type)
    predicates_list.append(actuator_decreases_sensor)

    is_next_to = Predicate("is_next_to", room_type, room2_type)
    predicates_list.append(is_next_to)

    is_at = Predicate("is_at", cleaning_team_type, room_type)
    predicates_list.append(is_at)

    # meta context

    is_occupied = Predicate("is_occupied", room_type)
    predicates_list.append(is_occupied)

    will_become_occupied = Predicate("will_become_occupied", room_type)
    predicates_list.append(will_become_occupied)

    is_cleaned = Predicate("is_cleaned", room_type)
    predicates_list.append(is_cleaned)

    # activity
    has_specified_activity_at = Predicate("has_specified_activity_at", room_type, room_position_type)
    predicates_list.append(has_specified_activity_at)
    
    activity_names = ['read','sleep','bath']
    is_doing_activitys_at = {}
    for activity in activity_names:
        is_doing_a_at = Predicate(f"is_doing_{activity}_at", room_type, room_position_type)
        is_doing_activitys_at.update({f"{activity}":is_doing_a_at})
        predicates_list.append(is_doing_a_at)

    # sensors
    is_sensing = Predicate("is_sensing", sensor_type)
    predicates_list.append(is_sensing)

    is_low = Predicate("is_low", numerical_s_type)
    predicates_list.append(is_low)
    is_ok = Predicate("is_ok", numerical_s_type)
    predicates_list.append(is_ok)
    is_high = Predicate("is_high", numerical_s_type)
    predicates_list.append(is_high)

    # actuators
    is_activated = Predicate("is_activated", actuator_type)
    predicates_list.append(is_activated)

    # force checks predicate
    fulfilled_activity = Predicate("fulfilled_activity", room_type, room_position_type)
    predicates_list.append(fulfilled_activity)

    return predicates_list, room_is_part_of_floor, sensor_is_part_of_room, actuator_is_part_of_room, positioned_at, actuator_increases_sensor, actuator_decreases_sensor, is_next_to, is_at, is_occupied, will_become_occupied, is_cleaned, has_specified_activity_at, activity_names, is_doing_activitys_at, is_sensing, is_low, is_ok, is_high, is_activated, fulfilled_activity
