#!/usr/bin/env python

# TODO 
# make an issue with minimal example (:requirements :typing :adl) does not work without the :typing

# pip install pddl==0.4.3
from pddl.logic import Predicate, constants, variables, base
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.requirements import Requirements
from pddl import parse_domain, parse_problem

def create_objects(amount: int, type: str):
    names = ''
    for i in range(amount):
        names = names + str(f'{type}_{i} ')

    objects = constants(names, type_=type)
    return objects

def create():
#def create_domain():
    domain_name = "SCIoT_G02_2025"

    # set up types
    type_dict = {
        "object": None,

        "floor": "object",
        "room": "object",
        "room_position": "object",
        "iot": "object",
        "cleaning_team": "object",
        
        "sensor": "iot",
        "actuator": "iot",

        "binary_s": "sensor",
        "numerical_s": "sensor",
        "textual_s": "sensor",

        "binary_a": "actuator",
        "numerical_a": "actuator",
        "textual_a": "actuator",

        "button_s": "binary_s",
        "motion_s": "binary_s",
        "virtual_switch_s": "binary_s",

        "temperature_s": "numerical_s",
        "humidity_s": "numerical_s",
        "light_s": "numerical_s",
        "sound_s": "numerical_s",
        "rotation_s": "numerical_s",
        "virtual_dimmer_s": "numerical_s",

        "switch_a": "binary_a",
        "light_switch_a": "binary_a",
        "virtual_switch_a": "binary_a",

        "light_dimmer_a": "numerical_a",
        "virtual_dimmer_a": "numerical_a",

        "display_a": "textual_a",
    }

    # set up variables and constants
    floor = variables("floor", types=["floor"])[0]
    room, room2 = variables("room room2", types=["room"])
    room_position = variables("room_position", types=["room_position"])[0]
    iot = variables("iot", types=["iot"])[0]
    cleaning_team = variables("cleaning_team", types=["cleaning_team"])[0]

    sensor = variables("sensor", types=["sensor"])[0]
    actuator = variables("actuator", types=["actuator"])[0]
    
    binary_s, numerical_s, textual_s = variables("binary_s numerical_s textual_s", types=["sensor"])
    binary_a, numerical_a, textual_a = variables("binary_a numerical_a textual_a", types=["actuator"])

    # define predicates
    predicates_list = []

    # topology
    room_is_part_of_floor = Predicate("room_is_part_of_floor", room, floor)
    predicates_list.append(room_is_part_of_floor)

    sensor_is_part_of_room = Predicate("sensor_is_part_of_room", sensor, room)
    predicates_list.append(sensor_is_part_of_room)
    actuator_is_part_of_room = Predicate("actuator_is_part_of_room", actuator, room)
    predicates_list.append(actuator_is_part_of_room)
    # problem to lock down a sensor that is part of two room positions
    positioned_at = Predicate("positioned_at", iot, room_position)
    predicates_list.append(positioned_at)

    actuator_increases_sensor = Predicate("actuator_increases_sensor", actuator, sensor)
    predicates_list.append(actuator_increases_sensor)
    actuator_decreases_sensor = Predicate("actuator_decreases_sensor", actuator, sensor)
    predicates_list.append(actuator_decreases_sensor)

    is_next_to = Predicate("is_next_to", room, room2)
    predicates_list.append(is_next_to)

    is_at = Predicate("is_at", cleaning_team, room2)
    predicates_list.append(is_at)

    # meta context

    is_ocupied = Predicate("is_ocupied", room)
    predicates_list.append(is_ocupied)

    will_become_ocupied = Predicate("will_become_ocupied", room)
    predicates_list.append(will_become_ocupied)

    is_cleaned = Predicate("is_cleaned", room)
    predicates_list.append(is_cleaned)

    # activity
    has_specified_activity_at = Predicate("has_specified_activity_at", room, room_position)
    predicates_list.append(has_specified_activity_at)
    
    activity_names = ['read','sleep']
    is_doing_activitys_at = {}
    for activity in activity_names:
        is_doing_a_at = Predicate(f"is_doing_{activity}_at", room, room_position)
        is_doing_activitys_at.update({f"is_doing_{activity}_at":is_doing_a_at})
        predicates_list.append(is_doing_a_at)

    # sensors
    is_sensing = Predicate("is_sensing", sensor)
    predicates_list.append(is_sensing)

    is_low = Predicate("is_low", numerical_s)
    predicates_list.append(is_low)
    is_ok = Predicate("is_ok", numerical_s)
    predicates_list.append(is_ok)
    is_high = Predicate("is_high", numerical_s)
    predicates_list.append(is_high)

    # actuators
    is_activated = Predicate("is_activated", actuator)
    predicates_list.append(is_activated)

    # force checks predicate
    fulfilled_activity = Predicate("fulfilled_activity", room, room_position)
    predicates_list.append(fulfilled_activity)

    # define actions
    actions_list = []
    a1 = Action(
        "action-1",
        parameters=[room, floor, sensor],
        precondition=sensor_is_part_of_room(sensor, room) & ~room_is_part_of_floor(room, floor),
        effect=room_is_part_of_floor(room, floor)
    )
    actions_list.append(a1)

    # define the domain object.
    requirements = [Requirements.STRIPS, Requirements.TYPING, Requirements.ADL]
    domain = Domain(domain_name,
                    requirements=requirements,
                    types=type_dict,
                    predicates=predicates_list,
                    actions=actions_list)

    print(domain)
    #return domain

