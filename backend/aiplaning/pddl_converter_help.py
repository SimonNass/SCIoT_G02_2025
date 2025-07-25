#!/usr/bin/env python
"""Module specifies miscelenius helper functions to hide some complexity in the main file."""

# pip install pddl==0.4.3
import os
from typing import Dict, List
import pddl
from pddl import parse_domain, parse_problem

def iterator_ofer_dict_list_elements(keys: List[str], key_to_element_lists: Dict[str,List[str]]):
    for key in keys:
        for element in key_to_element_lists[key]:
            yield element

def write_out_pddl(output_path, file_name, pddl_structure):
    os.makedirs(output_path, exist_ok=True)
    fime_path = os.path.join(output_path, file_name)
    if os.path.exists(fime_path):
        os.rename(fime_path, os.path.join(output_path, "old_version_" + file_name ))
    with open(fime_path,'w', encoding="utf8") as f:
        f.write(str(pddl_structure))

def reading_in_pddl():
    domaine_file_name = 'domain.pddl'
    problem_file_name = 'problem.pddl'

    domain = parse_domain(domaine_file_name)
    print(domain)
    problem = parse_problem(problem_file_name)
    print(problem)

def check_lib_versions():
    version_pddl = pddl.__version__
    print(f"You have PDDL Parser version {version_pddl} and you need at least version 0.4.3.")
    # make sure that it is above 0.4.2
