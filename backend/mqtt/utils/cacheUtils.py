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
                    'type_name': device.type_name,
                    'name': device.name,
                    'is_online': device.is_online
                }
            logging.info(f"Device cache initialized with {len(device_cache)} devices")
    except Exception as e:
        logging.error(f"Failed to initialize device cache: {str(e)}")


def remove_device_from_cache(device_id):
    """
    Remove a device from the cache
    """

    global device_cache
    try:
        if device_id in device_cache:
            del device_cache[device_id]
            logging.info(f"Device {device_id} removed from cache")
            return True
        logging.warning(f"Device {device_id} not found in cache")
        return False
    except Exception as e:
        logging.error(f"Failed to remove device {device_id} from cache: {str(e)}")
        return False