#def create_problem(problem_name: str, domain: Domain):
    problem_name = 'test'

    # create objects / constants
    all_objekts = []

    number_floors = 2
    number_rooms = 10
    number_cleaning_teams = 2
    number_sensors = 2
    number_actuators = 2
    names_room_positions = ['overall_room', 'bed', 'closet', 'window']
    rooms_per_floor = [5, 5]
    
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
    #sensor_room = rooms[0]
    #for sensor_object in sensors:
    #    print (sensor_object.type_tag)
    #    print (sensor_room.type_tag)
    #    next_part_of_room = sensor_is_part_of_room(sensor_object, sensor_room)
    #    initial_state.append(next_part_of_room)

    #actuator_room = rooms[0]
    #for actuator_object in actuators:
        #next_part_of_room = actuator_is_part_of_room(actuator_object, actuator_room)
        #initial_state.append(next_part_of_room)

    # sensor actuator mapping

    #for actuator_object in actuators:
    #    for sensor_object in sensors:
    #        if True:
    #            next_influence = actuator_increases_sensor(actuator_object, sensor_object)
    #            initial_state.append(next_influence)
    #        if False:
    #            next_influence = actuator_decreases_sensor(actuator_object, sensor_object)
    #            initial_state.append(next_influence)

    # iot position mapping
    #room_positions_default = room_positions[0]
    #for sensor_object in sensors:
    #    next_pos = positioned_at(sensor_object, room_positions_default)
    #    initial_state.append(next_pos)

    #for actuator_object in actuators:
    #    next_pos = positioned_at(actuator_object, room_positions_default)
    #    initial_state.append(next_pos)

    # context
    # raw sensor data
    
    #for sensor_object in sensors:
    #    state = is_high(sensor_object)
    #    initial_state.append(state)

    #for actuator_object in actuators:
    #    state = is_activated(actuator_object)
    #    initial_state.append(state)

    for room in rooms:
        initial_state.append(is_ocupied(room))


    # create goal
    goal_state = None

    goal_for_ocupied_rooms = None

    if_case = base.And(base.Not(is_ocupied(room)))
    then_clean_case = is_cleaned(room)
    turn_off_actuator = base.Imply(actuator_is_part_of_room(actuator, room),base.Not(is_activated(actuator)))
    then_actuators_off_case = base.ForallCondition(turn_off_actuator,[actuator])
    implication_for_unocupied_rooms = base.Imply(if_case, base.And(then_clean_case,then_actuators_off_case))
    goal_for_unocupied_rooms = base.ForallCondition(implication_for_unocupied_rooms, [room])

    envorce_checks = base.ForallCondition(base.ForallCondition(fulfilled_activity(room, room_position), [room_position]), [room])

    goal_state = base.And(goal_for_unocupied_rooms, envorce_checks) #base.Imply(is_ocupied(rooms[0]),is_ocupied(rooms[1]))

    problem = Problem(
        problem_name,
        domain=domain,
        requirements=domain.requirements,
        
        objects=all_objekts,
        init=initial_state,
        goal=goal_state
    )
    
    print(problem)
    return problem

def main():
    domaine_file_name = 'domain.pddl'
    problem_file_name = 'test_problem.pddl'
    
    #domain = parse_domain(domaine_file_name)
    #print(domain)
    #problem = parse_problem(problem_file_name)
    #print(problem)

    #d = create_domain()
    #create_problem("test", domain)
    p = create()
    
    with open(problem_file_name,'w') as f:
        f.write(p.__str__())


if __name__ == '__main__':
    main()