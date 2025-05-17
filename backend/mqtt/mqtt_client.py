import logging
import paho.mqtt.client as mqtt

mqtt_client = None
app_instance = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker")
        # Subscribe to the topic
        subscribe_topic = app_instance.config['MQTT_TOPIC_SUBSCRIBE']
        client.subscribe(subscribe_topic)
        logging.info(f"Subscribed to {subscribe_topic}")
    else:
        logging.error(f"Failed to connect to MQTT broker with code: {rc}")

def on_message(client, userdata, msg):
    logging.info(f"Message received on topic {msg.topic}")


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