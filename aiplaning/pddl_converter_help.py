#!/usr/bin/env python

# pip install pddl==0.4.3
from typing import Dict, List
from pddl.logic import constants
from pddl import parse_domain, parse_problem

def iterator_rooms_per_floor(floor_uids: List[str], room_uids_per_floor: Dict[str,List[str]]):
    for floor in floor_uids:
        for room in room_uids_per_floor[floor]:
            yield room

def reading_in_pddl():
    domaine_file_name = 'domain.pddl'
    problem_file_name = 'problem.pddl'

    domain = parse_domain(domaine_file_name)
    print(domain)
    problem = parse_problem(problem_file_name)
    print(problem)

def check_lib_versions():
    import pddl
    version_pddl = pddl.__version__
    print(version_pddl)
    # make sure that it is above 0.4.2
