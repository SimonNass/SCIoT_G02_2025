#!/usr/bin/env python

# TODO 
# make an issue with minimal example (:requirements :typing :adl) does not work without the :typing

# pip install pddl==0.4.3
from pddl.logic import Predicate, constants, variables, base
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.requirements import Requirements
from pddl import parse_domain, parse_problem

def create_objects(amount: int, type_name: str):
    names = ''
    for i in range(amount):
        names = names + str(f'{type_name}_{i} ')

    objects = constants(names, type_=type_name + '_type')
    return objects

def create():
#def create_domain():
    domain_name = "test_SCIoT_G02_2025"

    # set up types
    type_dict = {
        "object_type": None,

        "floor_type": "object_type",
        "room_type": "object_type",
        "room_position_type": "object_type",
        "iot_type": "object_type",
        "cleaning_team_type": "object_type",
        
        "sensor_type": "iot_type",
        "actuator_type": "iot_type",

        "binary_s_type": "sensor_type",
        "numerical_s_type": "sensor_type",
        "textual_s_type": "sensor_type",

        "binary_a_type": "actuator_type",
        "numerical_a_type": "actuator_type",
        "textual_a_type": "actuator_type",

        "button_s_type": "binary_s_type",
        "motion_s_type": "binary_s_type",
        "virtual_switch_s_type": "binary_s_type",

        "temperature_s_type": "numerical_s_type",
        "humidity_s_type": "numerical_s_type",
        "light_s_type": "numerical_s_type",
        "sound_s_type": "numerical_s_type",
        "rotation_s_type": "numerical_s_type",
        "virtual_dimmer_s_type": "numerical_s_type",

        "switch_a_type": "binary_a_type",
        "light_switch_a_type": "binary_a_type",
        "virtual_switch_a_type": "binary_a_type",

        "light_dimmer_a_type": "numerical_a_type",
        "virtual_dimmer_a_type": "numerical_a_type",

        "display_a_type": "textual_a_type",
    }

    # set up variables and constants
    floor_type, floor2_type = variables("floor_type floor2_type", types=["floor_type"])
    room_type, room2_type, room3_type = variables("room_type room2_type room3_type", types=["room_type"])
    room_position_type = variables("room_position_type", types=["room_position_type"])[0]
    iot_type = variables("iot_type", types=["iot_type"])[0]
    cleaning_team_type = variables("cleaning_team_type", types=["cleaning_team_type"])[0]

    sensor_type = variables("sensor_type", types=["sensor_type"])[0]
    actuator_type = variables("actuator_type", types=["actuator_type"])[0]
    
    binary_s_type, numerical_s_type, textual_s_type = variables("binary_s_type numerical_s_type textual_s_type", types=["sensor_type"])
    binary_a_type, numerical_a_type, textual_a_type = variables("binary_a_type numerical_a_type textual_a_type", types=["actuator_type"])

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

    is_ocupied = Predicate("is_ocupied", room_type)
    predicates_list.append(is_ocupied)

    will_become_ocupied = Predicate("will_become_ocupied", room_type)
    predicates_list.append(will_become_ocupied)

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

    # define actions
    actions_list = []
    move_to_floor = Action(
        "move_to_floor",
        parameters=[cleaning_team_type, room_type, room2_type, floor_type, floor2_type],
        precondition=is_at(cleaning_team_type,room_type)
                    & (base.Or(is_next_to(room_type, room2_type), is_next_to(room2_type, room_type))) 
                    & room_is_part_of_floor(room_type, floor_type) 
                    & room_is_part_of_floor(room2_type, floor2_type),
                    #& base.Not(=(floor_type, floor2_type)),
        effect=~is_at(cleaning_team_type,room_type) & is_at(cleaning_team_type,room2_type)
    )
    actions_list.append(move_to_floor)

    move_to_room = Action(
        "move_to_room",
        parameters=[cleaning_team_type, room_type, room2_type, floor_type],
        precondition=is_at(cleaning_team_type,room_type)
                    & (base.Or(is_next_to(room_type, room2_type), is_next_to(room2_type, room_type))) 
                    & room_is_part_of_floor(room_type, floor_type) 
                    & room_is_part_of_floor(room2_type, floor_type),
        effect=~is_at(cleaning_team_type,room_type) & is_at(cleaning_team_type,room2_type)
    )
    actions_list.append(move_to_room)

    move_to_isolated_room = Action(
        "move_to_isolated_room",
        parameters=[cleaning_team_type, room_type, room2_type, floor_type],
        precondition=is_at(cleaning_team_type,room_type)
                    & (base.ForallCondition((base.Or(~is_next_to(room3_type, room2_type), ~is_next_to(room2_type, room3_type))) , [room3_type])) 
                    & room_is_part_of_floor(room_type, floor_type) 
                    & room_is_part_of_floor(room2_type, floor_type),
        effect=~is_at(cleaning_team_type,room_type) & is_at(cleaning_team_type,room2_type)
    )
    actions_list.append(move_to_isolated_room)

    team_clean = Action(
        "team_clean",
        parameters=[cleaning_team_type, room_type],
        precondition=is_at(cleaning_team_type,room_type)
                    & ~is_cleaned(room_type) 
                    & ~is_ocupied(room_type) 
                    & ~will_become_ocupied(room_type),
        effect=is_cleaned(room_type) 
    )
    actions_list.append(team_clean)

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

    turn_on = Action(
        "turn_on",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~fulfilled_activity(room_type, room_position_type)
                    & positioned_at(sensor_type, room_position_type)
                    & sensor_is_part_of_room(sensor_type, room_type)
                    & actuator_increases_sensor(actuator_type, sensor_type)
                    #& base.Or(is_ocupied(room_type), will_become_ocupied(room_type))
                    & ~is_sensing(sensor_type)
                    & ~is_activated(actuator_type),
        effect=is_sensing(sensor_type) & is_activated(actuator_type)
    )
    actions_list.append(turn_on)

    turn_off = Action(
        "turn_off",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~fulfilled_activity(room_type, room_position_type)
                    & positioned_at(sensor_type, room_position_type)
                    & sensor_is_part_of_room(sensor_type, room_type)
                    & actuator_increases_sensor(actuator_type, sensor_type)
                    #& base.Or(is_ocupied(room_type), will_become_ocupied(room_type))
                    & is_sensing(sensor_type)
                    & is_activated(actuator_type),
        effect=~is_sensing(sensor_type) & ~is_activated(actuator_type)
    )
    actions_list.append(turn_off)

    turn_on_inverted = Action(
        "turn_on_inverted",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~fulfilled_activity(room_type, room_position_type)
                    & positioned_at(sensor_type, room_position_type)
                    & sensor_is_part_of_room(sensor_type, room_type)
                    & actuator_decreases_sensor(actuator_type, sensor_type)
                    #& base.Or(is_ocupied(room_type), will_become_ocupied(room_type))
                    & ~is_sensing(sensor_type)
                    & is_activated(actuator_type),
        effect=is_sensing(sensor_type) & ~is_activated(actuator_type)
    )
    actions_list.append(turn_on_inverted)

    turn_off_inverted = Action(
        "turn_off_inverted",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~fulfilled_activity(room_type, room_position_type)
                    & positioned_at(sensor_type, room_position_type)
                    & sensor_is_part_of_room(sensor_type, room_type)
                    & actuator_decreases_sensor(actuator_type, sensor_type)
                    #& base.Or(is_ocupied(room_type), will_become_ocupied(room_type))
                    & is_sensing(sensor_type)
                    & ~is_activated(actuator_type),
        effect=~is_sensing(sensor_type) & is_activated(actuator_type)
    )
    actions_list.append(turn_off_inverted)

    increase_s_by_a_in_r = Action(
        "increase_s_by_a_in_r",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~fulfilled_activity(room_type, room_position_type)
                    & positioned_at(sensor_type, room_position_type)
                    & sensor_is_part_of_room(sensor_type, room_type)
                    & actuator_increases_sensor(actuator_type, sensor_type)
                    #& base.Or(is_ocupied(room_type), will_become_ocupied(room_type))
                    & is_low(sensor_type)
                    & ~is_activated(actuator_type),
        effect=~is_low(sensor_type) & is_ok(sensor_type) & is_activated(actuator_type)
    )
    actions_list.append(increase_s_by_a_in_r)

    increase_s_by_na_in_r = Action(
        "increase_s_by_na_in_r",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~fulfilled_activity(room_type, room_position_type)
                    & positioned_at(sensor_type, room_position_type)
                    & sensor_is_part_of_room(sensor_type, room_type)
                    & actuator_decreases_sensor(actuator_type, sensor_type)
                    #& base.Or(is_ocupied(room_type), will_become_ocupied(room_type))
                    & is_low(sensor_type)
                    & is_activated(actuator_type),
        effect=~is_low(sensor_type) & is_ok(sensor_type) & ~is_activated(actuator_type)
    )
    actions_list.append(increase_s_by_na_in_r)

    decrease_s_by_a_in_r = Action(
        "decrease_s_by_a_in_r",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~fulfilled_activity(room_type, room_position_type)
                    & positioned_at(sensor_type, room_position_type)
                    & sensor_is_part_of_room(sensor_type, room_type)
                    & actuator_decreases_sensor(actuator_type, sensor_type)
                    #& base.Or(is_ocupied(room_type), will_become_ocupied(room_type))
                    & is_high(sensor_type)
                    & ~is_activated(actuator_type),
        effect=~is_high(sensor_type) & is_ok(sensor_type) & is_activated(actuator_type)
    )
    actions_list.append(decrease_s_by_a_in_r)

    decrease_s_by_na_in_r = Action(
        "decrease_s_by_na_in_r",
        parameters=[sensor_type, actuator_type, room_type, room_position_type],
        precondition=~fulfilled_activity(room_type, room_position_type)
                    & positioned_at(sensor_type, room_position_type)
                    & sensor_is_part_of_room(sensor_type, room_type)
                    & actuator_increases_sensor(actuator_type, sensor_type)
                    #& base.Or(is_ocupied(room_type), will_become_ocupied(room_type))
                    & is_high(sensor_type)
                    & is_activated(actuator_type),
        effect=~is_high(sensor_type) & is_ok(sensor_type) & ~is_activated(actuator_type)
    )
    actions_list.append(decrease_s_by_na_in_r)

    is_doing_read_at = is_doing_activitys_at['read']
    is_doing_bath_at = is_doing_activitys_at['bath']
    is_doing_sleep_at = is_doing_activitys_at['sleep']

    detect_activity = Action(
        "detect_activity",
        parameters=[room_type, room_position_type],
        precondition=base.Or(is_doing_read_at(room_type, room_position_type), is_doing_bath_at(room_type, room_position_type), is_doing_sleep_at(room_type, room_position_type)),
        effect=has_specified_activity_at(room_type, room_position_type)
    )
    actions_list.append(detect_activity)

    detect_no_activity = Action(
        "detect_no_activity",
        parameters=[room_type, room_position_type],
        precondition=base.And(~is_doing_read_at(room_type, room_position_type), ~is_doing_bath_at(room_type, room_position_type), ~is_doing_sleep_at(room_type, room_position_type)),
        effect=~has_specified_activity_at(room_type, room_position_type)
    )
    actions_list.append(detect_no_activity)

    fulfill_activity_bath = Action(
        "fulfill_activity_bath",
        parameters=[sensor_type, room_type, room_position_type],
        precondition=positioned_at(sensor_type, room_position_type)
                    & sensor_is_part_of_room(sensor_type, room_type)
                    & is_doing_bath_at(room_type, room_position_type),
        effect=fulfilled_activity(room_type, room_position_type)
    )
    actions_list.append(fulfill_activity_bath)

    fulfill_activity_read = Action(
        "fulfill_activity_read",
        parameters=[sensor_type, room_type, room_position_type],
        precondition=positioned_at(sensor_type, room_position_type)
                    & sensor_is_part_of_room(sensor_type, room_type)
                    & is_doing_read_at(room_type, room_position_type),
        effect=fulfilled_activity(room_type, room_position_type)
    )
    actions_list.append(fulfill_activity_read)

    fulfill_activity_sleep = Action(
        "fulfill_activity_sleep",
        parameters=[sensor_type, room_type, room_position_type],
        precondition=positioned_at(sensor_type, room_position_type)
                    & sensor_is_part_of_room(sensor_type, room_type)
                    & is_doing_sleep_at(room_type, room_position_type),
        effect=fulfilled_activity(room_type, room_position_type)
    )
    actions_list.append(fulfill_activity_sleep)

    fulfill_no_activity = Action(
        "fulfill_no_activity",
        parameters=[room_type, room_position_type],
        precondition=~has_specified_activity_at(room_type, room_position_type)
                    & ~is_doing_read_at(room_type, room_position_type)
                    & ~is_doing_bath_at(room_type, room_position_type)
                    & ~is_doing_sleep_at(room_type, room_position_type),
        effect=fulfilled_activity(room_type, room_position_type)
    )
    actions_list.append(fulfill_no_activity)

    #cancle_out_actuator = Action(
    #    "cancle_out_actuator",
    #    parameters=[room_type, room_position_type],
    #    precondition=,
    #    effect=
    #)
    #actions_list.append(cancle_out_actuator)

    save_energy = Action(
        "save_energy",
        parameters=[actuator_type, room_type],
        precondition=actuator_is_part_of_room(actuator_type, room_type)
                    & ~is_ocupied(room_type)
                    & ~will_become_ocupied(room_type)
                    & is_activated(actuator_type),
        effect=~is_activated(actuator_type)
    )
    actions_list.append(save_energy)

    # define the domain object.
    requirements = [Requirements.STRIPS, Requirements.TYPING, Requirements.ADL]
    domain = Domain(domain_name,
                    requirements=requirements,
                    types=type_dict,
                    predicates=predicates_list,
                    actions=actions_list)

    print(domain)

    problem_name = 'test'

    # create objects / constants
    all_objekts = []

    number_floors = 2
    number_rooms = 3
    number_cleaning_teams = 2
    number_sensors = 2
    number_actuators = 2
    names_room_positions = ['overall_room', 'bed', 'closet', 'window']
    rooms_per_floor = [2, 1]
    
    floors = create_objects(number_floors, "floor")
    all_objekts = all_objekts + floors

    rooms = create_objects(number_rooms, "room")
    all_objekts = all_objekts + rooms

    cleaning_teams = create_objects(number_cleaning_teams, "cleaning_team")
    all_objekts = all_objekts + cleaning_teams

    sensors = create_objects(number_sensors, "numerical_s")
    all_objekts = all_objekts + sensors

    actuators = create_objects(number_actuators, "actuator")
    all_objekts = all_objekts + actuators

    room_positions = create_objects(len(names_room_positions), "room_position")
    all_objekts = all_objekts + room_positions

    # create initial state
    initial_state = []
    
    comulative_rooms_bevore = [sum(rooms_per_floor[:i]) for i in range(len(rooms_per_floor))]
    #print (comulative_rooms_bevore)
    for i in range(len(rooms_per_floor)):
        for j in range(rooms_per_floor[i]):
            next_room_floor_mapping = room_is_part_of_floor(rooms[comulative_rooms_bevore[i]+j], floors[i])
            initial_state.append(next_room_floor_mapping)

    clean_starting_room = rooms[0]
    for cleaning_team in cleaning_teams:
        next_is_at = is_at(cleaning_team, clean_starting_room)
        initial_state.append(next_is_at)

    # iot to room papping
    sensor_room = rooms[0]
    for sensor_object in sensors:
        print (sensor_object.type_tags)
        print (sensor_room.type_tags)
        next_part_of_room = sensor_is_part_of_room(sensor_object, sensor_room)
        initial_state.append(next_part_of_room)

    actuator_room = rooms[0]
    for actuator_object in actuators:
        next_part_of_room = actuator_is_part_of_room(actuator_object, actuator_room)
        initial_state.append(next_part_of_room)

    # sensor actuator mapping
    for actuator_object in actuators:
        for sensor_object in sensors:
            if True:
                next_influence = actuator_increases_sensor(actuator_object, sensor_object)
                initial_state.append(next_influence)
            if False:
                next_influence = actuator_decreases_sensor(actuator_object, sensor_object)
                initial_state.append(next_influence)

    # iot position mapping
    room_positions_default = room_positions[0]
    for sensor_object in sensors:
        next_pos = positioned_at(sensor_object, room_positions_default)
        initial_state.append(next_pos)

    for actuator_object in actuators:
        next_pos = positioned_at(actuator_object, room_positions_default)
        initial_state.append(next_pos)

    # context
    # raw sensor data
    
    for sensor_object in sensors:
        state = is_high(sensor_object)
        initial_state.append(state)

    for actuator_object in actuators:
        state = is_activated(actuator_object)
        initial_state.append(state)

    #for room_o in rooms:
    #    initial_state.append(base.Not(is_ocupied(room_o)))
    #initial_state.append(base.Not(is_ocupied(rooms[0])))
    initial_state.append(is_ocupied(rooms[1]))


    # create goal
    goal_state = None

    goal_for_ocupied_rooms = None

    if_case1 = base.And(base.Not(is_ocupied(room_type)))
    then_clean_case = is_cleaned(room_type)
    clean_unocupied_rooms = base.ForallCondition(base.Imply(if_case1, then_clean_case), [room_type])

    if_case2 = base.And(base.Not(is_ocupied(room_type)), actuator_is_part_of_room(actuator_type, room_type))
    then_turn_off_actuator = base.Not(is_activated(actuator_type))
    actuator_off_unocupied_rooms = base.ForallCondition(base.Imply(if_case2, then_turn_off_actuator), [room_type, actuator_type])

    envorce_checks = base.ForallCondition(fulfilled_activity(room_type, room_position_type), [room_type, room_position_type])

    goal_state = base.And(clean_unocupied_rooms, actuator_off_unocupied_rooms, envorce_checks)

    problem = Problem(
        problem_name,
        domain=domain,
        requirements=domain.requirements,
        
        objects=all_objekts,
        init=initial_state,
        goal=is_cleaned(rooms[0])
        #goal=goal_state
    )
    
    print(problem)
    return domain, problem

def main():
    domaine_file_name = 'test_domain.pddl'
    problem_file_name = 'test_problem.pddl'
    
    #domain = parse_domain(domaine_file_name)
    #print(domain)
    #problem = parse_problem(problem_file_name)
    #print(problem)

    d, p = create()
    
    with open(domaine_file_name,'w') as f:
        f.write(d.__str__())
    
    with open(problem_file_name,'w') as f:
        f.write(p.__str__())


if __name__ == '__main__':
    main()