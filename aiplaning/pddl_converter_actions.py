#!/usr/bin/env python
"""Module specifies the actions of a pddl domain file."""

# pip install pddl==0.4.3
from typing import List, Dict

from pddl.logic import base, variables
from pddl.logic.predicates import EqualTo
from pddl.action import Action


def create_cleaning_actions(predicates_dict: Dict[str,variables], pddl_variable_types: Dict[str,List[variables]]):
    actions_list = []

    floor_type = pddl_variable_types["floor"][0]
    floor2_type = pddl_variable_types["floor"][1]
    room_type = pddl_variable_types["room"][0]
    room2_type = pddl_variable_types["room"][1]
    room3_type = pddl_variable_types["room"][2]
    cleaning_team_type = pddl_variable_types["cleaning_team"][0]

    room_is_part_of_floor = predicates_dict["room_is_part_of_floor"]
    is_next_to = predicates_dict["is_next_to"]
    is_at = predicates_dict["is_at"]
    is_occupied = predicates_dict["is_occupied"]
    will_become_occupied = predicates_dict["will_become_occupied"]
    is_cleaned = predicates_dict["is_cleaned"]

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

def create_assign_actions(predicates_dict: Dict[str,variables], pddl_variable_types: Dict[str,List[variables]]):
    actions_list = []

    floor_type = pddl_variable_types["floor"][0]
    floor2_type = pddl_variable_types["floor"][1]
    room_type = pddl_variable_types["room"][0]
    room_position_type = pddl_variable_types["room_position"][0]
    iot_type = pddl_variable_types["iot"][0]
    sensor_type = pddl_variable_types["sensor"][0]
    actuator_type = pddl_variable_types["actuator"][0]

    room_is_part_of_floor = predicates_dict["room_is_part_of_floor"]
    positioned_at = predicates_dict["positioned_at"]
    actuator_increases_sensor = predicates_dict["actuator_increases_sensor"]
    actuator_decreases_sensor = predicates_dict["actuator_decreases_sensor"]
    is_locked = predicates_dict["is_locked"]

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

    assign_lock_for_sensor = Action(
        "assign_lock_for_sensor",
        parameters=[sensor_type],
        precondition=base.ForallCondition(base.And(base.Not(actuator_increases_sensor(actuator_type, sensor_type)),base.Not(actuator_decreases_sensor(actuator_type, sensor_type))), [actuator_type]),
        effect=is_locked(sensor_type)
    )
    actions_list.append(assign_lock_for_sensor)

    return actions_list

