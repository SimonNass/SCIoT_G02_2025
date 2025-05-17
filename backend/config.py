import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig: 
    # Database settings
    DB_HOST = os.environ.get('DB_HOST', 'db')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'iot_database')
    DB_USER = os.environ.get('DB_USER', 'iot_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
    
    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MQTT settings
    MQTT_BROKER_HOST = os.environ.get('MQTT_BROKER_HOST', 'mqtt-broker')
    MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT', 1883))
    MQTT_CLIENT_ID = os.environ.get('MQTT_CLIENT_ID', 'flask_mqtt_client')
    MQTT_TOPIC_SUBSCRIBE = os.environ.get('MQTT_TOPIC_SUBSCRIBE', 'iot/+/data')