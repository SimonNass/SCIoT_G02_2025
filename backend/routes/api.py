from flask import Blueprint, jsonify
from backend.extensions import db
from backend.models import models

api = Blueprint('api', __name__)

@api.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

@api.route('/devices')
def list_devices():
    devices = models.Device.query.all()
    return jsonify([{
        'id': d.id,
        'device_id': d.device_id,
        'name': d.name,
        'is_online': d.is_online,
    } for d in devices])

