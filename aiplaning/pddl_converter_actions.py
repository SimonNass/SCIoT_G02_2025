#!/usr/bin/env python
"""Module specifies the actions of a pddl domain file."""

# pip install pddl==0.4.3
from pddl.logic import base
from pddl.logic.predicates import EqualTo
from pddl.action import Action


def create_cleaning_actions(is_cleaned, will_become_occupied, is_occupied, is_at, is_next_to, room_is_part_of_floor, cleaning_team_type, room_type, room2_type, room3_type, floor_type, floor2_type):
    actions_list = []
    # construct compound predicates
    is_next_to_bidirectional = lambda r1, r2 : (base.Or(is_next_to(r1, r2), is_next_to(r2, r1)))
    is_not_next_to_bidirectional = lambda r1, r2 : (base.And(~is_next_to(r1, r2), ~is_next_to(r2, r1)))
    rooms_are_part_of_floors = lambda r1, r2, f1, f2 : room_is_part_of_floor(r1, f1) & room_is_part_of_floor(r2, f2)

    move_to_floor = Action(
        "move_to_floor",
        parameters=[cleaning_team_type, room_type, room2_type, floor_type, floor2_type],
        precondition=is_at(cleaning_team_type,room_type)
                    & is_next_to_bidirectional(room_type, room2_type)
                    & rooms_are_part_of_floors(room_type, room2_type, floor_type, floor2_type)
                    & base.Not(EqualTo(floor_type, floor2_type)),
        effect=~is_at(cleaning_team_type,room_type) & is_at(cleaning_team_type,room2_type)
    )
    actions_list.append(move_to_floor)

    move_to_room = Action(
        "move_to_room",
        parameters=[cleaning_team_type, room_type, room2_type, floor_type],
        precondition=is_at(cleaning_team_type,room_type)
                    & is_next_to_bidirectional(room_type, room2_type)
                    & rooms_are_part_of_floors(room_type, room2_type, floor_type, floor_type),
        effect=~is_at(cleaning_team_type,room_type) & is_at(cleaning_team_type,room2_type)
    )
    actions_list.append(move_to_room)

    move_to_isolated_room = Action(
        "move_to_isolated_room",
        parameters=[cleaning_team_type, room_type, room2_type, floor_type],
        precondition=is_at(cleaning_team_type,room_type)
                    & (base.ForallCondition(is_not_next_to_bidirectional(room3_type, room2_type) , [room3_type]))
                    & rooms_are_part_of_floors(room_type, room2_type, floor_type, floor_type),
        effect=~is_at(cleaning_team_type,room_type) & is_at(cleaning_team_type,room2_type)
    )
    actions_list.append(move_to_isolated_room)

    team_clean = Action(
        "team_clean",
        parameters=[cleaning_team_type, room_type],
        precondition=is_at(cleaning_team_type,room_type)
                    & ~is_cleaned(room_type)
                    & ~is_occupied(room_type)
                    & ~will_become_occupied(room_type),
        effect=is_cleaned(room_type)
    )
    actions_list.append(team_clean)

    return actions_list

def create_assign_actions(positioned_at, room_is_part_of_floor, iot_type, room_position_type, room_type, floor_type, floor2_type):
    actions_list = []

    assign_floor = Action(
        "assign_floor",
        parameters=[room_type, floor_type],
        precondition=base.ForallCondition(~(room_is_part_of_floor(room_type, floor2_type)), [floor2_type]),
        effect=room_is_part_of_floor(room_type, floor_type)
    )
    actions_list.append(assign_floor)

    assign_room_position = Action(
        "assign_room_position",
        parameters=[iot_type],
        precondition=base.ForallCondition(~(positioned_at(iot_type, room_position_type)), [room_position_type]),
        effect=base.ForallCondition((positioned_at(iot_type, room_position_type)), [room_position_type])
    )
    actions_list.append(assign_room_position)

    return actions_list

