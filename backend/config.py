import os
from dotenv import load_dotenv

load_dotenv()

class Config: 
    # Database settings
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    
    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MQTT settings
    MQTT_BROKER_HOST = os.environ.get('MQTT_BROKER_HOST')
    MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT'))
    MQTT_CLIENT_ID = os.environ.get('MQTT_CLIENT_ID')
    MQTT_TOPIC_SUBSCRIBE = os.environ.get('MQTT_TOPIC_SUBSCRIBE')