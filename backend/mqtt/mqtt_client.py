import logging
import paho.mqtt.client as mqtt
from backend.models import models
from backend.extensions import db

mqtt_client = None
app_instance = None

device_cache = {}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker")
        # Subscribe to the topic
        subscribe_topic = app_instance.config['MQTT_TOPIC_SUBSCRIBE']
        client.subscribe(subscribe_topic)
        logging.info(f"Subscribed to {subscribe_topic}")
    else:
        logging.error(f"Failed to connect to MQTT broker with code: {rc}")

    initialize_device_cache()

def on_message(client, userdata, msg):
    """
    Handle incoming MQTT messages
    Topic format: iot/<floor>/<room>/<sensor-type>/<sensor-id>
    """
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        logging.info(f"Message received on topic {topic}")
        logging.debug(f"Payload: {payload}")
        
        # Parse the topic
        parsed = parse_mqtt_topic(topic)
        if not parsed:
            logging.warning(f"Skipping message with invalid topic: {topic}")
            return
        else: 
            logging.info("Valid message recieved")
        
        floor_number, room_number, sensor_type, sensor_id = parsed
        
        # Get or create device
        device_info = get_or_create_device(floor_number, room_number, sensor_type, sensor_id)
        
        if device_info:
            logging.info(f"Processed sensor data for device {sensor_id} ({sensor_type}) in room {room_number}, floor {floor_number}")
            # Todo: Could process sensor data here i.e. write to redis?
        else:
            logging.error(f"Failed to process device for topic: {topic}")
    
    except Exception as e:
        logging.error(f"Error processing MQTT message: {str(e)}")


def start_mqtt_client(app):
    global mqtt_client, app_instance
    app_instance = app
    
    # Create a new MQTT client instance
    mqtt_client = mqtt.Client()
    
    # Set up the callbacks
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    # Connect to the broker
    host = app.config['MQTT_BROKER_HOST']
    port = app.config['MQTT_BROKER_PORT']
    
    try:
        mqtt_client.connect(host, port, 60)
        # Start the loop in a background thread
        mqtt_client.loop_start()
        logging.info(f"MQTT client started and connecting to {host}:{port}")
    except Exception as e:
        logging.error(f"Failed to connect to MQTT broker: {str(e)}")

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
    
def initialize_device_cache():
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

def get_or_create_device(floor_number, room_number, sensor_type, sensor_id):
    """
    Get device from cache or create new device in database
    Returns: device info dict or None if error
    """
    global device_cache
    
    try:
        # Check if device already exists in cache
        if sensor_id in device_cache:
            logging.debug(f"Device {sensor_id} found in cache")
            # Update last seen status
            update_device_status(sensor_id, is_online=True)
            return device_cache[sensor_id]
        
        # Device not in cache, check database and create if needed
        with app_instance.app_context():
            floor = models.Floor.query.filter_by(floor_number=floor_number).first()
            if not floor:
                logging.error(f"Floor {floor_number} does not exist for device {sensor_id}")
                return None
            
            # Check if room exists
            room = models.Room.query.filter_by(room_number=room_number, floor_id=floor.id).first()
            if not room:
                logging.error(f"Room {room_number} on floor {floor_number} does not exist for device {sensor_id}")
                return None
            
            # Check if device already exists in database (might not be in cache)
            existing_device = models.Device.query.filter_by(device_id=sensor_id).first()
            
            if existing_device:
                # Device exists in DB but not in cache, add to cache
                device_info = {
                    'id': existing_device.id,
                    'room_id': existing_device.room_id,
                    'device_type': existing_device.device_type,
                    'name': existing_device.name,
                    'is_online': True
                }
                device_cache[sensor_id] = device_info
                
                # Update device status
                existing_device.is_online = True
                db.session.commit()
                
                logging.info(f"Device {sensor_id} added to cache from database")
                return device_info
            
            # Create new device
            device_name = f"{sensor_type.title()} - {room_number}"
            new_device = models.Device(
                device_id=sensor_id,
                name=device_name,
                device_type=sensor_type,
                description=f"{sensor_type} sensor in room {room_number} on floor {floor_number}",
                is_online=True,
                room_id=room.id
            )
            
            db.session.add(new_device)
            db.session.commit()
            
            # Add to cache
            device_info = {
                'id': new_device.id,
                'room_id': new_device.room_id,
                'device_type': new_device.device_type,
                'name': new_device.name,
                'is_online': True
            }
            device_cache[sensor_id] = device_info
            
            logging.info(f"New device created and cached: {sensor_id} ({sensor_type}) in room {room_number}, floor {floor_number}")
            return device_info
    
    except Exception as e:
        logging.error(f"Error creating/getting device {sensor_id}: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return None
    
def update_device_status(device_id, is_online=True):
    """Update device online status in database"""
    try:
        with app_instance.app_context():
            device = models.Device.query.filter_by(device_id=device_id).first()
            if device:
                device.is_online = is_online
                from datetime import datetime
                if is_online:
                    device.last_seen = datetime.utcnow()
                db.session.commit()
                
                # Update cache
                if device_id in device_cache:
                    device_cache[device_id]['is_online'] = is_online
                    
    except Exception as e:
        logging.error(f"Error updating device status for {device_id}: {str(e)}")