def create_actuator_actions_binary_sensors(predicates_dict: Dict[str,variables], pddl_variable_types: Dict[str,List[variables]]):
    actions_list = []

    room_type = pddl_variable_types["room"][0]
    room_position_type = pddl_variable_types["room_position"][0]
    binary_s_type = pddl_variable_types["binary_s"][0]
    actuator_type = pddl_variable_types["actuator"][0]

    sensor_is_part_of_room = predicates_dict["sensor_is_part_of_room"]
    positioned_at = predicates_dict["positioned_at"]
    actuator_increases_sensor = predicates_dict["actuator_increases_sensor"]
    actuator_decreases_sensor = predicates_dict["actuator_decreases_sensor"]
    is_sensing = predicates_dict["is_sensing"]
    is_activated = predicates_dict["is_activated"]
    is_changed = predicates_dict["is_changed"]
    is_locked = predicates_dict["is_locked"]

    # construct compound predicates
    works_together = lambda s1, p1, r1 : positioned_at(s1, p1) & sensor_is_part_of_room(s1, r1) & ~is_locked(s1)

    # for binary sensors
    params_numerical=[binary_s_type, actuator_type, room_type, room_position_type]

    for increase, activated_a in [(True,True),(False,True),(True,False),(False,False)]:
        action_name = ("increase" if increase ^ (not activated_a) else "decrease")
        action_name = action_name + "_s_binary_by"
        action_name = action_name + ("_activating" if activated_a else "_deactivating")
        pre = base.And(works_together(binary_s_type, room_position_type, room_type), ~is_changed(actuator_type))
        if increase:
            pre = base.And(pre, actuator_increases_sensor(actuator_type, binary_s_type))
        else:
            pre = base.And(pre, actuator_decreases_sensor(actuator_type, binary_s_type))
        if increase ^ (not activated_a):
            pre = base.And(pre, ~is_sensing(binary_s_type))
            eff = base.And(is_sensing(binary_s_type))
        else:
            pre = base.And(pre, is_sensing(binary_s_type))
            eff = base.And(~is_sensing(binary_s_type))
        if activated_a:
            pre = base.And(pre, ~is_activated(actuator_type))
            eff = base.And(eff, is_activated(actuator_type))
        else:
            pre = base.And(pre, is_activated(actuator_type))
            eff = base.And(eff, ~is_activated(actuator_type))

        binary_sensor_actuator_change = Action(
            action_name,
            parameters=params_numerical,
            precondition=pre,
            effect=eff
        )
        actions_list.append(binary_sensor_actuator_change)

    for increase, change_a in [(True,True),(False,True),(True,False),(False,False)]:
        action_name = ("increase" if increase ^ (not change_a) else "decrease")
        action_name = action_name + "_s_binary_by"
        action_name = action_name + ("_change" if change_a else "_reverse_change")
        pre = base.And(works_together(binary_s_type, room_position_type, room_type), is_activated(actuator_type))
        if increase:
            pre = base.And(pre, actuator_increases_sensor(actuator_type, binary_s_type))
        else:
            pre = base.And(pre, actuator_decreases_sensor(actuator_type, binary_s_type))
        if increase ^ (not change_a):
            pre = base.And(pre, ~is_sensing(binary_s_type))
            eff = base.And(is_sensing(binary_s_type))
        else:
            pre = base.And(pre, is_sensing(binary_s_type))
            eff = base.And(~is_sensing(binary_s_type))
        if change_a:
            pre = base.And(pre, ~is_changed(actuator_type))
            eff = base.And(eff, is_changed(actuator_type))
        else:
            pre = base.And(pre, is_changed(actuator_type))
            eff = base.And(eff, ~is_changed(actuator_type))

        binary_sensor_actuator_change = Action(
            action_name,
            parameters=params_numerical,
            precondition=pre,
            effect=eff
        )
        actions_list.append(binary_sensor_actuator_change)

    return actions_list

