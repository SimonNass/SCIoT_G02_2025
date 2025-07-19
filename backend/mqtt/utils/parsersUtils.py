import logging
import json
from backend.extensions import db
from backend.models.models import Device

def parse_mqtt_topic(topic, app_instance):
    """
    Parse MQTT topic: SCIoT_G02_2025/<floor>/<room>/<device-type>/<device-id>/all
    Returns: (floor_number, room_number, device_type, device_id) or None if invalid
    """
    try:
        if not topic or not isinstance(topic, str):
            logging.warning("Invalid topic: empty or not string")
            return None
            
        parts = topic.split('/')
        
        # Get the expected topic prefix from config
        expected_prefix = app_instance.config['MQTT_TOPIC_SUBSCRIBE'].split('/')[0]
        
        # Process Mapping Topic
        if len(parts) == 5 and parts[0] == expected_prefix and parts[4] == "all" and parts[3] == "mapping":
            # SCIoT_G02_2025/<floor_number>/<room_number>/mapping/all
            _, floor_str, room_number, mapping, _ = parts
            floor_number = floor_str_to_int_converter(floor_str)
            return floor_number, room_number, mapping
        if len(parts) == 6 and parts[0] == expected_prefix and parts[5] == "delete":
            try:
                # Delete all devices from the database
                deleted_count = db.session.query(Device).delete()
                db.session.commit()
                logging.info(f"Successfully deleted {deleted_count} devices from database")

                return None
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error deleting devices from database: {str(e)}")
                return None
        if len(parts) == 6 and parts[0] == expected_prefix and parts[5] == "UPDATE":
            logging.info(f"Detected message publish for request to gateway, skipping message")
            return None
        if len(parts) != 6 or parts[0] != expected_prefix and parts[5] != "all":
            logging.warning(f"Invalid topic format: {topic}")
            return None
        
        _, floor_str, room_number, device_type, device_id, _ = parts
        
        # Convert floor to integer
        floor_number = floor_str_to_int_converter(floor_str)
        if floor_number is None:
            raise Exception("Floor number out of range")
        
        return floor_number, room_number, device_type, device_id
    
    except Exception as e:
        logging.error(f"Error parsing topic {topic}: {str(e)}")
        return None
    
def floor_str_to_int_converter(floor_str: str):
        try:
            floor_number = int(floor_str)
            if floor_number < 0 or floor_number > 100:
                raise Exception("Floor number out of range")
            return floor_number
        except ValueError:
            logging.warning(f"Invalid floor number in topic: {floor_str}")
            raise

def safe_float_conversion(value):
    """
    Safely convert a value to float, handling empty strings and None values.
    Returns None if conversion fails or value is empty.
    """
    if value is None:
        return None
    
    # Handle empty strings
    if isinstance(value, str) and value.strip() == '':
        return None
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def safe_int_conversion(value):
    """
    Safely convert a value to int, handling empty strings and None values.
    Returns None if conversion fails or value is empty.
    """
    if value is None:
        return None
    
    # Handle empty strings
    if isinstance(value, str) and value.strip() == '':
        return None
    
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def safe_str_conversion(value):
    """
    Safely convert a value to string, handling None values and empty strings.
    Returns None for None input or empty strings.
    """
    if value is None:
        return None
    
    # Convert to string and check if it's empty or just whitespace
    str_value = str(value).strip()
    if str_value == '' or str_value.lower() == 'none':
        return None
    
    return str_value

