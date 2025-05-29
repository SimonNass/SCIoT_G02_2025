from functools import wraps
from flask import request, jsonify, current_app

def require_api_key(f):
    """Simple decorator to check API key from environment"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from headers
        provided_key = request.headers.get('X-API-Key')
        
        if not provided_key:
            return jsonify({'error': 'API key required in X-API-Key header'}), 401
        
        # Compare with environment variable
        expected_key = current_app.config.get('API_KEY')
        
        if not expected_key:
            return jsonify({'error': 'API key not configured on server'}), 500
        
        if provided_key != expected_key:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function