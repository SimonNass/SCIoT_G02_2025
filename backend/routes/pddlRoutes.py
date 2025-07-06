from backend.extensions import pddl_service
import requests
from flask import current_app, jsonify, request, Blueprint
import time

pddl_api = Blueprint('pddl_api', __name__)

@pddl_api.route('/api/planning/solve', methods=['POST'])
def solve_problem():
    """Solve a planning problem"""
    request_data = request.get_json()
    
    # Validate that required fields are present
    if not request_data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    if "domain" not in request_data:
        return jsonify({"error": "Missing required field: domain"}), 400
    
    if "problem" not in request_data:
        return jsonify({"error": "Missing required field: problem"}), 400
    
    solve_result = pddl_service.solve_planning_problem(
        domain=request_data["domain"],
        problem=request_data["problem"],
        planner=request_data.get("planner"),
    )
    
    if solve_result.get('success'):
        return jsonify({
            "success": True,
            "plan": solve_result.get('plan'),
            "cost": solve_result.get('cost'),
            "time": solve_result.get('time'),
            "raw_plan": solve_result.get('raw_plan')
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": solve_result.get('error', 'Unknown error')
        }), 503

@pddl_api.route('/api/planning/solvers/list', methods=['GET'])
def list_solvers():
    """List available planning solvers"""
    solvers = pddl_service.get_solvers()
    if solvers:
        return jsonify(solvers), 200
    else:
        return jsonify({"error": "No solvers available"}), 503

@pddl_api.route('/api/planning/test', methods=['POST'])
def planning_test():
    request_data = request.get_json()

    # Validate that required fields are present
    if not request_data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    if "domain" not in request_data:
        return jsonify({"error": "Missing required field: domain"}), 400
    
    if "problem" not in request_data:
        return jsonify({"error": "Missing required field: problem"}), 400
    
    # Build the request body for the planning service
    req_body = {
        "domain": request_data["domain"],
        "problem": request_data["problem"]
    }

    planning_service_url = current_app.config.get('PDDL_PLANNING_SERVICE_URL', 'http://web:5001')

    # Send job request to solve endpoint
    solve_request_url=requests.post(f"{planning_service_url}/package/lama-first/solve", json=req_body).json()

    # Query the result in the job
    celery_result=requests.post(planning_service_url + solve_request_url['result'])

    while celery_result.json().get("status","")== 'PENDING':
        # Query the result every 0.5 seconds while the job is executing
        celery_result=requests.post(planning_service_url + solve_request_url['result'])
        time.sleep(0.5)
    
    return celery_result.json()