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
        topic = f"SCIoT_G02_2025/{device_id}/UPDATE"
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
        if not (device.min_value <= new_value <= device.max_value):
            logging.error(f'New value {new_value} for device {device_id} is out of range ({device.min_value}, {device.max_value})')
            return False

        # Convert payload to JSON string
        payload_json = json.dumps(payload)
        
        mqtt_client = current_app.mqtt_client
        
        # Publish the message
        if mqtt_client and mqtt_client.is_connected():
            result = mqtt_client.publish(topic, payload_json, qos=1)

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
        logging.error(f"Error publishing actuator update: {str(e)}")
        return False


def request_current_sensor_value(device_id: str) -> bool:
    """
    Generic function to request current sensor/actuator value via MQTT
        
    Returns:
        bool: True if request was sent successfully, False otherwise
    """
    try:
        topic = f"SCIoT_G02_2025/{device_id}/GET"
        
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
        
        mqtt_client = current_app.mqtt_client
        logging.info(f"After import mqtt_client: {mqtt_client}")
        
        # Publish the request
        if mqtt_client and mqtt_client.is_connected():
            result = mqtt_client.publish(topic, payload_json, qos=1)

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