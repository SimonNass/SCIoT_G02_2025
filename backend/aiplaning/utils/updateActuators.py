import logging
from backend.mqtt.utils.mqttPublish import request_actuator_update
from backend.models.models import Device

def updateActuators(increse_actuator_plans: list, turn_off_actuator_plans: list, decrese_actuator_plans: list):
    try:
        devices = {device.device_id: device for device in Device.query.filter_by(device_type='actuator').all()}
        
        for plan in increse_actuator_plans:
            uuids = extract_uuids(plan)
            for uuid in uuids:
                device = devices.get(uuid)
                if device:
                    if device.datatype is 'str':
                        request_actuator_update(device.device_id, "Employee Notified")
                        continue
                    last_value_float: float = safe_float_conversion_for_sensor_data(device.last_value)
                    min_value_float = safe_float_conversion_for_sensor_data(device.min_value)
                    min_value_float = min_value_float if min_value_float is not None else 0
                    increase_value = max((last_value_float if last_value_float is not None else 0) + device.impact_step_size, min_value_float)
                    logging.info(f"Increase Value {increase_value}")
                    request_actuator_update(device.device_id, increase_value)

        for plan in turn_off_actuator_plans:
            uuids = extract_uuids(plan)
            for uuid in uuids:
                device = devices.get(uuid)
                if device:
                    logging.info(f"Defice Off {device.off_value}")
                    request_actuator_update(device.device_id, device.off_value)

        for plan in decrese_actuator_plans:
            uuids = extract_uuids(plan)
            for uuid in uuids:
                device = devices.get(uuid)
                if device:
                    if device.datatype is 'str':
                        request_actuator_update(device.device_id, "Employee Notified")
                        continue 
                    last_value_float: float = safe_float_conversion_for_sensor_data(device.last_value)
                    min_value_float = safe_float_conversion_for_sensor_data(device.min_value)
                    min_value_float = min_value_float if min_value_float is not None else 0
                    decrease_value = max((last_value_float if last_value_float is not None else 0) - device.impact_step_size, min_value_float)
                    logging.info(f"Decrease value: {decrease_value}")
                    request_actuator_update(device.device_id, decrease_value)
    except Exception as e:
        logging.error({'Error sending actuator updates': str(e)})
        
def extract_uuids(plan):
        # Skip first element and extract the UUID (last part after underscore)
        return [part.split('_')[-1] for part in plan[1:]]

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