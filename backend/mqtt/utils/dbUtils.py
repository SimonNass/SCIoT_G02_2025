import logging
import backend.models.models as models
from backend.extensions import db
from backend.mqtt.utils.cacheUtils import device_cache
from sqlalchemy.exc import IntegrityError

def get_or_create_device(app_instance, floor_number, room_number, sensor_type, sensor_id):
    """
    Get device from cache or create new device in database
    Returns: device info dict or None if error
    """
    
    try:
        # Check if device already exists in cache
        if sensor_id in device_cache:
            logging.debug(f"Device {sensor_id} found in cache")
            # Update last seen status
            update_device_status(app_instance, device_id=sensor_id, is_online=True)
            return device_cache[sensor_id]
        
        # Device not in cache, check database and create if needed
        with app_instance.app_context():
            floor = models.Floor.query.filter_by(floor_number=floor_number).first()
            if not floor:
                logging.error(f"Floor {floor_number} does not exist for device {sensor_id}")
                return None
            
            # Check if room exists
            room = models.Room.query.filter_by(room_number=room_number, floor_id=floor.id).first()
            if not room:
                logging.error(f"Room {room_number} on floor {floor_number} does not exist for device {sensor_id}")
                return None
            
            # Try to get existing device first
            existing_device = models.Device.query.filter_by(device_id=sensor_id).first()
            
            if existing_device:
                # Device exists in DB but not in cache, add to cache
                device_info = {
                    'id': existing_device.id,
                    'room_id': existing_device.room_id,
                    'device_type': existing_device.device_type,
                    'name': existing_device.name,
                    'is_online': True
                }
                device_cache[sensor_id] = device_info
                
                # Update device status
                existing_device.is_online = True
                db.session.commit()
                
                logging.info(f"Device {sensor_id}-{device_name} added to cache from database")
                return device_info
            
            # Try to create new device with proper error handling for race conditions
            try:
                device_name = f"{sensor_type.title()} - {room_number}"
                new_device = models.Device(
                    device_id=sensor_id,
                    name=device_name,
                    device_type=sensor_type,
                    description=f"{sensor_type} sensor in room {room_number} on floor {floor_number}",
                    is_online=True,
                    room_id=room.id
                )
                
                db.session.add(new_device)
                db.session.commit()
                
                # Add to cache
                device_info = {
                    'id': new_device.id,
                    'room_id': new_device.room_id,
                    'device_type': new_device.device_type,
                    'name': new_device.name,
                    'is_online': True
                }
                device_cache[sensor_id] = device_info
                
                logging.info(f"New device created and cached: {sensor_id} ({sensor_type}) in room {room_number}, floor {floor_number}")
                return device_info
                
            except IntegrityError as ie:
                # Handle race condition - device was created by another process
                db.session.rollback()
                logging.info(f"Device {sensor_id} was created by another process, fetching from database")
                
                # Fetch the device that was created by another process
                existing_device = models.Device.query.filter_by(device_id=sensor_id).first()
                if existing_device:
                    # Add to cache
                    device_info = {
                        'id': existing_device.id,
                        'room_id': existing_device.room_id,
                        'device_type': existing_device.device_type,
                        'name': existing_device.name,
                        'is_online': True
                    }
                    device_cache[sensor_id] = device_info
                    
                    # Update device status
                    existing_device.is_online = True
                    db.session.commit()
                    
                    logging.info(f"Device {sensor_id} retrieved after race condition and added to cache")
                    return device_info
                else:
                    logging.error(f"Failed to retrieve device {sensor_id} after integrity error")
                    return None
    
    except Exception as e:
        logging.error(f"Error creating/getting device {sensor_id}: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return None
    
def update_device_status(app_instance, device_id, is_online=True):
    """Update device online status in database"""
    try:
        with app_instance.app_context():
            device = models.Device.query.filter_by(device_id=device_id).first()
            if device:
                device.is_online = is_online
                from datetime import datetime
                if is_online:
                    device.last_seen = datetime.utcnow()
                db.session.commit()
                
                # Update cache
                if device_id in device_cache:
                    device_cache[device_id]['is_online'] = is_online
                    
    except Exception as e:
        logging.error(f"Error updating device status for {device_id}: {str(e)}")