def create_actuator_actions_numerical_sensors(predicates_dict: Dict[str,variables], pddl_variable_types: Dict[str,List[variables]]):
    actions_list = []

    room_type = pddl_variable_types["room"][0]
    room_position_type = pddl_variable_types["room_position"][0]
    numerical_s_type = pddl_variable_types["numerical_s"][0]
    actuator_type = pddl_variable_types["actuator"][0]

    sensor_is_part_of_room = predicates_dict["sensor_is_part_of_room"]
    positioned_at = predicates_dict["positioned_at"]
    actuator_increases_sensor = predicates_dict["actuator_increases_sensor"]
    actuator_decreases_sensor = predicates_dict["actuator_decreases_sensor"]
    is_activated = predicates_dict["is_activated"]
    is_changed = predicates_dict["is_changed"]
    is_locked = predicates_dict["is_locked"]

    # construct compound predicates
    works_together = lambda s1, p1, r1 : positioned_at(s1, p1) & sensor_is_part_of_room(s1, r1) & ~is_locked(s1)

    # for numerical sensors
    params_numerical=[numerical_s_type, actuator_type, room_type, room_position_type]
    sensor_buckets_sortet = ['is_low','is_ok','is_high']

    for i in range(len(sensor_buckets_sortet) - 1):
        curent_state = predicates_dict[sensor_buckets_sortet[i]]
        next_state = predicates_dict[sensor_buckets_sortet[i + 1]]
        for increase, activated_a in [(True,True),(False,True),(True,False),(False,False)]:
            action_name = ("increase" if increase ^ (not activated_a) else "decrease")
            action_name = action_name + "_s_numerical"
            action_name = action_name + f"_{sensor_buckets_sortet[i]}_to_{sensor_buckets_sortet[i + 1]}"
            action_name = action_name + ("_activating" if activated_a else "_deactivating")
            pre = base.And(works_together(numerical_s_type, room_position_type, room_type), ~is_changed(actuator_type))
            if increase:
                pre = base.And(pre, actuator_increases_sensor(actuator_type, numerical_s_type))
            else:
                pre = base.And(pre, actuator_decreases_sensor(actuator_type, numerical_s_type))
            if increase ^ (not activated_a):
                pre = base.And(pre, curent_state(numerical_s_type))
                eff = base.And(~curent_state(numerical_s_type), next_state(numerical_s_type))
            else:
                pre = base.And(pre, next_state(numerical_s_type))
                eff = base.And(~next_state(numerical_s_type), curent_state(numerical_s_type))
            if activated_a:
                pre = base.And(pre, ~is_activated(actuator_type))
                eff = base.And(eff, is_activated(actuator_type))
            else:
                pre = base.And(pre, is_activated(actuator_type))
                eff = base.And(eff, ~is_activated(actuator_type))

            numerical_sensor_actuator_change = Action(
                action_name,
                parameters=params_numerical,
                precondition=pre,
                effect=eff
            )
            actions_list.append(numerical_sensor_actuator_change)

    for i in range(len(sensor_buckets_sortet) - 1):
        curent_state = predicates_dict[sensor_buckets_sortet[i]]
        next_state = predicates_dict[sensor_buckets_sortet[i + 1]]
        for increase, change_a in [(True,True),(False,True),(True,False),(False,False)]:
            action_name = ("increase" if increase ^ (not change_a) else "decrease")
            action_name = action_name + "_s_numerical"
            action_name = action_name + f"_{sensor_buckets_sortet[i]}_to_{sensor_buckets_sortet[i + 1]}"
            action_name = action_name + ("_change" if change_a else "_reverse_change")
            pre = base.And(works_together(numerical_s_type, room_position_type, room_type), is_activated(actuator_type))
            if increase:
                pre = base.And(pre, actuator_increases_sensor(actuator_type, numerical_s_type))
            else:
                pre = base.And(pre, actuator_decreases_sensor(actuator_type, numerical_s_type))
            if increase ^ (not change_a):
                pre = base.And(pre, curent_state(numerical_s_type))
                eff = base.And(~curent_state(numerical_s_type), next_state(numerical_s_type))
            else:
                pre = base.And(pre, next_state(numerical_s_type))
                eff = base.And(~next_state(numerical_s_type), curent_state(numerical_s_type))
            if change_a:
                pre = base.And(pre, ~is_changed(actuator_type))
                eff = base.And(eff, is_changed(actuator_type))
            else:
                pre = base.And(pre, is_changed(actuator_type))
                eff = base.And(eff, ~is_changed(actuator_type))

            numerical_sensor_actuator_change = Action(
                action_name,
                parameters=params_numerical,
                precondition=pre,
                effect=eff
            )
            actions_list.append(numerical_sensor_actuator_change)

    remove_actuator_change_flag = Action(
        "remove_actuator_change_flag",
        parameters=[actuator_type],
        precondition=is_changed(actuator_type),
        effect=base.Not(is_changed(actuator_type))
    )
    actions_list.append(remove_actuator_change_flag)

    return actions_list

