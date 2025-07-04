import os
from flask import Flask
import logging
from backend.config import Config
from backend.extensions import db, pddl_service
from backend.mqtt.mqtt_client import start_mqtt_client
from backend.routes import register_routes
from backend.services.pddl_service import create_sample_planning_routes
# Necessary s.t. create_all() knows what models to create
from backend.models import models
from backend.cron.deviceCron import start_scheduler

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    pddl_service.init_app(app)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        with app.app_context():
            # Only creates new tables if they don't already exist
            db.create_all()
    except Exception as e:
        app.logger.error(f"Error initializing database: {e}")
    
    # Register routes
    register_routes(app)
    
    # Register planning routes
    create_sample_planning_routes(app)
    
    # Should prevent double initialization when debug=True (hopefully)
    app.mqtt_client = start_mqtt_client(app)
    start_scheduler(app)
    
    return app