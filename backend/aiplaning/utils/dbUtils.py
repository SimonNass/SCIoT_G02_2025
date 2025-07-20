from backend.models.models import Floor, Room, Device, PlanScope, PDDLPlan, PlanStep
from backend.extensions import db
import logging
from typing import Dict, Optional

def get_floor_uids(room_number=None):
    """Get list of all floor IDs from database."""
    from flask import current_app
    with current_app.app_context():
        if room_number is not None:
            # Get floor ID for the specific room
            room = Room.query.filter_by(room_number=room_number).first()
            if room:
                return [room.floor_id]
            else:
                return []
        else:
            floors_ids = Floor.query.with_entities(Floor.id).all()
            return [floor_id for (floor_id,) in floors_ids]

def get_room_uids_per_floor(room_number=None):
    """Get dictionary mapping floor IDs to their room IDs."""
    from flask import current_app
    with current_app.app_context():
        if room_number is not None:
            # Get only the specific room and its floor
            room = Room.query.filter_by(room_number=room_number).first()
            if room:
                return {room.floor_id: [room.id]}
            else:
                return {}
        else:
            room_floor_data = Room.query.with_entities(Room.id, Room.floor_id).all()
            
            room_uids_per_floor = {}
            for room_id, floor_id in room_floor_data:
                if floor_id not in room_uids_per_floor:
                    room_uids_per_floor[floor_id] = []
                room_uids_per_floor[floor_id].append(room_id)

            return room_uids_per_floor
    
def get_room_occupied_initial_values(room_number=None):
    """Get dictionary of room IDs and their occupation status."""
    from flask import current_app
    with current_app.app_context():
        if room_number is not None:
            # Get only the specific room
            room = Room.query.filter_by(room_number=room_number).first()
            if room:
                return {room.id: room.is_occupied}
            else:
                return {}
        else:
            room_data = db.session.query(Room.id, Room.is_occupied).all()
            return {room_id: is_occupied for room_id, is_occupied in room_data}

def get_sensor_room_mapping(room_number=None):
    """Get dictionary mapping room IDs to their sensor device IDs."""
    from flask import current_app
    with current_app.app_context():
        if room_number is not None:
            # Get sensors only for the specific room
            room = Room.query.filter_by(room_number=room_number).first()
            if room:
                sensor_data = db.session.query(Device.device_id, Device.room_id).filter_by(
                    device_type='sensor', is_online=True, room_id=room.id
                ).all()
            else:
                sensor_data = []
        else:
            sensor_data = db.session.query(Device.device_id, Device.room_id).filter_by(device_type='sensor', is_online=True).all()

        sensor_room_mapping = {}
        for device_id, room_id in sensor_data:
            if room_id not in sensor_room_mapping:
                sensor_room_mapping[room_id] = []
            sensor_room_mapping[room_id].append(device_id)

        return sensor_room_mapping
    
def get_actuator_room_mapping(room_number=None):
    """Get dictionary mapping room IDs to their actuator device IDs."""
    from flask import current_app
    with current_app.app_context():
        if room_number is not None:
            # Get actuators only for the specific room
            room = Room.query.filter_by(room_number=room_number).first()
            if room:
                actuator_data = db.session.query(Device.device_id, Device.room_id).filter_by(
                    device_type='actuator', is_online=True, room_id=room.id
                ).all()
            else:
                actuator_data = []
        else:
            actuator_data = db.session.query(Device.device_id, Device.room_id).filter_by(device_type='actuator', is_online=True).all()
        
        actuator_room_mapping = {}
        for device_id, room_id in actuator_data:
            if room_id not in actuator_room_mapping:
                actuator_room_mapping[room_id] = []
            actuator_room_mapping[room_id].append(device_id)
        
        return actuator_room_mapping
    
def get_sensor_types(room_number=None):
    """Get dictionary mapping sensor device IDs to their type names."""
    from flask import current_app
    with current_app.app_context():
        if room_number is not None:
            # Get sensor types only for the specific room
            room = Room.query.filter_by(room_number=room_number).first()
            if room:
                sensor_data = db.session.query(Device.device_id, Device.ai_planing_type).filter_by(
                    device_type='sensor', is_online=True, room_id=room.id
                ).all()
            else:
                sensor_data = []
        else:
            sensor_data = db.session.query(Device.device_id, Device.ai_planing_type).filter_by(device_type='sensor', is_online=True).all()
        
        return {device_id: ai_planing_type for device_id, ai_planing_type in sensor_data}
    
