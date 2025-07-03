import logging
import json

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
        if len(parts) == 6 and parts[0] == expected_prefix and parts[5] != "all":
            logging.info(f"Detected message publish for request to gateway")
            return None
        if len(parts) != 6 or parts[0] != expected_prefix and parts[5] != "all":
            logging.warning(f"Invalid topic format: {topic}")
            return None
        
        _, floor_str, room_number, device_type, device_id, _ = parts
        
        # Convert floor to integer
        try:
            floor_number = int(floor_str)
            if floor_number < 0 or floor_number > 100:
                logging.warning(f"Floor number out of range: {floor_number}")
                return None
        except ValueError:
            logging.warning(f"Invalid floor number in topic: {floor_str}")
            return None
        
        return floor_number, room_number, device_type, device_id
    
    except Exception as e:
        logging.error(f"Error parsing topic {topic}: {str(e)}")
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
            'min_value': float(data.get('min')) if data.get('min') is not None else None,
            'max_value': float(data.get('max')) if data.get('max') is not None else None,
            'datatype': data.get('datatype'),
            'unit': data.get('unit'),
            'last_value': str(data.get('last_value')) if data.get('last_value') is not None else None,
        }
        
        # Extract device-specific fields
        if device_type == 'sensor':
            parsed_data.update({
                'read_interval': int(data.get('read_interval')) if data.get('read_interval') is not None else None,
                'notify_interval': str(data.get('notify_interval')) if data.get('notify_interval') is not None else None,
                'notify_change_precision': float(data.get('notify_change_precision')) if data.get('notify_change_precision') is not None else None,
            })
        elif device_type == 'actuator':
            parsed_data.update({
                'initial_value': str(data.get('initial_value')) if data.get('initial_value') is not None else None,
                'off_value': str(data.get('off_value')) if data.get('off_value') is not None else None,
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
                
        # Additional validation can be added here
        
        return True
        
    except Exception as e:
        logging.error(f"Error validating device data: {str(e)}")
        return False