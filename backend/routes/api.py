from flask import Blueprint, jsonify, request
from backend.aiplaning.utils.dbUtils import get_sensor_types
from backend.extensions import db
from backend.models import models
from sqlalchemy.exc import IntegrityError
from backend.routes.auth.simple_auth import require_api_key
from backend.mqtt.utils.mqttPublish import request_actuator_update, request_current_sensor_value, request_sensor_update
from backend.mqtt.utils.mappingParserUtils import get_actuator_sensor_matrices, get_mapping_impact_factors
from datetime import datetime, timedelta
from sqlalchemy import and_
import logging

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

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': f'Floor number already exists: {str(e)}'}), 409
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
                    'device_count': len(room.devices),
                    'rfid_access_id': room.rfid_access_id,
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
                'rfid_access_id': room.rfid_access_id,
                'devices': []
            }

            # Include device information
            for device in room.devices:
                device_data = {
                    'id': device.id,
                    'device_id': device.device_id,
                    'name': device.name,
                    'device_type': device.device_type,
                    'type_name': device.type_name,
                    'description': device.description,
                    'min_value': device.min_value,
                    'max_value': device.max_value,
                    'is_online': device.is_online,
                    'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                    'read_interval': device.read_interval,
                    'created_at': device.created_at.isoformat(),
                    'last_value': device.last_value,
                    'last_value_simplified': device.last_value_simplified,
                    'initial_value': device.initial_value,
                    'off_value': device.off_value,
                    'is_off': device.is_off,
                    'ai_planing_type': device.ai_planing_type,
                    'impact_step_size': device.impact_step_size
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

@api.route('/floors/<int:floor_number>/rooms/<string:room_number>/occupancy/set', methods=['POST'])
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

@api.route('/rooms/occupancy/list/set', methods=['POST'])
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
               'type_name': device.type_name,
               'description': device.description,
               'min_value': device.min_value,
               'max_value': device.max_value,
               'is_online': device.is_online,
               'last_seen': device.last_seen.isoformat() if device.last_seen else None,
               'read_interval': device.read_interval,
               'created_at': device.created_at.isoformat(),
               'last_value': device.last_value,
               'last_value_simplified': device.last_value_simplified,
               'initial_value': device.initial_value,
               'off_value': device.off_value,
               'is_off': device.is_off,
               'unit': device.unit,
               'ai_planing_type': device.ai_planing_type,
               'impact_step_size': device.impact_step_size
           }
           devices.append(device_data)

       return jsonify({
           'floor_number': floor_number,
           'room_number': room_number,
           'devices': devices,
           'total_devices': len(devices),
           'is_occupied': room.is_occupied
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

@api.route('/devices/sensor/<string:device_id>/set', methods=['POST'])
# Todo: Add authentication decorator
def set_sensor_value(device_id):
    """
    Set sensor value for a specific device

    Expected JSON format:
    {
        "new_value": "value_to_set"
    }

    Path: /devices/sensor/{device_id}/set
    """
    try:
        # Get request data
        data = request.get_json()
        if not data or 'new_value' not in data:
            return jsonify({'error': 'new_value is required'}), 400

        new_value = data['new_value']

        # Use device.id (UUID) for MQTT communication
        success = request_sensor_update(device_id, new_value)

        if success:
            return jsonify({
                'message': f'Sensor update request sent successfully',
                'device_id': device_id,
                'device_uuid': device_id,
                'new_value': new_value
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send sensor update request. Please refer to server logs for more details.'
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

@api.route('/type_name_configs/list', methods=['GET'])
@require_api_key
def list_type_name_configs():
    """
    List all type name configurations
    """
    try:
        configs = models.TypeNameConfig.query.all()

        result = []
        for config in configs:
            config_data = {
                'id': config.id,
                'device_type': config.device_type,
                'type_name': config.type_name,
                'min_value': config.min_value,
                'max_value': config.max_value,
                'lower_mid_limit': config.lower_mid_limit,
                'upper_mid_limit': config.upper_mid_limit,
                'unit': config.unit,
            }
            result.append(config_data)

        return jsonify({
            'configs': result,
            'total_configs': len(result)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/type_name_configs/set', methods=['POST'])
@require_api_key
def set_type_name_configs():
    """
    Update existing type name config lower_mid and upper_mid values.

    Expected JSON format:
    {
        "device_type": "sensor",
        "type_name": "temperature",
        "lower_mid_limit": 20.0,
        "upper_mid_limit": 80.0,
    }

    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400

        device_type = data.get('device_type')
        type_name = data.get('type_name')
        lower_mid_limit = data.get('lower_mid_limit')
        upper_mid_limit = data.get('upper_mid_limit')

        if not device_type or not type_name or lower_mid_limit is None or upper_mid_limit is None:
            return jsonify({'error': 'All fields are required'}), 400

        # Update the config in the database
        config = models.TypeNameConfig.query.filter_by(device_type=device_type, type_name=type_name).first()
        if not config:
            return jsonify({'error': 'Config not found'}), 404

        config.lower_mid_limit = lower_mid_limit
        config.upper_mid_limit = upper_mid_limit
        db.session.commit()

        return jsonify({'message': 'Config updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/mappings/matrices')
def get_mapping_matrices():
    """Get actuator-sensor mapping matrices"""
    try:
        increases_matrix, decreases_matrix = get_actuator_sensor_matrices()
        impact_factors = get_mapping_impact_factors()

        # Return as a proper JSON response
        response_data = {
            'increases_matrix': increases_matrix,
            'decreases_matrix': decreases_matrix,
            'impact_factors': impact_factors
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error - Failed to retrieve mapping matrices:': str(e)}), 500

@api.route('/query/test', methods=['GET'])
def list_floor_uids():
    try:
        floor_ids = get_sensor_types()
        import logging
        logging.info(f"Info: {floor_ids}")
        return jsonify(floor_ids), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Device offline/deletion endpoints
@api.route('/devices/<string:device_id>/offline/set', methods=['POST'])
@require_api_key
def set_device_offline(device_id):
    """
    Set a specific device to offline status
    Path: /devices/{device_id}/offline
    """
    try:
        device = models.Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'error': f'Device {device_id} does not exist'}), 404

        device.is_online = False
        db.session.commit()

        return jsonify({
            'message': f'Device {device_id} set to offline successfully',
            'device_id': device_id,
            'is_online': False
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/devices/<string:device_id>/delete', methods=['DELETE'])
@require_api_key
def delete_device(device_id):
    """
    Delete a specific device
    Path: /devices/{device_id}/delete
    """
    try:
        device = models.Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'error': f'Device {device_id} does not exist'}), 404

        db.session.delete(device)
        db.session.commit()

        return jsonify({
            'message': f'Device {device_id} deleted successfully',
            'device_id': device_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Bulk offline/deletion based on last_seen
@api.route('/devices/bulk/offline/set', methods=['POST'])
@require_api_key
def bulk_set_devices_offline():
    """
    Set devices to offline that haven't been seen for more than n minutes
    Expected JSON format:
    {
        "minutes": 30
    }
    """
    try:
        data = request.get_json()
        if not data or 'minutes' not in data:
            return jsonify({'error': 'minutes parameter is required'}), 400

        minutes = data['minutes']
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)

        devices = models.Device.query.filter(
            and_(
                models.Device.last_seen < cutoff_time,
                models.Device.is_online == True
            )
        ).all()

        updated_count = 0
        for device in devices:
            device.is_online = False
            updated_count += 1

        db.session.commit()

        return jsonify({
            'message': f'{updated_count} devices set to offline',
            'minutes_threshold': minutes,
            'devices_affected': updated_count
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/devices/bulk/delete', methods=['DELETE'])
@require_api_key
def bulk_delete_devices():
    """
    Delete devices that haven't been seen for more than n minutes
    Expected JSON format:
    {
        "minutes": 60
    }
    """
    try:
        data = request.get_json()
        if not data or 'minutes' not in data:
            return jsonify({'error': 'minutes parameter is required'}), 400

        minutes = data['minutes']
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)

        devices = models.Device.query.filter(
            models.Device.last_seen < cutoff_time
        ).all()

        deleted_count = len(devices)
        device_ids = [device.device_id for device in devices]

        for device in devices:
            db.session.delete(device)

        db.session.commit()

        return jsonify({
            'message': f'{deleted_count} devices deleted',
            'minutes_threshold': minutes,
            'devices_deleted': deleted_count,
            'deleted_device_ids': device_ids
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Sensor data retrieval endpoints
@api.route('/devices/<string:device_id>/sensor_data', methods=['POST'])
@require_api_key
def get_device_sensor_data(device_id):
    """
    Get sensor data for a device with interval sampling
    Expected JSON format:
    {
        "interval": 6
    }
    If interval is 6 and there are 60 datapoints, returns every 6th datapoint (10 total)
    """
    try:
        device = models.Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'error': f'Device {device_id} does not exist'}), 404

        if device.device_type != 'sensor':
            return jsonify({'error': f'Device {device_id} is not a sensor'}), 400

        data = request.get_json()
        interval = data.get('interval', 1) if data else 1

        if interval < 1:
            return jsonify({'error': 'interval must be at least 1'}), 400

        # Get all sensor data for this device
        all_sensor_data = models.SensorData.query.filter_by(
            device_id=device.id
        ).order_by(models.SensorData.timestamp.asc()).all()

        # Apply interval sampling - take every nth datapoint
        sampled_data = all_sensor_data[::interval]

        result = []
        for data_point in sampled_data:
            result.append({
                'id': data_point.id,
                'value': data_point.value,
                'simplified_value': data_point.simplified_value,
                'timestamp': data_point.timestamp.isoformat()
            })

        return jsonify({
            'device_id': device_id,
            'device_name': device.name,
            'type_name': device.type_name,
            'unit': device.unit,
            'total_datapoints_available': len(all_sensor_data),
            'sampling_interval': interval,
            'sampled_datapoints': len(result),
            'sensor_data': result
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/devices/<string:device_id>/sensor_data/recent', methods=['POST'])
@require_api_key
def get_recent_sensor_data(device_id):
    """
    Get sensor data from the last n minutes with interval sampling
    Expected JSON format:
    {
        "minutes": 30,
        "interval": 6
    }
    """
    try:
        device = models.Device.query.filter_by(device_id=device_id).first()
        if not device:
            return jsonify({'error': f'Device {device_id} does not exist'}), 404

        if device.device_type != 'sensor':
            return jsonify({'error': f'Device {device_id} is not a sensor'}), 400

        data = request.get_json()
        minutes = data.get('minutes', 60) if data else 60
        interval = data.get('interval', 1) if data else 1

        if interval < 1:
            return jsonify({'error': 'interval must be at least 1'}), 400

        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        logging.info(cutoff_time)

        sensor_data = models.SensorData.query.filter(
            and_(
                models.SensorData.device_id == device.id,
                models.SensorData.timestamp >= cutoff_time
            )
        ).order_by(models.SensorData.timestamp.asc()).all()

        # Apply interval sampling
        sampled_data = sensor_data[::interval]  # Take every nth value

        result = []
        for data in sampled_data:
            result.append({
                'id': data.id,
                'value': data.value,
                'simplified_value': data.simplified_value,
                'timestamp': data.timestamp.isoformat()
            })

        return jsonify({
            'device_id': device_id,
            'device_name': device.name,
            'type_name': device.type_name,
            'unit': device.unit,
            'minutes_range': minutes,
            'sampling_interval': interval,
            'total_datapoints_in_range': len(sensor_data),
            'sampled_datapoints': len(result),
            'sensor_data': result
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/cleardb', methods=['DELETE'])
@require_api_key
def clear_database():

    try:
        db.session.remove()        # close any pending sessions
        db.drop_all()
        db.create_all()

        return jsonify({'message': 'Database wiped successfully'}), 200
    except Exception as exc:
        return jsonify({'error': f'Failed to wipe database: {exc}'}), 500
