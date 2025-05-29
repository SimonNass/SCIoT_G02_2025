import logging
import paho.mqtt.client as mqtt
from backend.mqtt.utils.parsersUtils import parse_mqtt_topic
from backend.mqtt.utils.dbUtils import get_or_create_device
from backend.mqtt.utils.cacheUtils import initialize_device_cache

mqtt_client = None
app_instance = None

# Todo: Switch to device-id from sensor-id
# Todo: Cron job to remove devices that have not sent data in a while and remove room if all devices are gone

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker")
        # Subscribe to the topic
        subscribe_topic = app_instance.config['MQTT_TOPIC_SUBSCRIBE']
        client.subscribe(subscribe_topic)
        logging.info(f"Subscribed to {subscribe_topic}")
    else:
        logging.error(f"Failed to connect to MQTT broker with code: {rc}")

    initialize_device_cache(app_instance)

def on_message(client, userdata, msg):
    """
    Handle incoming MQTT messages
    Topic format: SCIoT_G02_2025/<floor_number>/<room_number>/<sensor-type>/<sensor-id>
    """
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        logging.info(f"Message received on topic {topic}")
        logging.debug(f"Payload: {payload}")
        
        # Parse the topic
        parsed = parse_mqtt_topic(topic, app_instance)
        if not parsed:
            logging.warning(f"Skipping message with invalid topic: {topic}")
            return
        
        floor_number, room_number, sensor_type, sensor_id = parsed
        
        # Get or create device
        device_info = get_or_create_device(app_instance, floor_number, room_number, sensor_type, sensor_id)
        
        if device_info:
            # Todo: Could process sensor data here i.e. write to redis?
            logging.info(f"Processed sensor data for device {sensor_id} ({sensor_type}) in room {room_number}, floor {floor_number}")
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
