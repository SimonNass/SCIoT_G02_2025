from .api import api
from .pddlRoutes import pddl_api

def register_routes(app):
    app.register_blueprint(api)
    app.register_blueprint(pddl_api)