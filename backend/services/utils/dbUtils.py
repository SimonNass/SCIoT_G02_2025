from backend.models.models import PDDLPlan, PlanStep, PlanScope
from typing import Dict, Optional
import logging
from flask import jsonify

logger = logging.getLogger(__name__)

def save_plan_to_database(
    plan_data: Dict,
    planner_used: str,
    scope: PlanScope = PlanScope.BUILDING,
    target_floor_id: Optional[str] = None,
    target_room_id: Optional[str] = None
) -> Optional[PDDLPlan]:
    """
    Save a PDDL plan to the database
    
    Args:
        plan_data: Dictionary containing plan data from solve_planning_problem
        scope: The scope of the plan (building, floor, or room)
        planner_used: Name of the planner that was used
        target_floor_id: Optional floor ID if scope is floor or room
        target_room_id: Optional room ID if scope is room
    
    Returns:
        The saved PDDLPlan object or None if failed
    """
    # import inside the function to avoid circular imports
    from backend.extensions import db

    try:
        # Create the main plan record
        plan = PDDLPlan(
            scope=scope,
            target_floor_id=target_floor_id,
            target_room_id=target_room_id,
            total_cost=plan_data.get('cost'),
            planning_time=plan_data.get('time'),
            planner_used=planner_used,
            raw_plan=plan_data.get('raw_plan', '')
        )
        
        db.session.add(plan)
        db.session.flush()  # Get the plan ID
        
        # Create plan steps
        plan_actions = plan_data.get('plan', [])
        logging.info(f"Plan actions: {plan_actions}")
        for step_order, action in enumerate(plan_actions):
            # Parse action string to extract action name and parameters
            action_parts = action.strip().split()
            action_name = action_parts[0] if action_parts else ''
            parameter_list = action_parts[1:] if len(action_parts) > 1 else []
            
            plan_step = PlanStep(
                plan_id=plan.id,
                step_order=step_order,
                action_name=action_name,
                raw_step=action,
                target_device_ids=parameter_list
            )
            
            db.session.add(plan_step)
        
        db.session.commit()
        logger.info(f"Plan saved to database with ID: {plan.id}")
        return plan
        
    except Exception as e:
        logger.error(f"Failed to save plan to database: {e}")
        db.session.rollback()
        return None