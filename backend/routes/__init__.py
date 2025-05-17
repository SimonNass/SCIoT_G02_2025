from .api import api

def register_routes(app):
    app.register_blueprint(api)