def create_actuator_actions(is_locked, is_activated, is_high, is_ok, is_low, is_sensing, positioned_at, actuator_decreases_sensor, actuator_increases_sensor, sensor_is_part_of_room, sensor_type, actuator_type, room_position_type, room_type):
    actions_list = []
    # construct compound predicates
    works_together = lambda s1, p1, r1 : positioned_at(s1, p1) & sensor_is_part_of_room(s1, r1)

    turn_on = Action(
        "turn_on",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~is_locked(sensor_type)
                    & works_together(sensor_type, room_position_type, room_type)
                    & actuator_increases_sensor(actuator_type, sensor_type)
                    & ~is_sensing(sensor_type)
                    & ~is_activated(actuator_type),
        effect=is_sensing(sensor_type) & is_activated(actuator_type)
    )
    actions_list.append(turn_on)

    turn_off = Action(
        "turn_off",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~is_locked(sensor_type)
                    & works_together(sensor_type, room_position_type, room_type)
                    & actuator_increases_sensor(actuator_type, sensor_type)
                    & is_sensing(sensor_type)
                    & is_activated(actuator_type),
        effect=~is_sensing(sensor_type) & ~is_activated(actuator_type)
    )
    actions_list.append(turn_off)

    turn_on_inverted = Action(
        "turn_on_inverted",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~is_locked(sensor_type)
                    & works_together(sensor_type, room_position_type, room_type)
                    & actuator_decreases_sensor(actuator_type, sensor_type)
                    & ~is_sensing(sensor_type)
                    & is_activated(actuator_type),
        effect=is_sensing(sensor_type) & ~is_activated(actuator_type)
    )
    actions_list.append(turn_on_inverted)

    turn_off_inverted = Action(
        "turn_off_inverted",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~is_locked(sensor_type)
                    & works_together(sensor_type, room_position_type, room_type)
                    & actuator_decreases_sensor(actuator_type, sensor_type)
                    & is_sensing(sensor_type)
                    & ~is_activated(actuator_type),
        effect=~is_sensing(sensor_type) & is_activated(actuator_type)
    )
    actions_list.append(turn_off_inverted)

    increase_s_by_a_in_r = Action(
        "increase_s_by_a_in_r",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~is_locked(sensor_type)
                    & works_together(sensor_type, room_position_type, room_type)
                    & actuator_increases_sensor(actuator_type, sensor_type)
                    & is_low(sensor_type)
                    & ~is_activated(actuator_type),
        effect=~is_low(sensor_type) & is_ok(sensor_type) & is_activated(actuator_type)
    )
    actions_list.append(increase_s_by_a_in_r)

    increase_s_by_na_in_r = Action(
        "increase_s_by_na_in_r",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~is_locked(sensor_type)
                    & works_together(sensor_type, room_position_type, room_type)
                    & actuator_decreases_sensor(actuator_type, sensor_type)
                    & is_low(sensor_type)
                    & is_activated(actuator_type),
        effect=~is_low(sensor_type) & is_ok(sensor_type) & ~is_activated(actuator_type)
    )
    actions_list.append(increase_s_by_na_in_r)

    decrease_s_by_a_in_r = Action(
        "decrease_s_by_a_in_r",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~is_locked(sensor_type)
                    & works_together(sensor_type, room_position_type, room_type)
                    & actuator_decreases_sensor(actuator_type, sensor_type)
                    & is_high(sensor_type)
                    & ~is_activated(actuator_type),
        effect=~is_high(sensor_type) & is_ok(sensor_type) & is_activated(actuator_type)
    )
    actions_list.append(decrease_s_by_a_in_r)

    decrease_s_by_na_in_r = Action(
        "decrease_s_by_na_in_r",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~is_locked(sensor_type)
                    & works_together(sensor_type, room_position_type, room_type)
                    & actuator_increases_sensor(actuator_type, sensor_type)
                    & is_high(sensor_type)
                    & is_activated(actuator_type),
        effect=~is_high(sensor_type) & is_ok(sensor_type) & ~is_activated(actuator_type)
    )
    actions_list.append(decrease_s_by_na_in_r)

    return actions_list

