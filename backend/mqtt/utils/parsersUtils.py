import logging

def parse_mqtt_topic(topic):
    """
    Parse MQTT topic: iot/<floor>/<room>/<sensor-type>/<sensor-id>
    Returns: (floor_number, room_number, sensor_type, sensor_id) or None if invalid
    """
    try:
        parts = topic.split('/')
        if len(parts) != 5 or parts[0] != 'iot':
            logging.warning(f"Invalid topic format: {topic}")
            return None
        
        _, floor_str, room_number, sensor_type, sensor_id = parts
        
        # Convert floor to integer
        try:
            floor_number = int(floor_str)
        except ValueError:
            logging.warning(f"Invalid floor number in topic: {floor_str}")
            return None
        
        return floor_number, room_number, sensor_type, sensor_id
    
    except Exception as e:
        logging.error(f"Error parsing topic {topic}: {str(e)}")
        return None
