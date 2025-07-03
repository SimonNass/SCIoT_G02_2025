import logging
import backend.models.models as models
from backend.extensions import db
from backend.mqtt.utils.cacheUtils import device_cache
from backend.mqtt.utils.parsersUtils import parse_device_payload, validate_device_data
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from backend.mqtt.utils.typeNameConfigUtils import get_simple_default_middle_values

def get_or_create_device(app_instance, floor_number, room_number, sensor_type, device_id, payload=None):
    """
    Get device from cache or create new device in database.
    Also processes payload data and saves sensor readings.
    Returns: device info dict or None if error
    """
    
    try:
        # Check if device already exists in cache
        if device_id in device_cache:
            logging.debug(f"Device {device_id} found in cache")
            # Process payload and update device status in a single transaction
            success = _process_device_payload_and_status(app_instance, device_id, sensor_type, payload, update_only=True)
            if success:
                return device_cache[device_id]
            else:
                logging.warning(f"Failed to process payload for cached device {device_id}")
                return device_cache[device_id]  # Return device info even if payload processing failed
        
        # Device not in cache, check database and create if needed
        with app_instance.app_context():
            floor = models.Floor.query.filter_by(floor_number=floor_number).first()
            if not floor:
                logging.error(f"Floor {floor_number} does not exist")
                return None
            
            # Check if room exists
            room = models.Room.query.filter_by(room_number=room_number, floor_id=floor.id).first()
            if not room:
                logging.error(f"Room {room_number} on floor {floor_number} does not exist")
                return None
            
            # Try to get existing device first
            existing_device = models.Device.query.filter_by(device_id=device_id).first()
            
            if existing_device:
                # Device exists in DB but not in cache
                return _handle_existing_device(app_instance, existing_device, sensor_type, payload)
            else:
                # Create new device
                return _create_new_device(app_instance, device_id, sensor_type, room, floor_number, room_number, payload)
    
    except Exception as e:
        logging.error(f"Error creating/getting device {device_id}: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return None

def _handle_existing_device(app_instance, existing_device, sensor_type, payload):
    """Handle existing device found in database but not in cache"""
    try:
        device_info = {
            'id': existing_device.id,
            'room_id': existing_device.room_id,
            'device_type': existing_device.device_type,
            'type_name': existing_device.type_name,
            'name': existing_device.name,
            'is_online': True
        }
        
        # Add to cache
        device_cache[existing_device.device_id] = device_info
        
        # Process payload and update device status in a single transaction
        success = _process_device_payload_and_status(app_instance, existing_device.device_id, sensor_type, payload, 
                                                   device_obj=existing_device, update_only=True)
        
        if success:
            logging.info(f"Device {existing_device.device_id} added to cache from database and payload processed")
        else:
            logging.warning(f"Device {existing_device.device_id} added to cache but payload processing failed")
        
        return device_info
        
    except Exception as e:
        logging.error(f"Error handling existing device {existing_device.device_id}: {str(e)}")
        db.session.rollback()
        return None

def _create_new_device(app_instance, device_id, sensor_type, room, floor_number, room_number, payload):
    """Create a new device with proper race condition handling"""
    try:
        device_name = f"{sensor_type.title()} - {room_number}"
        new_device = models.Device(
            device_id=device_id,
            name=device_name,
            device_type=sensor_type,
            description=f"{sensor_type} sensor in room {room_number} on floor {floor_number}",
            is_online=True,
            room_id=room.id,
            last_seen=datetime.utcnow()
        )
        
        # Parse and validate payload data if provided
        parsed_payload = None
        if payload:
            parsed_payload = parse_device_payload(payload, sensor_type)
            if parsed_payload and validate_device_data(parsed_payload, sensor_type):
                # Update device with parsed payload data
                _update_device_from_payload(new_device, parsed_payload)
            else:
                logging.warning(f"Invalid payload for new device {device_id}, creating device without payload data")
        
        # Add device to session
        db.session.add(new_device)
        
        # Try to commit the new device
        try:
            db.session.flush()  # Get the device ID without committing
            device_info = {
                'id': new_device.id,
                'room_id': new_device.room_id,
                'device_type': new_device.device_type,
                'type_name': new_device.type_name,
                'name': new_device.name,
                'is_online': True
            }
            
            # Create sensor data record if we have valid payload and it's a sensor
            sensor_data_created = False
            if parsed_payload and sensor_type == 'sensor' and parsed_payload['last_value'] is not None:
                try:
                    latest_value = float(parsed_payload['last_value'])
                    create_device_type_config(app_instance, new_device.device_type, new_device.type_name, 
                                                      new_device.max_value, new_device.min_value, new_device.unit)
                    simplified_value = get_simplified_value(latest_value, new_device.device_type, new_device.type_name)
                    new_device.last_value = latest_value  # Update latest value in device object
                    new_device.last_value_simplified = simplified_value  # Update simplified value in device object
                    sensor_data = models.SensorData(
                        device_id=new_device.id,
                        value=latest_value,
                        simplified_value=simplified_value,
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(sensor_data)
                    sensor_data_created = True
                    logging.debug(f"Sensor data record created for new device {device_id}")
                except Exception as sd_error:
                    logging.warning(f"Failed to create sensor data for device {device_id}: {sd_error}")
            
            # Commit everything at once
            db.session.commit()
            
            # Add to cache only after successful commit
            device_cache[device_id] = device_info
            
            log_msg = f"New device created and cached: {device_id} ({sensor_type}) in room {room_number}, floor {floor_number}"
            if sensor_data_created:
                log_msg += " with sensor data"
            logging.info(log_msg)
            
            return device_info
            
        except IntegrityError as ie:
            # Handle race condition - device was created by another process
            db.session.rollback()
            logging.info(f"Device {device_id} was created by another process, fetching from database")
            
            # Fetch the device that was created by another process
            existing_device = models.Device.query.filter_by(device_id=device_id).first()
            if existing_device:
                return _handle_existing_device(app_instance, existing_device, sensor_type, payload)
            else:
                logging.error(f"Failed to retrieve device {device_id} after integrity error")
                return None
                
    except Exception as e:
        logging.error(f"Error creating new device {device_id}: {str(e)}")
        db.session.rollback()
        return None

def _process_device_payload_and_status(app_instance, device_id, sensor_type, payload, device_obj=None, update_only=False):
    """
    Process device payload and update device status in a single transaction.
    Returns True if successful, False otherwise.
    """
    try:
        with app_instance.app_context():
            # Get device object if not provided
            if device_obj is None:
                device_obj = models.Device.query.filter_by(device_id=device_id).first()
                if not device_obj:
                    logging.error(f"Device {device_id} not found in database")
                    return False
            
            # Update device status and last_seen
            device_obj.is_online = True
            device_obj.last_seen = datetime.utcnow()
            
            # Process payload if provided
            sensor_data_created = False
            if payload:
                parsed_payload = parse_device_payload(payload, sensor_type)
                if parsed_payload and validate_device_data(parsed_payload, sensor_type):
                    # Update device with payload data
                    _update_device_from_payload(device_obj, parsed_payload)
                    
                    # Create sensor data record if it's a sensor with a value
                    if sensor_type == 'sensor' and parsed_payload['last_value'] is not None:
                        try:
                            latest_value = float(parsed_payload['last_value'])
                            create_device_type_config(app_instance, device_obj.device_type, device_obj.type_name, 
                                                      device_obj.max_value, device_obj.min_value, device_obj.unit)
                            simplified_value = get_simplified_value(latest_value, device_obj.device_type, device_obj.type_name)
                            device_obj.last_value = latest_value  # Update latest value in device object
                            device_obj.last_value_simplified = simplified_value  # Update simplified value in device object
                            sensor_data = models.SensorData(
                                device_id=device_obj.id,
                                value=latest_value,
                                simplified_value=simplified_value,
                                timestamp=datetime.utcnow()
                            )
                            db.session.add(sensor_data)
                            sensor_data_created = True
                            logging.debug(f"Sensor data record created for device {device_id}")
                        except Exception as sd_error:
                            logging.warning(f"Failed to create sensor data for device {device_id}: {sd_error}")
                else:
                    logging.warning(f"Invalid payload for device {device_id}")
            
            # Commit all changes at once
            db.session.commit()
            
            # Update cache
            if device_id in device_cache:
                device_cache[device_id]['is_online'] = True
                # Update cache with new device data if we have parsed payload
                if payload:
                    parsed_payload = parse_device_payload(payload, sensor_type)
                    if parsed_payload:
                        device_cache[device_id]['type_name'] = parsed_payload.get('type_name', device_cache[device_id].get('type_name'))
            
            log_msg = f"Device {device_id} status updated"
            if sensor_data_created:
                log_msg += " with new sensor data"
            logging.debug(log_msg)
            
            return True
            
    except Exception as e:
        logging.error(f"Error processing payload and status for device {device_id}: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return False

def _update_device_from_payload(device_obj, parsed_payload):
    """Update device object with parsed payload data"""
    try:
        # Update device fields with payload data
        if parsed_payload.get('type_name'):
            device_obj.type_name = parsed_payload['type_name']
        
        if parsed_payload.get('unit'):
            device_obj.unit = parsed_payload['unit']
        
        if parsed_payload.get('min_value') is not None:
            device_obj.min_value = parsed_payload['min_value']
            
        if parsed_payload.get('max_value') is not None:
            device_obj.max_value = parsed_payload['max_value']
            
        if parsed_payload.get('datatype'):
            device_obj.datatype = parsed_payload['datatype']
            
        # Update sensor-specific fields
        if parsed_payload.get('read_interval') is not None:
            device_obj.read_interval = parsed_payload['read_interval']
            
        if parsed_payload.get('notify_interval'):
            device_obj.notify_interval = parsed_payload['notify_interval']
            
        if parsed_payload.get('notify_change_precision') is not None:
            device_obj.notify_change_precision = parsed_payload['notify_change_precision']
            
        # Update actuator-specific fields
        if parsed_payload.get('initial_value'):
            device_obj.initial_value = parsed_payload['initial_value']
            
        if parsed_payload.get('off_value'):
            device_obj.off_value = parsed_payload['off_value']
            
        logging.debug(f"Device {device_obj.device_id} updated with payload data")
        
    except Exception as e:
        logging.error(f"Error updating device {device_obj.device_id} from payload: {str(e)}")
        raise

def update_device_status(app_instance, device_id, is_online=True):
    """Update device online status in database"""
    try:
        with app_instance.app_context():
            device = models.Device.query.filter_by(device_id=device_id).first()
            if device:
                device.is_online = is_online
                if is_online:
                    device.last_seen = datetime.utcnow()
                db.session.commit()
                
                # Update cache
                if device_id in device_cache:
                    device_cache[device_id]['is_online'] = is_online
                    
                logging.debug(f"Device {device_id} status updated to {'online' if is_online else 'offline'}")
                return True
            else:
                logging.warning(f"Device {device_id} not found for status update")
                return False
                    
    except Exception as e:
        logging.error(f"Error updating device status for {device_id}: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return False
    

def create_device_type_config(app_instance, device_type, type_name, max_value, min_value, unit):
    """
    Save the device type configuration to database.
    """
    try:
        with app_instance.app_context():
            # Check input validity
            if max_value is None or min_value is None:
                logging.error("Max value and min value must be provided")
                raise
            
            if device_type is None or type_name is None or unit is None:
                logging.error("Device type, type name and unit must be provided")
                raise
            
            device_type_config = models.TypeNameConfig.query.filter_by(device_type=device_type, type_name=type_name).first()
            if device_type_config:
               logging.info(f"Device type config for {device_type} already exists")
               return None  # Device type config already exists
            
            if device_type == "sensor":
                lower_mid_limit, upper_mid_limit = get_simple_default_middle_values(max_value, min_value)
            else: 
                lower_mid_limit, upper_mid_limit = None, None
                
            if lower_mid_limit is None or upper_mid_limit is None:
                raise ValueError("Invalid values, cannot create config")

            # Create new device type config
            new_device_type_config = models.TypeNameConfig(
               # Set device type as enum value
               device_type=device_type,
               type_name=type_name,
               max_value=max_value,
               min_value=min_value,
               lower_mid_limit=lower_mid_limit,
               upper_mid_limit=upper_mid_limit,
               unit=unit
            )
            
            # Save to database
            db.session.add(new_device_type_config)
            db.session.commit()
            logging.info(f"Device type config for {device_type} created successfully")
            
            return new_device_type_config
        
    except IntegrityError as e:
        logging.error(f"Integrity error while creating device type config for {device_type}: {str(e)}")
        db.session.rollback()
        raise

def get_simplified_value(value: float, device_type: str, type_name: str) -> str:
    """
    Get simplified value from device type configuration.
    Args:
        value (float): The value to simplify.
        device_type (str): The type of the device.
    Returns:
        str: The simplified value as a string.
    """      
    try:
        value = float(value) 
        device_type_config = models.TypeNameConfig.query.filter_by(device_type=device_type, type_name=type_name).first()
        if not device_type_config:
            logging.error(f"Device type config for {device_type} and {type_name} not found")
            raise
        
        # Check if value is within the configured range
        if value < device_type_config.min_value or value > device_type_config.max_value:
            logging.error(f"Value {value} out of range for device type {device_type}")
            raise
        
        # Simplify value based on mid limits
        if value < device_type_config.lower_mid_limit:
            return -1 # Maps to LOW
        elif value > device_type_config.upper_mid_limit:
            return 1 # Maps to HIGH
        else:
            return 0 # Maps to MID 
    except Exception as e:
        logging.error(f"Error simplifying value {value} for device type {device_type}: {str(e)}")
        raise