def get_sensor_initial_values(room_number=None):
    """Get dictionary mapping sensor IDs to their last simplified values."""
    from flask import current_app
    with current_app.app_context():
        if room_number is not None:
            # Get sensor values only for the specific room
            room = Room.query.filter_by(room_number=room_number).first()
            if room:
                sensor_data = db.session.query(Device.device_id, Device.last_value_simplified).filter_by(
                    device_type='sensor', is_online=True, room_id=room.id
                ).all()
            else:
                sensor_data = []
        else:
            sensor_data = db.session.query(Device.device_id, Device.last_value_simplified).filter_by(device_type='sensor', is_online=True).all()
        
        sensor_values = {}
        for device_id, last_value_simplified in sensor_data:
            # Use last_value_simplified if available, otherwise default to 0
            value = last_value_simplified if last_value_simplified is not None else 0
            sensor_values[device_id] = value
        
        return sensor_values


def get_actuator_initial_values(room_number=None):
    """Get dictionary mapping actuator IDs to their current state (on/off)."""
    from flask import current_app
    with current_app.app_context():
        if room_number is not None:
            # Get actuator values only for the specific room
            room = Room.query.filter_by(room_number=room_number).first()
            if room:
                actuator_data = db.session.query(Device.device_id, Device.is_off).filter_by(
                    device_type='actuator', is_online=True, room_id=room.id
                ).all()
            else:
                actuator_data = []
        else:
            actuator_data = db.session.query(Device.device_id, Device.is_off).filter_by(device_type='actuator', is_online=True).all()
        
        actuator_values = {}
        for device_id, is_off in actuator_data:
            if is_off is None:
                is_off = True
            actuator_values[device_id] = is_off

        # invert from is_off in db and gateway to is activated in ai planner
        for device_id, is_off in actuator_values.items():
            actuator_values[device_id] = not is_off
        
        return actuator_values
    
def save_to_database(
        plan_data: Dict,
        planner_used: str,
        cleaning_plan: list,
        filtered_plan: list,
        detected_activity_plan: list,
        scope: PlanScope = PlanScope.BUILDING,
        target_room_number: Optional[str] = None,
        ):
    """
    Save a PDDL plan to the database
    
    Args:
        plan_data: Dictionary containing plan data from solve_planning_problem
        scope: The scope of the plan (building, floor, or room)
        cleaning_plan: cleaning plan parsed from pddl_converter_execution
        detected_activity_plan: cleaning plan parsed from pddl_converter_execution
        filtered_plan: filtered plan pared frompddl_converter_execution
        planner_used: Name of the planner that was used
        target_floor_id: Optional floor ID if scope is floor or room
        target_room_id: Optional room ID if scope is room
    
    Returns:
        The saved PDDLPlan object or None if failed
    """
    from flask import current_app
    with current_app.app_context():
        try:
            target_room_id = None
            
            if target_room_number is not None:
                room = Room.query.filter_by(room_number=target_room_number).first()
                if room:
                    target_room_id = room.id
                else:
                    logging.warning(f"Room with number {target_room_number} not found")

            plan = PDDLPlan(
                scope=scope,
                target_floor_id=None,
                target_room_id=target_room_id,
                total_cost=plan_data.get('cost'),
                planning_time=plan_data.get('time'),
                planner_used=planner_used,
                raw_plan=plan_data.get('raw_plan', ''),
                cleaning_plan=cleaning_plan,
                filtered_plan=filtered_plan,
                detected_activity_plan=detected_activity_plan
            )

            db.session.add(plan)
            db.session.flush() 

            # Create Plan steps
            for step_order, action_list in enumerate(filtered_plan):
                # Extract action name (first element) and parameters (remaining elements)
                action_name = action_list[0] if action_list else ''
                parameter_list = action_list[1:] if len(action_list) > 1 else []
                
                # Create raw_step string by joining the list elements (to match original format)
                raw_step = ' '.join(action_list)
                
                plan_step = PlanStep(
                    plan_id=plan.id,
                    step_order=step_order,
                    action_name=action_name,
                    raw_step=raw_step,
                    target_device_ids=parameter_list 
                )
                
                db.session.add(plan_step)

            db.session.commit()

            # Refresh the object to ensure all relationships are loaded
            db.session.refresh(plan)
            
            # Load the steps relationship before returning
            _ = plan.steps  # This triggers loading of the relationship
            
            logging.info(f"Plan saved to database with ID: {plan.id}")
            return plan
        except Exception as e:
            logging.error(f"Failed to save plan after AI Planning to database: {e}")
            db.session.rollback()
            return None
