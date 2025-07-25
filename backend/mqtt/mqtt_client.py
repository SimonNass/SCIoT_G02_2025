import logging
import paho.mqtt.client as mqtt
from backend.mqtt.utils.parsersUtils import parse_mqtt_topic
from backend.mqtt.utils.dbUtils import get_or_create_device, process_sensor_actuator_mapping
from backend.mqtt.utils.cacheUtils import initialize_device_cache

# Configuration constants
MQTT_KEEPALIVE = 600
# At most once: 0, At least once 1 Exactly once 2
MQTT_QOS = 2
MAX_PAYLOAD_SIZE = 1024 * 10  # 10KB

mqtt_client = None
app_instance = None

def validate_mqtt_message(topic, payload):
    """
    Validate MQTT message for security and format
    """
    if not payload or len(payload) > MAX_PAYLOAD_SIZE:
        logging.warning(f"Invalid payload size: {len(payload) if payload else 0}")
        return False
    
    # Check for suspicious characters in topic
    if any(char in topic for char in ['<', '>', '"', "'"]):
        logging.warning(f"Suspicious characters in topic: {topic}")
        return False
    
    return True


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker")
        # Subscribe to the topic
        subscribe_topic = app_instance.config['MQTT_TOPIC_SUBSCRIBE']
        client.subscribe(subscribe_topic, qos=MQTT_QOS)
        logging.info(f"Subscribed to {subscribe_topic}")
        logging.info(f"MQTT_QOS: {MQTT_QOS}")
    else:
        logging.error(f"Failed to connect to MQTT broker with code: {rc}")
        return

    try:
        initialize_device_cache(app_instance)
    except Exception as e:
        logging.error(f"Failed to initialize device cache: {str(e)}")


def on_message(client, userdata, msg):
    """
    Handle incoming MQTT messages
    Topic format: SCIoT_G02_2025/<floor_number>/<room_number>/<device-type>/<device-id>
    type: {sensor, actuator}
    """
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        # Validate message
        if not validate_mqtt_message(topic, payload):
            logging.warning(f"Invalid MQTT message rejected: {topic}")
            return
        
        logging.info(f"Message received on topic {topic}")
        
        # Parse the topic
        parsed = parse_mqtt_topic(topic, app_instance)
        if not parsed:
            # logging.warning(f"Skipping message with topic: {topic}")
            return
        
        if parsed[2] == "mapping":
            logging.info(f"Parsed Topic: {parsed}")
            floor_number, room_number, _ = parsed
            success = process_sensor_actuator_mapping(app_instance, floor_number, room_number, payload)
            if success:
                logging.info(f"Successfully processed sensor-actuator mapping for floor {floor_number}, room {room_number}")
            else:
                logging.error(f"Failed to process sensor-actuator mapping for floor {floor_number}, room {room_number}")
            return
        
        floor_number, room_number, device_type, device_id = parsed
        
        # Get or create device with payload data
        device_info = get_or_create_device(app_instance, floor_number, room_number, device_type, device_id, payload)
        
        if device_info:
            logging.info(f"Processed device data for {device_id} ({device_type}) in room {room_number}, floor {floor_number}")
        else:
            logging.error(f"Failed to process device for topic: {topic}")
    
    except UnicodeDecodeError as e:
        logging.error(f"Failed to decode MQTT payload: {str(e)}")
    except Exception as e:
        logging.error(f"Error processing MQTT message: {str(e)}")


def on_disconnect(client, userdata, rc):
    """Handle MQTT disconnection"""
    if rc != 0:
        logging.warning(f"Unexpected MQTT disconnection (code: {rc})")
    else:
        logging.info("MQTT client disconnected")


def on_log(client, userdata, level, buf):
    """Handle MQTT client logging"""
    logging.debug(f"MQTT: {buf}")


def start_mqtt_client(app):
    global mqtt_client, app_instance
    app_instance = app
    
    # Create a new MQTT client instance
    mqtt_client = mqtt.Client()
    
    # Set up the callbacks
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_log = on_log
    
    # Connect to the broker
    host = app.config['MQTT_BROKER_HOST']
    port = app.config['MQTT_BROKER_PORT']
    
    try:
        mqtt_client.connect(host, port, MQTT_KEEPALIVE)
        # Start the loop in a background thread
        mqtt_client.loop_start()
        logging.info(f"MQTT client started and connecting to {host}:{port}")
        return mqtt_client
    except Exception as e:
        logging.error(f"Failed to connect to MQTT broker: {str(e)}")
        return None


def stop_mqtt_client():
    """Gracefully stop the MQTT client"""
    global mqtt_client
    if mqtt_client:
        try:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            logging.info("MQTT client stopped")
        except Exception as e:
            logging.error(f"Error stopping MQTT client: {str(e)}")