def create_activity_detection_actions_x(predicates_dict: Dict[str,variables], pddl_variable_types: Dict[str,List[variables]], activity_mapping: Dict[str,Dict[str,str]], activity_name: str):
    actions_list = []

    room_type = pddl_variable_types["room"][0]
    room_position_type = pddl_variable_types["room_position"][0]
    binary_s_type = pddl_variable_types["binary_s"][0]

    sensor_is_part_of_room = predicates_dict["sensor_is_part_of_room"]
    positioned_at = predicates_dict["positioned_at"]
    is_sensing = predicates_dict["is_sensing"]
    is_low = predicates_dict["is_low"]
    is_ok = predicates_dict["is_ok"]
    is_high = predicates_dict["is_high"]
    is_activated = predicates_dict["is_activated"]
    is_locked = predicates_dict["is_locked"]
    checked_all_activitys = predicates_dict["checked_all_activitys"]

    fulfilled_activity_sleep = predicates_dict["fulfilled_activity_sleep"]
    fulfilled_activity_read = predicates_dict["fulfilled_activity_read"]

    is_doing_read_at = predicates_dict["is_doing_read_at"]
    is_doing_sleep_at = predicates_dict["is_doing_sleep_at"]

    checked_activity_sleep = predicates_dict["checked_activity_sleep"]
    checked_activity_read = predicates_dict["checked_activity_read"]

    # TODO fine tune sensor detection for the activitys
    detect_activity_sleep = Action(
        "detect_activity_sleep",
        parameters=[binary_s_type, room_type, room_position_type],
        precondition=is_sensing(binary_s_type)
                    & positioned_at(binary_s_type, room_position_type)
                    & sensor_is_part_of_room(binary_s_type, room_type)
                    & ~checked_activity_sleep(room_type, room_position_type),
        effect=checked_activity_sleep(room_type, room_position_type) & is_doing_sleep_at(room_type, room_position_type) & ~fulfilled_activity_sleep(room_type, room_position_type)
    )
    actions_list.append(detect_activity_sleep)

    detect_no_activity_sleep = Action(
        "detect_no_activity_sleep",
        parameters=[binary_s_type, room_type, room_position_type],
        precondition=~is_sensing(binary_s_type)
                    & positioned_at(binary_s_type, room_position_type)
                    & sensor_is_part_of_room(binary_s_type, room_type)
                    & ~checked_activity_sleep(room_type, room_position_type),
        effect=checked_activity_sleep(room_type, room_position_type) & ~is_doing_sleep_at(room_type, room_position_type) & ~fulfilled_activity_sleep(room_type, room_position_type)
    )
    actions_list.append(detect_no_activity_sleep)

    detect_no_possible_activity_sleep = Action(
        "detect_no_possible_activity_sleep",
        parameters=[room_type, room_position_type],
        precondition=base.Not(base.ExistsCondition(positioned_at(binary_s_type, room_position_type)
                                                    & sensor_is_part_of_room(binary_s_type, room_type), [binary_s_type]))
                    & ~checked_activity_sleep(room_type, room_position_type),
        effect=checked_activity_sleep(room_type, room_position_type) & ~is_doing_sleep_at(room_type, room_position_type) & ~fulfilled_activity_sleep(room_type, room_position_type)
    )
    actions_list.append(detect_no_possible_activity_sleep)

    detect_activity_read = Action(
        "detect_activity_read",
        parameters=[binary_s_type, room_type, room_position_type],
        precondition=is_sensing(binary_s_type)
                    & positioned_at(binary_s_type, room_position_type)
                    & sensor_is_part_of_room(binary_s_type, room_type)
                    & ~checked_activity_read(room_type, room_position_type),
        effect=checked_activity_read(room_type, room_position_type) & is_doing_read_at(room_type, room_position_type) & ~fulfilled_activity_read(room_type, room_position_type)
    )
    actions_list.append(detect_activity_read)

    detect_no_activity_read = Action(
        "detect_no_activity_read",
        parameters=[binary_s_type, room_type, room_position_type],
        precondition=~is_sensing(binary_s_type)
                    & positioned_at(binary_s_type, room_position_type)
                    & sensor_is_part_of_room(binary_s_type, room_type)
                    & ~checked_activity_read(room_type, room_position_type),
        effect=checked_activity_read(room_type, room_position_type) & ~is_doing_read_at(room_type, room_position_type) & ~fulfilled_activity_read(room_type, room_position_type)
    )
    actions_list.append(detect_no_activity_read)

    detect_no_possible_activity_read = Action(
        "detect_no_possible_activity_read",
        parameters=[room_type, room_position_type],
        precondition=base.Not(base.ExistsCondition(positioned_at(binary_s_type, room_position_type)
                                                    & sensor_is_part_of_room(binary_s_type, room_type), [binary_s_type]))
                    & ~checked_activity_read(room_type, room_position_type),
        effect=checked_activity_read(room_type, room_position_type) & ~is_doing_read_at(room_type, room_position_type) & ~fulfilled_activity_read(room_type, room_position_type)
    )
    actions_list.append(detect_no_possible_activity_read)

    return actions_list

