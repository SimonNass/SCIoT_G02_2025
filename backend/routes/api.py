from flask import Blueprint, jsonify, request
from backend.extensions import db
from backend.models import models
from sqlalchemy.exc import IntegrityError
from backend.routes.auth.simple_auth import require_api_key
from backend.mqtt.utils.mqttPublish import request_actuator_update, request_current_sensor_value

api = Blueprint('api', __name__)

@api.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

# Create floor with rooms (optional)
@api.route('/floors/create', methods=['POST'])
@require_api_key
def create_floor_with_rooms():
    """
    Create a floor with optional rooms
    Expected JSON format:
    {
        "floor_number": 1,
        "floor_name": "Ground Floor",
        "description": "Main lobby and reception",
        "rooms": [
            {
                "room_number": "101",
                "room_type": "Standard",
                "capacity": 2
            },
            {
                "room_number": "102", 
                "room_type": "Suite",
                "capacity": 4
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'floor_number' not in data:
            return jsonify({'error': 'floor_number is required'}), 400
        
        # Create floor
        floor = models.Floor(
            floor_number=data['floor_number'],
            floor_name=data.get('floor_name'),
            description=data.get('description'),
        )
        
        # Add rooms if provided
        rooms_data = data.get('rooms', [])
        for room_data in rooms_data:
            if 'room_number' not in room_data or 'room_type' not in room_data:
                return jsonify({'error': 'room_number and room_type are required for each room'}), 400
            
            room = models.Room(
                room_number=room_data['room_number'],
                room_type=room_data['room_type'],
                capacity=room_data.get('capacity', 2),
                is_occupied=room_data.get('is_occupied', False),
            )
            floor.rooms.append(room)
        
        db.session.add(floor)
        db.session.commit()
        
        return jsonify({
            'message': 'Floor created successfully',
            'floor': {
                'id': floor.id,
                'floor_number': floor.floor_number,
                'floor_name': floor.floor_name,
                'description': floor.description,
                'rooms_created': len(rooms_data)
            }
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Floor number already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Create rooms for existing floor
@api.route('/floors/<int:floor_number>/rooms/create', methods=['POST'])
@require_api_key
def create_rooms_for_floor(floor_number):
    """
    Create rooms for an existing floor
    Expected JSON format:
    {
        "rooms": [
            {
                "room_number": "103",
                "room_type": "Deluxe",
                "capacity": 3
            }
        ]
    }
    """
    try:
        # Check if floor exists
        floor = models.Floor.query.filter_by(floor_number=floor_number).first()
        if not floor:
            return jsonify({'error': f'Floor {floor_number} does not exist'}), 404
        
        data = request.get_json()
        if not data or 'rooms' not in data:
            return jsonify({'error': 'rooms array is required'}), 400
        
        rooms_data = data['rooms']
        if not isinstance(rooms_data, list) or len(rooms_data) == 0:
            return jsonify({'error': 'rooms must be a non-empty array'}), 400
        
        created_rooms = []
        for room_data in rooms_data:
            if 'room_number' not in room_data or 'room_type' not in room_data:
                return jsonify({'error': 'room_number and room_type are required for each room'}), 400
            
            room = models.Room(
                room_number=room_data['room_number'],
                room_type=room_data['room_type'],
                capacity=room_data.get('capacity', 2),
                is_occupied=room_data.get('is_occupied', False),
                floor_id=floor.id
            )
            
            db.session.add(room)
            created_rooms.append({
                'room_number': room.room_number,
                'room_type': room.room_type,
                'capacity': room.capacity
            })
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(created_rooms)} rooms created successfully for floor {floor_number}',
            'floor_number': floor_number,
            'created_rooms': created_rooms
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Room number already exists on this floor'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# List all floors with their rooms
@api.route('/floors/list', methods=['GET'])
@require_api_key
def list_all_floors():
    """Get all floors with their associated rooms"""
    try:
        floors = models.Floor.query.all()
        
        result = []
        for floor in floors:
            floor_data = {
                'id': floor.id,
                'floor_number': floor.floor_number,
                'floor_name': floor.floor_name,
                'description': floor.description,
                'created_at': floor.created_at.isoformat(),
                'rooms': []
            }
            
            for room in floor.rooms:
                room_data = {
                    'id': room.id,
                    'room_number': room.room_number,
                    'room_type': room.room_type,
                    'capacity': room.capacity,
                    'is_occupied': room.is_occupied,
                    'device_count': len(room.devices)
                }
                floor_data['rooms'].append(room_data)
            
            result.append(floor_data)
        
        return jsonify({
            'floors': result,
            'total_floors': len(result)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# List all rooms for a specific floor
@api.route('/floors/<int:floor_number>/rooms/list', methods=['GET'])
@require_api_key
def list_rooms_for_floor(floor_number):
    """Get all rooms for a specific floor by floor number"""
    try:
        floor = models.Floor.query.filter_by(floor_number=floor_number).first()
        if not floor:
            return jsonify({'error': f'Floor {floor_number} does not exist'}), 404
        
        rooms = []
        for room in floor.rooms:
            room_data = {
                'id': room.id,
                'room_number': room.room_number,
                'room_type': room.room_type,
                'capacity': room.capacity,
                'is_occupied': room.is_occupied,
                'last_cleaned': room.last_cleaned.isoformat() if room.last_cleaned else None,
                'is_cleaned': room.is_cleaned,
                'created_at': room.created_at.isoformat(),
                'devices': []
            }
            
            # Include device information
            for device in room.devices:
                device_data = {
                    'id': device.id,
                    'device_id': device.device_id,
                    'name': device.name,
                    'device_type': device.device_type,
                    'is_online': device.is_online,
                }
                room_data['devices'].append(device_data)
            
            rooms.append(room_data)
        
        return jsonify({
            'floor_number': floor_number,
            'floor_name': floor.floor_name,
            'rooms': rooms,
            'total_rooms': len(rooms)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/floors/<int:floor_number>/rooms/<string:room_number>/occupancy', methods=['POST'])
@require_api_key
def set_room_occupancy(floor_number, room_number):
    """
    Set occupancy status for a specific room
    Expected JSON format:
    {
        "is_occupied": true
    }
    """
    try: 
        # Check if floor exists
        floor = models.Floor.query.filter_by(floor_number=floor_number).first()
        if not floor:
            return jsonify({'error': f'Floor {floor_number} does not exist'}), 404
        
        # Check if room exists
        room = models.Room.query.filter_by(
            room_number=room_number, 
            floor_id=floor.id
        ).first()
        if not room:
            return jsonify({'error': f'Room {room_number} does not exist on floor {floor_number}'}), 404
        
        # Get request data
        data = request.get_json()
        if not data or 'is_occupied' not in data:
            return jsonify({'error': 'is_occupied is required'}), 400
        
        is_occupied = data['is_occupied']
        
        room.is_occupied = is_occupied
        db.session.commit()
        
        return jsonify({
            'message': f'Room {room_number} occupancy status updated successfully',
            'floor_number': floor_number,
            'room_number': room_number,
            'is_occupied': is_occupied
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/rooms/occupancy/list', methods=['POST'])   
@require_api_key
def bulk_update_room_occupancy():
    """
    Bulk update occupancy status for all rooms on a specific floor
    Expected JSON format:
    {
        "rooms": [
            {
                "room_number": "101",
                "is_occupied": true
            },
            {
                "room_number": "102",
                "is_occupied": false
            }
        ]
    }
    """
    try:    
        # Get request data
        data = request.get_json()
        if not data or 'rooms' not in data:
            return jsonify({'error': 'rooms array is required'}), 400
        
        rooms_data = data['rooms']
        if not isinstance(rooms_data, list) or len(rooms_data) == 0:
            return jsonify({'error': 'rooms must be a non-empty array'}), 400
        
        rooms_to_update = []
        # Check if rooms exist
        for room_data in rooms_data:
            if 'room_number' not in room_data or 'is_occupied' not in room_data:
                return jsonify({'error': 'room_number and is_occupied are required for each room'}), 400
            
            room = models.Room.query.filter_by(room_number=room_data['room_number']).first()
            if not room:
                return jsonify({'error': f'Room {room_data["room_number"]} does not exist'}), 404
            rooms_to_update.append(room)
        
        updated_rooms = []
        if not rooms_to_update:
            return jsonify({'error': 'No rooms to update'}), 400
        
        for room in rooms_to_update:
            room.is_occupied = room_data['is_occupied']
            db.session.add(room)
            
            updated_rooms.append({
                'room_number': room.room_number,
                'is_occupied': room.is_occupied
            })
        db.session.commit()
        
        return jsonify({
            'message': f'{len(updated_rooms)} rooms occupancy status updated successfully',
            'updated_rooms': updated_rooms
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500  

@api.route('/devices/list', methods=['GET'])
@require_api_key
def list_devices():
    devices = models.Device.query.all()
    return jsonify([{
        'id': d.id,
        'device_id': d.device_id,
        'device_type': d.device_type,
        'name': d.name,
        'is_online': d.is_online,
        'type_name': d.type_name,
    } for d in devices])

@api.route('/floors/<int:floor_number>/rooms/<string:room_number>/devices/list', methods=['GET'])
@require_api_key
def list_devices_in_room(floor_number, room_number):
   """
   Get all devices in a specific room
   Path: /floors/{floor_number}/rooms/{room_number}/devices/list
   """
   try:
       floor = models.Floor.query.filter_by(floor_number=floor_number).first()
       if not floor:
           return jsonify({'error': f'Floor {floor_number} does not exist'}), 404
       
       room = models.Room.query.filter_by(
           room_number=room_number, 
           floor_id=floor.id
       ).first()
       if not room:
           return jsonify({'error': f'Room {room_number} does not exist on floor {floor_number}'}), 404
       
       # Get all devices in the room
       devices = []
       for device in room.devices:
           device_data = {
               'id': device.id,
               'device_id': device.device_id,
               'name': device.name,
               'device_type': device.device_type,
               'description': device.description,
               'is_online': device.is_online,
               'last_seen': device.last_seen.isoformat() if device.last_seen else None,
               'created_at': device.created_at.isoformat()
           }
           devices.append(device_data)
       
       return jsonify({
           'floor_number': floor_number,
           'room_number': room_number,
           'devices': devices,
           'total_devices': len(devices)
       }), 200
       
   except Exception as e:
       return jsonify({'error': str(e)}), 500
   
@api.route('/floors/<int:floor_number>/rooms/<string:room_number>/devices/<string:device_id>', methods=['GET'])
@require_api_key
def get_device_details(floor_number, room_number, device_id):
    """
    Get detailed information about a specific device
    Path: /floors/{floor_number}/rooms/{room_number}/devices/{device_id}
    """
    try:
        floor = models.Floor.query.filter_by(floor_number=floor_number).first()
        if not floor:
            return jsonify({'error': f'Floor {floor_number} does not exist'}), 404
        
        room = models.Room.query.filter_by(
            room_number=room_number, 
            floor_id=floor.id
        ).first()
        if not room:
            return jsonify({'error': f'Room {room_number} does not exist on floor {floor_number}'}), 404
        
        device = models.Device.query.filter_by(
            device_id=device_id,
            room_id=room.id
        ).first()
        if not device:
            return jsonify({'error': f'Device {device_id} does not exist in room {room_number} on floor {floor_number}'}), 404
        
        # Return detailed device information
        device_details = {
            'id': device.id,
            'device_id': device.device_id,
            'name': device.name,
            'device_type': device.device_type,
            'description': device.description,
            'is_online': device.is_online,
            'last_seen': device.last_seen.isoformat() if device.last_seen else None,
            'created_at': device.created_at.isoformat(),
            'location': {
                'floor_number': floor.floor_number,
                'floor_name': floor.floor_name,
                'room_number': room.room_number,
                'room_type': room.room_type,
                'room_id': room.id
            }
        }
        
        return jsonify({
            'device': device_details
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@api.route('/devices/<string:device_id>/set', methods=['POST'])
# Todo: Add authentication decorator
def set_actuator_value(device_id):
    """
    Set actuator value for a specific device
    
    Expected JSON format:
    {
        "new_value": "value_to_set"
    }
    
    Path: /devices/{device_id}/set
    """
    try:
        # Get request data
        data = request.get_json()
        if not data or 'new_value' not in data:
            return jsonify({'error': 'new_value is required'}), 400
        
        new_value = data['new_value']
        
        # Use device.id (UUID) for MQTT communication
        success = request_actuator_update(device_id, new_value)
        
        if success:
            return jsonify({
                'message': f'Actuator update request sent successfully',
                'device_id': device_id,
                'device_uuid': device_id,
                'new_value': new_value
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send actuator update request. Please refer to server logs for more details.'
            }), 500
            
    except Exception as e:
        return jsonify({'error': 'An error occurred while processing your request'}), 500


@api.route('/devices/<string:device_id>/get', methods=['POST'])
# Todo: Add authentication decorator
def request_current_value(device_id):
    """
    Request current value from a sensor or actuator. It does not return the value directly.
    
    Path: /devices/{device_id}/get
    """
    try:
        # Use device.id (UUID) for MQTT communication
        success = request_current_sensor_value(device_id)
        
        if success:
            return jsonify({
                'message': f'Current value request sent successfully',
                'device_id': device_id,
                'device_uuid': device_id,
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send current value request.  Please refer to server logs for more details.'
            }), 500
            
    except Exception as e:
        return jsonify({'error': 'An error occurred while processing your request'}), 500
