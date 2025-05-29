import logging

def parse_mqtt_topic(topic):
    """
    Parse MQTT topic: SCIoT_G02_2025/<floor>/<room>/<sensor-type>/<sensor-id>
    Returns: (floor_number, room_number, sensor_type, sensor_id) or None if invalid
    """
    try:
        parts = topic.split('/')
        if len(parts) != 5 or parts[0] != 'SCIoT_G02_2025':
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

# Todo parse/verify payload
# Sensor:
# {
#   "id":str(self.id),
#   "name":self.name,
#   "type_name":self.type,
#   "connector":self.i2c_connector,
#   "connector_type":str(self.connector_type),
#   "min":self.min_value, 
#   "max":self.max_value, 
#   "datatype":self.datatype, 
#   "unit":self.unit, 
#   "read_interval":self.read_interval, 
#   "notify_interval":str(self.notify_interval), 
#   "notify_change_precision":self.notify_change_precision, 
#   "last_value":self.last_value
# }
# Actuator:
# {
#   "id":str(self.id),
#   "name":self.name,
#   "type_name":self.type,
#   "connector":self.i2c_connector,
#   "connector_type":str(self.connector_type),
#   "min":self.min_value, 
#   "max":self.max_value, 
#   "datatype":self.datatype, 
#   "unit":self.unit, 
#   "initial_value":self.initial_value, 
#   "off_value":self.off_value, 
#   "last_value":self.last_value
# }