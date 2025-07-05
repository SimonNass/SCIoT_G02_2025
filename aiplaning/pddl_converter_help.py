#!/usr/bin/env python

# pip install pddl==0.4.3
from typing import Dict, List
from pddl import parse_domain, parse_problem

def iterator_ofer_dict_list_elements(keys: List[str], key_to_element_lists: Dict[str,List[str]]):
    for key in keys:
        for element in key_to_element_lists[key]:
            yield element

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
