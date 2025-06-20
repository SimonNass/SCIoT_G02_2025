#!/usr/bin/env python

# TODO 
# make an issue with minimal example (:requirements :typing :adl) does not work without the :typing

# pip install pddl
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
    }

    # set up variables and constants
    #object = variables("object", types=["object"])
    floor = variables("floor", types=["floor"])[0]
    room = variables("room", types=["room"])[0]
    room_position = variables("room_position", types=["room_position"])[0]
    iot = variables("iot", types=["iot"])[0]
    cleaning_team = variables("cleaning_team", types=["cleaning_team"])[0]
    iot = variables("iot", types=["iot"])[0]
    sensor = variables("sensor", types=["sensor"])[0]
    actuator = variables("actuator", types=["actuator"])[0]
    
    binary_s, numerical_s, textual_s = variables("binary_s numerical_s textual_s", types=["sensor"])
    binary_a, numerical_a, textual_a = variables("binary_s numerical_s textual_s", types=["actuator"])

    # define predicates
    predicates_list = []
    room_is_part_of_floor = Predicate("room_is_part_of_floor", room, floor)
    predicates_list.append(room_is_part_of_floor)
    sensor_is_part_of_room = Predicate("sensor_is_part_of_room", sensor, room)
    predicates_list.append(sensor_is_part_of_room)
    is_ocupied = Predicate("is_ocupied", room)
    predicates_list.append(is_ocupied)
    is_cleaned = Predicate("is_cleaned", room)
    predicates_list.append(is_cleaned)
    actuator_is_part_of_room = Predicate("actuator_is_part_of_room", actuator, room)
    predicates_list.append(actuator_is_part_of_room)
    is_activated = Predicate("is_activated", actuator)
    predicates_list.append(is_activated)

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
    requirements = [Requirements.STRIPS, Requirements.TYPING]
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
    floors = create_objects(number_floors, "floor")
    all_objekts = all_objekts + floors

    number_rooms = 10
    rooms = create_objects(number_rooms, "room")
    all_objekts = all_objekts + rooms

    number_cleaning_teams = 2
    cleaning_teams = create_objects(number_cleaning_teams, "cleaning_team")
    all_objekts = all_objekts + cleaning_teams

    number_actuators = 2
    actuators = create_objects(number_cleaning_teams, "actuator")
    all_objekts = all_objekts + actuators

    # create initial state
    initial_state = []
    
    rooms_per_floor = [5, 5]
    comulative_rooms_bevore = [sum(rooms_per_floor[:i]) for i in range(len(rooms_per_floor))]
    #print (comulative_rooms_bevore)
    for i in range(len(floors)):
        for j in range(rooms_per_floor[i]):
            next_room_floor_mapping = room_is_part_of_floor(rooms[comulative_rooms_bevore[i]+j], floors[i])
            initial_state.append(next_room_floor_mapping)


    # create goal
    goal_state = ''

    goal_for_ocupied_rooms = None

    if_case = base.And(base.Not(is_ocupied(room)))
    then_clean_case = is_cleaned(room)
    then_actuators_off_case = base.ForallCondition(base.Imply(actuator_is_part_of_room(actuator, room),base.Not(is_activated(actuator))),actuators)
    implication_for_unocupied_rooms = base.Imply(if_case, base.And(then_clean_case,then_actuators_off_case))
    goal_for_unocupied_rooms = base.ForallCondition(implication_for_unocupied_rooms, rooms)

    envorce_checks = None
    goal_state = base.And(goal_for_unocupied_rooms) #base.Imply(is_ocupied(rooms[0]),is_ocupied(rooms[1]))

    problem = Problem(
        problem_name,
        domain=domain,
        requirements=domain.requirements,
        objects=all_objekts,
        init=initial_state,
        goal=goal_state
    )
    
    print(problem)

def main():
    domaine_file_name = 'domain.pddl'
    problem_file_name = 'problem.pddl'
    
    #domain = parse_domain(domaine_file_name)
    #print(domain)
    #problem = parse_problem(problem_file_name)
    #print(problem)

    #d = create_domain()
    #create_problem("test", domain)
    create()


if __name__ == '__main__':
    main()