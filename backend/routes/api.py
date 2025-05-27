from flask import Blueprint, jsonify, request
from backend.extensions import db
from backend.models import models
from sqlalchemy.exc import IntegrityError

api = Blueprint('api', __name__)

@api.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

# Create floor with rooms (optional)
@api.route('/floors/create', methods=['POST'])
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
@api.route('/floors/list')
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
@api.route('/floors/<int:floor_number>/rooms/list')
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
                    'battery_level': device.battery_level
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

@api.route('/devices/list')
def list_devices():
    devices = models.Device.query.all()
    return jsonify([{
        'id': d.id,
        'device_id': d.device_id,
        'name': d.name,
        'is_online': d.is_online,
    } for d in devices])