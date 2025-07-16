from backend.models.models import Floor, Room, Device
from backend.extensions import db
import logging

def get_floor_uids():
    """Get list of all floor IDs from database."""
    from flask import current_app
    with current_app.app_context():
        floors_ids = Floor.query.with_entities(Floor.id).all()
        return [floor_id for (floor_id,) in floors_ids]

def get_room_uids_per_floor():
    """Get dictionary mapping floor IDs to their room IDs."""
    from flask import current_app
    with current_app.app_context():
        room_floor_data = Room.query.with_entities(Room.id, Room.floor_id).all()
        
        room_uids_per_floor = {}
        for room_id, floor_id in room_floor_data:
            if floor_id not in room_uids_per_floor:
                room_uids_per_floor[floor_id] = []
            room_uids_per_floor[floor_id].append(room_id)

        return room_uids_per_floor
    
def get_room_occupied_initial_values():
    """Get dictionary of room IDs and their occupation status."""
    from flask import current_app
    with current_app.app_context():
        room_data = db.session.query(Room.id, Room.is_occupied).all()
        return {room_id: is_occupied for room_id, is_occupied in room_data}
    
def get_sensor_room_mapping():
    """Get dictionary mapping room IDs to their sensor device IDs."""
    from flask import current_app
    with current_app.app_context():
        sensor_data = db.session.query(Device.device_id, Device.room_id).filter_by(device_type='sensor').all()

        sensor_room_mapping = {}
        for device_id, room_id in sensor_data:
            if room_id not in sensor_room_mapping:
                sensor_room_mapping[room_id] = []
            sensor_room_mapping[room_id].append(device_id)

        return sensor_room_mapping
    
def get_actuator_room_mapping():
    """Get dictionary mapping room IDs to their actuator device IDs."""
    from flask import current_app
    with current_app.app_context():
        actuator_data = db.session.query(Device.device_id, Device.room_id).filter_by(device_type='actuator').all()
        
        actuator_room_mapping = {}
        for device_id, room_id in actuator_data:
            if room_id not in actuator_room_mapping:
                actuator_room_mapping[room_id] = []
            actuator_room_mapping[room_id].append(device_id)
        
        return actuator_room_mapping
    
def get_sensor_types():
    """Get dictionary mapping sensor device IDs to their type names."""
    from flask import current_app
    with current_app.app_context():
        sensor_data = db.session.query(Device.device_id, Device.ai_planing_type).filter_by(device_type='sensor').all()
        return {device_id: ai_planing_type for device_id, ai_planing_type in sensor_data}
    
def get_sensor_initial_values():
    """Get dictionary mapping sensor IDs to their last simplified values."""
    from flask import current_app
    with current_app.app_context():
        sensor_data = db.session.query(Device.device_id, Device.last_value_simplified).filter_by(device_type='sensor').all()
        
        sensor_values = {}
        for device_id, last_value_simplified in sensor_data:
            # Use last_value_simplified if available, otherwise default to 0
            value = last_value_simplified if last_value_simplified is not None else 0
            sensor_values[device_id] = value
        
        return sensor_values


def get_actuator_initial_values():
    """Get dictionary mapping actuator IDs to their current state (on/off)."""
    from flask import current_app
    with current_app.app_context():
        actuator_data = db.session.query(Device.device_id, Device.is_off).filter_by(device_type='actuator').all()
        
        actuator_values = {}
        for device_id, is_off in actuator_data:
            if is_off is None:
                is_off = True
            actuator_values[device_id] = is_off
        
        return actuator_values