from flask import Flask
import logging
from backend.config import Config
from backend.extensions import db
from backend.mqtt.mqtt_client import start_mqtt_client
from backend.routes import register_routes
# Necessary s.t. create_all() knows what models to create
from backend.models import models

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        with app.app_context():
            # Only creates new tabels if they don't already exist
            db.create_all()
    except Exception as e:
        app.logger.error(f"Error initializing database: {e}")
    
    register_routes(app)
    start_mqtt_client(app)
    
    return app