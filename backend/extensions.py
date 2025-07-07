from flask_sqlalchemy import SQLAlchemy
from backend.services.pddl_service import PDDLPlannerService

db = SQLAlchemy()
pddl_service = PDDLPlannerService()