def create_activity_detection_actions(checked_activity_x, checked_all_activitys, is_doing_activitys_at, room_position_type, room_type, binary_s_type, is_sensing, positioned_at, sensor_is_part_of_room):
    actions_list = []

    is_doing_read_at = is_doing_activitys_at['read']
    is_doing_bath_at = is_doing_activitys_at['bath']
    is_doing_sleep_at = is_doing_activitys_at['sleep']

    checked_activity_sleep = checked_activity_x['sleep']
    checked_activity_read = checked_activity_x['read']

    # TODO fine tune sensor detection for the activitys
    detect_activity_sleep = Action(
        "detect_activity_sleep",
        parameters=[binary_s_type, room_type, room_position_type],
        precondition=is_sensing(binary_s_type)
                    & positioned_at(binary_s_type, room_position_type) 
                    & sensor_is_part_of_room(binary_s_type, room_type)
                    & ~checked_activity_sleep(room_type, room_position_type),
        effect=checked_activity_sleep(room_type, room_position_type) & is_doing_sleep_at(room_type, room_position_type)
    )
    actions_list.append(detect_activity_sleep)

    detect_no_activity_sleep = Action(
        "detect_no_activity_sleep",
        parameters=[binary_s_type, room_type, room_position_type],
        precondition=~is_sensing(binary_s_type)
                    & positioned_at(binary_s_type, room_position_type) 
                    & sensor_is_part_of_room(binary_s_type, room_type)
                    & ~checked_activity_sleep(room_type, room_position_type),
        effect=checked_activity_sleep(room_type, room_position_type) & ~is_doing_sleep_at(room_type, room_position_type)
    )
    actions_list.append(detect_no_activity_sleep)

    detect_no_possible_activity_sleep = Action(
        "detect_no_possible_activity_sleep",
        parameters=[room_type, room_position_type],
        precondition=base.Not(base.ExistsCondition(positioned_at(binary_s_type, room_position_type) 
                                                    & sensor_is_part_of_room(binary_s_type, room_type), [binary_s_type]))
                    & ~checked_activity_sleep(room_type, room_position_type),
        effect=checked_activity_sleep(room_type, room_position_type) & ~is_doing_sleep_at(room_type, room_position_type)
    )
    actions_list.append(detect_no_possible_activity_sleep)

    detect_activity_read = Action(
        "detect_activity_read",
        parameters=[binary_s_type, room_type, room_position_type],
        precondition=is_sensing(binary_s_type)
                    & positioned_at(binary_s_type, room_position_type) 
                    & sensor_is_part_of_room(binary_s_type, room_type)
                    & ~checked_activity_read(room_type, room_position_type),
        effect=checked_activity_read(room_type, room_position_type) & is_doing_read_at(room_type, room_position_type)
    )
    actions_list.append(detect_activity_read)

    detect_no_activity_read = Action(
        "detect_no_activity_read",
        parameters=[binary_s_type, room_type, room_position_type],
        precondition=~is_sensing(binary_s_type)
                    & positioned_at(binary_s_type, room_position_type) 
                    & sensor_is_part_of_room(binary_s_type, room_type)
                    & ~checked_activity_read(room_type, room_position_type),
        effect=checked_activity_read(room_type, room_position_type) & ~is_doing_read_at(room_type, room_position_type)
    )
    actions_list.append(detect_no_activity_read)

    detect_no_possible_activity_read = Action(
        "detect_no_possible_activity_read",
        parameters=[room_type, room_position_type],
        precondition=base.Not(base.ExistsCondition(positioned_at(binary_s_type, room_position_type) 
                                                    & sensor_is_part_of_room(binary_s_type, room_type), [binary_s_type]))
                    & ~checked_activity_read(room_type, room_position_type),
        effect=checked_activity_read(room_type, room_position_type) & ~is_doing_read_at(room_type, room_position_type)
    )
    actions_list.append(detect_no_possible_activity_read)

    detect_all_activitys = Action(
        "detect_all_activitys",
        parameters=[room_type, room_position_type],
        precondition=base.And(checked_activity_sleep(room_type, room_position_type),
                              checked_activity_read(room_type, room_position_type),
                              ~checked_all_activitys(room_type, room_position_type)),
        effect=checked_all_activitys(room_type, room_position_type)
    )
    actions_list.append(detect_all_activitys)

    return actions_list

