import json
import logging
from typing import Any
from backend.models import models
from flask import current_app

def request_actuator_update(device_id: str, new_value: Any) -> bool:
    """
    Generic function to set actuator value via MQTT
        
    Returns:
        bool: True if message was published successfully, False otherwise
    """
    try:

        payload = {
            "new_value": new_value
        }
        
        # Validate device information
        device = models.Device.query.filter_by(device_id=device_id).first()

        if not device:
            logging.error(f'Device {device_id} does not exist')
            return False

        # Check if device is an actuator
        if device.device_type.lower() != 'actuator':
            logging.error(f'Device {device_id} is not an actuator')
            return False
        
        # Check if new_value is in range
        if device.datatype != 'str':
            new_value = safe_float_conversion_for_sensor_data(new_value)
            if new_value is not None and not (safe_float_conversion_for_sensor_data(device.min_value) <= new_value <= safe_float_conversion_for_sensor_data(device.max_value)):
                logging.error(f'New value {new_value} for device {device_id} is out of range ({device.min_value}, {device.max_value})')
                return False
            if new_value is None:
                logging.error(f"Failed to update actuator value, new_value can not be None - device_id: {device_id}")
                return False
            
            payload = {
                "new_value": new_value
            }
        
        room = device.room
        floor = room.floor
        floor_number = floor.floor_number
        room_number = room.room_number

        # Build Topic
        topic = f"SCIoT_G02_2025/{floor_number}/{room_number}/actuator/{device_id}/UPDATE"

        # Convert payload to JSON string
        payload_json = json.dumps(payload)
        
        mqtt_client = current_app.mqtt_client
        
        # Publish the message
        if mqtt_client and mqtt_client.is_connected():
            result = mqtt_client.publish(topic, payload_json, qos=2)

            if result.rc == 0:
                logging.info(f"Actuator update published to {topic}: {payload_json}")
                return True
            else:
                logging.error(f"Failed to publish actuator update to {topic}, return code: {result.rc}")
                return False
        else:
            logging.error("MQTT client is not connected")
            return False
            
    except Exception as e:
        logging.error(f"Error publishing actuator update {device_id} - value: {new_value}: {str(e)}")
        return False
    
def request_sensor_update(device_id: str, new_value: Any) -> bool:
    """
    Generic function to set sensor value via MQTT
        
    Returns:
        bool: True if message was published successfully, False otherwise
    """
    try:

        payload = {
            "new_value": new_value
        }
        
        # Validate device information
        device = models.Device.query.filter_by(device_id=device_id).first()

        if not device:
            logging.error(f'Device {device_id} does not exist')
            return False

        # Check if device is an sensor
        if device.device_type.lower() != 'sensor':
            logging.error(f'Device {device_id} is not a sensor')
            return False
        
        # Check if new_value is in range
        if device.datatype != 'str':
            new_value = safe_float_conversion_for_sensor_data(new_value)
            if new_value is not None and not (safe_float_conversion_for_sensor_data(device.min_value) <= new_value <= safe_float_conversion_for_sensor_data(device.max_value)):
                logging.error(f'New value {new_value} for device {device_id} is out of range ({device.min_value}, {device.max_value})')
                return False
            if new_value is None:
                logging.error(f"Failed to update sensor value, new_value can not be None - device_id: {device_id}")
                return False
            
            payload = {
                "new_value": new_value
            }
        
        room = device.room
        floor = room.floor
        floor_number = floor.floor_number
        room_number = room.room_number

        # Build Topic
        topic = f"SCIoT_G02_2025/{floor_number}/{room_number}/sensor/{device_id}/UPDATE"

        # Convert payload to JSON string
        payload_json = json.dumps(payload)
        
        mqtt_client = current_app.mqtt_client
        
        # Publish the message
        if mqtt_client and mqtt_client.is_connected():
            logging.info("Calls publish")
            result = mqtt_client.publish(topic, payload_json, qos=2)

            if result.rc == 0:
                logging.info(f"Sensor update published to {topic}: {payload_json}")
                return True
            else:
                logging.error(f"Failed to publish Sensor update to {topic}, return code: {result.rc}")
                return False
        else:
            logging.error("MQTT client is not connected")
            return False
            
    except Exception as e:
        logging.error(f"Error publishing Sensor update {device_id} - value: {new_value}: {str(e)}")
        return False

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

def request_current_sensor_value(device_id: str) -> bool:
    """
    Generic function to request current sensor/actuator value via MQTT
        
    Returns:
        bool: True if request was sent successfully, False otherwise
    """
    try:
        payload = {}
        payload_json = json.dumps(payload)
        
        # Validate device information
        device = models.Device.query.filter_by(device_id=device_id).first()
        if not device:
            logging.error(f'Device {device_id} does not exist')
            return False

        # Check if device is a sensor
        if device.device_type.lower() != 'sensor':
            logging.error(f'Device {device_id} is not a sensor')
            return False
        
        room = device.room
        floor = room.floor
        floor_number = floor.floor_number
        room_number = room.room_number
        
        # Build topic
        topic = f"SCIoT_G02_2025/{floor_number}/{room_number}/sensor/{device_id}/GET"
        
        mqtt_client = current_app.mqtt_client
        logging.info(f"After import mqtt_client: {mqtt_client}")
        
        # Publish the request
        if mqtt_client and mqtt_client.is_connected():
            result = mqtt_client.publish(topic, payload_json, qos=2)

            if result.rc == 0:
                logging.info(f"Current value request published to {topic}")
                return True
            else:
                logging.error(f"Failed to publish current value request to {topic}, return code: {result.rc}")
                return False
        else:
            logging.error(mqtt_client)
            logging.error("MQTT client is not connected")
            return False
            
    except Exception as e:
        logging.error(f"Error requesting current value: {str(e)}")
        return False