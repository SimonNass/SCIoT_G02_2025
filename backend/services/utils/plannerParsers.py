
def parse_values_lama_first(plan_result):
    """Parse results from lama-first planner"""
    output = plan_result.get('output', {})

    plan_actions = []
    cost = None
    planner_time = None
    stdout = plan_result.get('stdout', '')
    sas_plan = ""

    if 'sas_plan' in output:
        sas_plan = output.get('sas_plan', '')
                    
        # Parse the plan from sas_plan string
        if sas_plan:
            lines = sas_plan.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith(';'):
                    # Remove parentheses and split by spaces
                    action = line.strip('()')
                    plan_actions.append(action)
                    
        # Extract cost from the comment in sas_plan
        if '; cost = ' in sas_plan:
            try:
                cost_line = [line for line in sas_plan.split('\n') if '; cost = ' in line][0]
                cost = int(cost_line.split('cost = ')[1].split(' ')[0])
            except (IndexError, ValueError):
                cost = len(plan_actions)  # fallback to plan length
                    
        # Extract planner time from stdout
        if 'Planner time: ' in stdout:
            try:
                time_line = [line for line in stdout.split('\n') if 'Planner time: ' in line][0]
                time_str = time_line.split('Planner time: ')[1].strip()
                # Remove suffix
                planner_time = float(time_str.rstrip('s'))
            except (IndexError, ValueError):
                planner_time = None

    return plan_actions, cost, planner_time, sas_plan

def parse_values_delfi(plan_result):
    """Parse results from delfi planner"""
    output = plan_result.get('output', {})

    plan_actions = []
    cost = None
    planner_time = None
    stdout = plan_result.get('stdout', '')
    
    plan_str = output.get('plan', '')
    
    # Parse the plan from plan string
    if plan_str:
        lines = plan_str.strip().split('\n')
        for line in lines:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith(';'):
                # Check if it's an action (starts and ends with parentheses)
                if line.startswith('(') and line.endswith(')'):
                    action = line.strip('()')
                    plan_actions.append(action)
        
        # Extract cost from the plan string itself
        if '; cost = ' in plan_str:
            try:
                cost_line = [line for line in plan_str.split('\n') if '; cost = ' in line][0]
                cost_part = cost_line.split('cost = ')[1]
                cost = int(cost_part.split(' ')[0])
            except (IndexError, ValueError):
                cost = len(plan_actions)  # fallback
    
    # Extract planner time from stdout
    if 'Total time: ' in stdout:
        try:
            time_line = [line for line in stdout.split('\n') if 'Total time: ' in line][0]
            time_str = time_line.split('Total time: ')[1].strip()
            planner_time = float(time_str.rstrip('s'))
        except (IndexError, ValueError):
            # Try alternative format "Overall time: [0.210s CPU, 0.233s wall-clock]"
            if 'Overall time: ' in stdout:
                try:
                    time_line = [line for line in stdout.split('\n') if 'Overall time: ' in line][0]
                    # Extract wall-clock time
                    wall_clock_part = time_line.split('wall-clock')[0]
                    time_str = wall_clock_part.split()[-1].rstrip('s')
                    planner_time = float(time_str)
                except (IndexError, ValueError):
                    planner_time = None
            else:
                planner_time = None

    return plan_actions, cost, planner_time, plan_str

    
def parse_values_dual_bfws_ffparser(plan_result):
    """Parse results from dual-bfws-ffparser planner"""
    output = plan_result.get('output', {})

    plan_actions = []
    cost = None
    planner_time = None
    stdout = plan_result.get('stdout', '')

    plan_str = output.get('plan', '')
                    
    # Parse the plan from plan string
    if 'plan' in output:
        if plan_str:
            lines = plan_str.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and line.startswith('(') and line.endswith(')'):
                    # Remove parentheses
                    action = line.strip('()')
                    plan_actions.append(action)
        
        # Extract cost from stdout
        if 'Plan found with cost: ' in stdout:
            try:
                cost_line = [line for line in stdout.split('\n') if 'Plan found with cost: ' in line][0]
                cost = int(cost_line.split('Plan found with cost: ')[1].strip())
            except (IndexError, ValueError):
                cost = len(plan_actions)  # fallback to plan length
        
        # Extract planner time from stdout
        if 'Total time: ' in stdout:
            try:
                time_line = [line for line in stdout.split('\n') if 'Total time: ' in line][0]
                time_str = time_line.split('Total time: ')[1].strip()
                planner_time = float(time_str)
            except (IndexError, ValueError):
                planner_time = None

    return plan_actions, cost, planner_time, plan_str