def create_activity_detection_actions(predicates_dict: Dict[str,variables], pddl_variable_types: Dict[str,List[variables]], activity_mapping: Dict[str,Dict[str,str]]):
    actions_list = []

    room_type = pddl_variable_types["room"][0]
    room_position_type = pddl_variable_types["room_position"][0]

    checked_all_activitys = predicates_dict["checked_all_activitys"]

    for activity_name in activity_mapping.keys():
        detection_activity_x = create_activity_detection_actions_x(predicates_dict, pddl_variable_types, activity_mapping, activity_name)
        actions_list.append(detection_activity_x)


    detect_all_activitys_pre = base.And(~checked_all_activitys(room_type, room_position_type))
    for activity in activity_mapping.keys():
        detect_all_activitys_pre = base.And(predicates_dict[f"checked_activity_{activity}"](room_type, room_position_type))
    detect_all_activitys = Action(
        "detect_all_activitys",
        parameters=[room_type, room_position_type],
        precondition=detect_all_activitys_pre,
        effect=checked_all_activitys(room_type, room_position_type)
    )
    actions_list.append(detect_all_activitys)

    return actions_list

def create_activity_fulfilled_action_x(predicates_dict: Dict[str,variables], pddl_variable_types: Dict[str,List[variables]], activity_name: str, sensor_type_x_dict: Dict[str, str]):

    room_type: variables = pddl_variable_types["room"][0]
    room_position_type: variables = pddl_variable_types["room_position"][0]

    sensor_is_part_of_room: variables = predicates_dict["sensor_is_part_of_room"]
    positioned_at: variables = predicates_dict["positioned_at"]
    is_locked: variables = predicates_dict["is_locked"]
    checked_all_activitys: variables = predicates_dict["checked_all_activitys"]

    param = [room_type, room_position_type]
    for sensor_type_x in sensor_type_x_dict.keys():
        param.append(pddl_variable_types[sensor_type_x][0])

    pre = base.And(checked_all_activitys(room_type, room_position_type), predicates_dict[f"is_doing_{activity_name}_at"](room_type, room_position_type), base.Not(predicates_dict[f"fulfilled_activity_{activity_name}"](room_type, room_position_type)))
    for sensor_type_x, expected_value in sensor_type_x_dict.items():
        sensor_object_type = pddl_variable_types[sensor_type_x][0]
        pre = base.And(pre, positioned_at(sensor_object_type, room_position_type))
        pre = base.And(pre, sensor_is_part_of_room(sensor_object_type, room_type))
        pre = base.And(pre, predicates_dict[expected_value](sensor_object_type))

    eff = predicates_dict[f"fulfilled_activity_{activity_name}"](room_type, room_position_type)
    for sensor_type_x in sensor_type_x_dict.keys():
        eff = base.And(eff, is_locked(pddl_variable_types[sensor_type_x][0]))

    fulfill_activity_x = Action(
        f"fulfill_activity_{activity_name}",
        parameters=param,
        precondition=pre,
        effect=eff
    )

    return fulfill_activity_x