def safe_float_conversion_for_sensor_data(value):
    """
    Safely convert a value to float for sensor data storage.
    Returns None if conversion fails.
    """
    if value is None:
        return None
    
    # Handle empty strings
    if isinstance(value, str) and value.strip() == '':
        return None
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def parse_device_payload(payload, device_type):
    """
    Parse device payload JSON and extract relevant fields for sensors or actuators
    
    Args:
        payload (str): JSON string payload from MQTT message
        device_type (str): 'sensor' or 'actuator'
    
    Returns:
        dict: Parsed device data or None if parsing fails
    
    Sensor payload structure:
    {
        "id": str,
        "name": str,
        "type_name": str,
        "connector": str,
        "connector_type": str,
        "min": float,
        "max": float,
        "datatype": str,
        "unit": str,
        "read_interval": int,
        "notify_interval": str,
        "notify_change_precision": float,
        "last_value": any
    }
    
    Actuator payload structure:
    {
        "id": str,
        "name": str,
        "type_name": str,
        "connector": str,
        "connector_type": str,
        "min": float,
        "max": float,
        "datatype": str,
        "unit": str,
        "initial_value": any,
        "off_value": any,
        "is_off": bool,
        "last_value": any
    }
    """
    try:
        if not payload:
            return None
            
        # Parse JSON payload
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON payload: {str(e)}")
            return None
        
        if not isinstance(data, dict):
            logging.error("Payload is not a JSON object")
            return None
        
        # Extract common fields
        parsed_data = {
            'name': data.get('name'),
            'type_name': data.get('type_name'),
            'connector': data.get('connector'),
            'connector_type': str(data.get('connector_type')) if data.get('connector_type') is not None else None,
            'min_value': safe_float_conversion(data.get('min')),
            'max_value': safe_float_conversion(data.get('max')),
            'datatype': data.get('datatype'),
            'unit': data.get('unit'),
            'ai_planing_type': safe_str_conversion(data.get('ai_planing_type')),
            'last_value': safe_str_conversion(data.get('last_value')),
        }
        
        # Extract device-specific fields
        if device_type == 'sensor':
            parsed_data.update({
                'read_interval': int(data.get('read_interval')) if data.get('read_interval') is not None else None,
                'notify_interval': str(data.get('notify_interval')) if data.get('notify_interval') is not None else None,
                'notify_change_precision': safe_float_conversion(data.get('notify_change_precision')),
            })
        elif device_type == 'actuator':
            parsed_data.update({
                'initial_value': safe_str_conversion(data.get('initial_value')),
                'off_value': safe_str_conversion(data.get('off_value')),
                'is_off': bool(data.get('is_off')) if data.get('is_off') is not None else None,
                'impact_step_size': safe_float_conversion(data.get('impact_step_size')),
            })
        
        # Remove None values to avoid overwriting existing data with None
        parsed_data = {k: v for k, v in parsed_data.items() if v is not None}
        
        logging.debug(f"Successfully parsed {device_type} payload with {len(parsed_data)} fields")
        return parsed_data
        
    except Exception as e:
        logging.error(f"Error parsing device payload: {str(e)}")
        return None
    
def validate_device_data(data, device_type):
    """
    Validate parsed device data for consistency
    
    Args:
        data (dict): Parsed device data
        device_type (str): 'sensor' or 'actuator'
    
    Returns:
        bool: True if data is valid, False otherwise
    """
    try:
        # Check required fields exist
        if not data.get('type_name'):
            logging.warning("Missing required field: type_name")
            return False
        
        # Validate numeric ranges
        if data.get('min_value') is not None and data.get('max_value') is not None:
            if data['min_value'] > data['max_value']:
                logging.warning(f"Invalid range: min_value ({data['min_value']}) > max_value ({data['max_value']})")
                return False
        
        # Validate device-specific fields
        if device_type == 'sensor':
            if data.get('read_interval') is not None and data['read_interval'] <= 0:
                logging.warning(f"Invalid read_interval: {data['read_interval']}")
                return False
        
        elif device_type == 'actuator':
            # Validate actuator-specific fields
            if data.get('is_off') is not None and not isinstance(data['is_off'], bool):
                logging.warning(f"Invalid is_off value: {data['is_off']}")
                return False
            
            # Validate that off_value is within min/max range if all are provided
            if (data.get('off_value') is not None and 
                data.get('min_value') is not None and 
                data.get('max_value') is not None):
                try:
                    off_val = float(data['off_value'])
                    if off_val < data['min_value'] or off_val > data['max_value']:
                        logging.warning(f"off_value ({off_val}) outside valid range [{data['min_value']}, {data['max_value']}]")
                        return False
                except (ValueError, TypeError):
                    # Skip validation if off_value is not numeric
                    pass
                
        # Additional validation can be added here
        
        return True
        
    except Exception as e:
        logging.error(f"Error validating device data: {str(e)}")
        return False