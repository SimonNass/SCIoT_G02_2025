import logging
from backend.models import models

device_cache = {}

def initialize_device_cache(app_instance):
    """Initialize the device cache with existing devices from database"""
    global device_cache
    try:
        with app_instance.app_context():
            devices = models.Device.query.all()
            for device in devices:
                device_cache[device.device_id] = {
                    'id': device.id,
                    'room_id': device.room_id,
                    'device_type': device.device_type,
                    'name': device.name,
                    'is_online': device.is_online
                }
            logging.info(f"Device cache initialized with {len(device_cache)} devices")
    except Exception as e:
        logging.error(f"Failed to initialize device cache: {str(e)}")