def create_activity_fulfilled_actions(is_low, is_ok, is_high, is_locked, fulfilled_activity_x, fulfilled_activitys, checked_all_activitys, is_doing_activitys_at, positioned_at, sensor_is_part_of_room, sensor_type, sensor2_type, room_position_type, room_type):
    actions_list = []

    precondition_to_fulfill_activity = lambda s1, r1, p1 : (base.And(positioned_at(s1, p1), 
                                                                     sensor_is_part_of_room(s1, r1), 
                                                                     checked_all_activitys(r1, p1)))

    activity_names = ['read','sleep','bath']
    is_doing_read_at = is_doing_activitys_at['read']
    #is_doing_bath_at = is_doing_activitys_at['bath']
    is_doing_sleep_at = is_doing_activitys_at['sleep']

    fulfilled_activity_read = fulfilled_activity_x['read']
    fulfilled_activity_sleep = fulfilled_activity_x['sleep']

    # TODO fine tune sensor ideal position for the activitys
    # TODO remove sensor_type from fulfilled_activity?
    fulfill_activity_sleep = Action(
        "fulfill_activity_read",
        parameters=[sensor_type, room_type, room_position_type],
        precondition=precondition_to_fulfill_activity(sensor_type, room_type, room_position_type)
                    & is_doing_read_at(room_type, room_position_type)
                    & ~fulfilled_activity_read(room_type, room_position_type)
                    & is_high(sensor_type),
        effect=fulfilled_activity_read(room_type, room_position_type) & is_locked(sensor_type)
    )
    actions_list.append(fulfill_activity_sleep)

    fulfill_activity_sleep = Action(
        "fulfill_activity_sleep",
        parameters=[sensor_type, room_type, room_position_type],
        precondition=precondition_to_fulfill_activity(sensor_type, room_type, room_position_type)
                    & is_doing_sleep_at(room_type, room_position_type)
                    & ~fulfilled_activity_sleep(room_type, room_position_type)
                    & is_low(sensor_type),
        effect=fulfilled_activity_sleep(room_type, room_position_type) & is_locked(sensor_type)
    )
    actions_list.append(fulfill_activity_sleep)

    for activity in activity_names:
        fulfill_activity_no_x = Action(
            f"fulfill_activity_no_{activity}",
            parameters=[room_type, room_position_type],
            precondition=checked_all_activitys(room_type, room_position_type)
                        & ~is_doing_activitys_at[activity](room_type, room_position_type)
                        & ~fulfilled_activity_x[activity](room_type, room_position_type),
            effect=fulfilled_activity_x[activity](room_type, room_position_type)
        )
        actions_list.append(fulfill_activity_no_x)

    fulfill_all_activitys = Action(
        "fulfill_all_activitys",
        parameters=[room_type, room_position_type],
        precondition=checked_all_activitys(room_type, room_position_type)
                    & fulfilled_activity_sleep(room_type, room_position_type)
                    & fulfilled_activity_read(room_type, room_position_type)
                    & ~fulfilled_activitys(room_type, room_position_type),
        effect=fulfilled_activitys(room_type, room_position_type)
    )
    actions_list.append(fulfill_all_activitys)

    return actions_list

def create_energy_saving_actions(is_activated, will_become_occupied, is_occupied, actuator_decreases_sensor, actuator_increases_sensor, actuator_is_part_of_room, sensor_is_part_of_room, sensor_type, actuator_type, actuator2_type, room_type):
    actions_list = []

    cancel_out_actuator = Action(
        "cancel_out_actuator",
        parameters=[sensor_type, actuator_type, actuator2_type, room_type],
        precondition= base.Not(EqualTo(actuator_type, actuator2_type))
                        & sensor_is_part_of_room(sensor_type, room_type)
                        & actuator_increases_sensor(actuator_type, sensor_type)
                        & actuator_decreases_sensor(actuator2_type, sensor_type)
                        & is_activated(actuator_type)
                        & is_activated(actuator2_type),
        effect= is_activated(actuator_type)
                & is_activated(actuator2_type)
    )
    actions_list.append(cancel_out_actuator)

    save_energy = Action(
        "save_energy",
        parameters=[actuator_type, room_type],
        precondition=actuator_is_part_of_room(actuator_type, room_type)
                    & ~is_occupied(room_type)
                    & ~will_become_occupied(room_type)
                    & is_activated(actuator_type),
        effect=~is_activated(actuator_type)
    )
    actions_list.append(save_energy)

    return actions_list