def create_activity_fulfilled_actions(predicates_dict, pddl_variable_types, activity_mapping: Dict[str,Dict[str,str]]):
    actions_list = []

    room_type = pddl_variable_types["room"][0]
    room_position_type = pddl_variable_types["room_position"][0]

    checked_all_activitys = predicates_dict["checked_all_activitys"]
    fulfilled_activitys = predicates_dict["fulfilled_activitys"]

    fulfilled_activity_sleep = predicates_dict["fulfilled_activity_sleep"]
    fulfilled_activity_read = predicates_dict["fulfilled_activity_read"]

    # TODO add or for sensor state
    # TODO check activitc colisions

    for activity_name, sensor_type_x_dict in activity_mapping.items():
        fulfill_activity_x = create_activity_fulfilled_action_x(predicates_dict, pddl_variable_types, activity_name, sensor_type_x_dict)
        actions_list.append(fulfill_activity_x)

    for activity in activity_mapping.keys():
        fulfill_activity_no_x = Action(
            f"fulfill_activity_no_{activity}",
            parameters=[room_type, room_position_type],
            precondition=checked_all_activitys(room_type, room_position_type)
                        & ~predicates_dict[f"is_doing_{activity}_at"](room_type, room_position_type)
                        & ~predicates_dict[f"fulfilled_activity_{activity}"](room_type, room_position_type),
            effect=predicates_dict[f"fulfilled_activity_{activity}"](room_type, room_position_type)
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

def create_energy_saving_actions(predicates_dict: Dict[str,variables], pddl_variable_types: Dict[str,List[variables]]):
    actions_list = []

    room_type = pddl_variable_types["room"][0]
    sensor_type = pddl_variable_types["sensor"][0]
    actuator_type = pddl_variable_types["actuator"][0]
    actuator2_type = pddl_variable_types["actuator"][1]

    sensor_is_part_of_room = predicates_dict["sensor_is_part_of_room"]
    actuator_is_part_of_room = predicates_dict["actuator_is_part_of_room"]
    actuator_increases_sensor = predicates_dict["actuator_increases_sensor"]
    actuator_decreases_sensor = predicates_dict["actuator_decreases_sensor"]
    is_occupied = predicates_dict["is_occupied"]
    will_become_occupied = predicates_dict["will_become_occupied"]
    is_activated = predicates_dict["is_activated"]
    is_changed = predicates_dict["is_changed"]

    # TODO these will never trigger since it makes the kost optimisation worse without a benefit the planer can see
    cancel_out_actuator = Action(
        "cancel_out_actuator_off",
        parameters=[sensor_type, actuator_type, actuator2_type, room_type],
        precondition= base.Not(EqualTo(actuator_type, actuator2_type))
                        & sensor_is_part_of_room(sensor_type, room_type)
                        & actuator_increases_sensor(actuator_type, sensor_type)
                        & actuator_decreases_sensor(actuator2_type, sensor_type)
                        & is_activated(actuator_type)
                        & is_activated(actuator2_type)
                        & ~is_changed(actuator_type)
                        & ~is_changed(actuator2_type),
        effect= ~is_activated(actuator_type)
                & ~is_activated(actuator2_type)
    )
    actions_list.append(cancel_out_actuator)

    # TODO these will never trigger since it makes the kost optimisation worse without a benefit the planer can see
    cancel_out_actuator = Action(
        "cancel_out_actuator_changed",
        parameters=[sensor_type, actuator_type, actuator2_type, room_type],
        precondition= base.Not(EqualTo(actuator_type, actuator2_type))
                        & sensor_is_part_of_room(sensor_type, room_type)
                        & actuator_increases_sensor(actuator_type, sensor_type)
                        & actuator_decreases_sensor(actuator2_type, sensor_type)
                        & is_activated(actuator_type)
                        & is_activated(actuator2_type)
                        & is_changed(actuator_type)
                        & is_changed(actuator2_type),
        effect= ~is_changed(actuator_type)
                & ~is_changed(actuator2_type)
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

def create_actions(predicates_dict: Dict[str,variables], pddl_variable_types: Dict[str,List[variables]], activity_mapping: Dict[str,Dict[str,str]]):
    actions_list = []

    actions_list = actions_list + create_cleaning_actions(predicates_dict, pddl_variable_types)
    actions_list = actions_list + create_assign_actions(predicates_dict, pddl_variable_types)
    actions_list = actions_list + create_actuator_actions_binary_sensors(predicates_dict, pddl_variable_types)
    actions_list = actions_list + create_actuator_actions_numerical_sensors(predicates_dict, pddl_variable_types)
    actions_list = actions_list + create_activity_detection_actions(predicates_dict, pddl_variable_types)
    actions_list = actions_list + create_activity_fulfilled_actions(predicates_dict, pddl_variable_types, activity_mapping)
    actions_list = actions_list + create_energy_saving_actions(predicates_dict, pddl_variable_types)

    return actions_list
