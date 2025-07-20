from backend.extensions import pddl_service
import requests
from flask import current_app, jsonify, request, Blueprint
import time
from backend.models import models
from backend.aiplaning.pddl_converter_main import run_planner_with_db_data

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

# Get all plans
@pddl_api.route('/api/planning/plans/list', methods=['GET'])
def list_all_plans():
    """Get all PDDL plans"""
    try:
        plans = models.PDDLPlan.query.order_by(models.PDDLPlan.created_at.desc()).all()
        
        plans_data = []
        for plan in plans:
            plan_data = {
                'id': plan.id,
                'scope': plan.scope.value,
                'target_floor_id': plan.target_floor_id,
                'target_room_id': plan.target_room_id,
                'total_cost': plan.total_cost,
                'planning_time': plan.planning_time,
                'planner_used': plan.planner_used,
                'raw_plan': plan.raw_plan,
                'created_at': plan.created_at.isoformat(),
                'filtered_plan': plan.filtered_plan,
                'cleaning_plan': plan.cleaning_plan,
                'steps': []
            }
            
            # Include plan steps
            for step in plan.steps:
                step_data = {
                    'id': step.id,
                    'step_order': step.step_order,
                    'action_name': step.action_name,
                    'raw_step': step.raw_step,
                    'target_device_ids': step.target_device_ids
                }
                plan_data['steps'].append(step_data)
            
            plans_data.append(plan_data)
        
        return jsonify({
            'plans': plans_data,
            'total_plans': len(plans_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get all plans for a specific floor
@pddl_api.route('/api/planning/floors/<int:floor_number>/plans/list', methods=['GET'])
def list_plans_for_floor(floor_number):
    """Get all PDDL plans for a specific floor by floor number"""
    try:
        floor = models.Floor.query.filter_by(floor_number=floor_number).first()
        if not floor:
            return jsonify({'error': f'Floor {floor_number} does not exist'}), 404
        
        plans = models.PDDLPlan.query.filter_by(target_floor_id=floor.id).order_by(models.PDDLPlan.created_at.desc()).all()
        
        plans_data = []
        for plan in plans:
            plan_data = {
                'id': plan.id,
                'scope': plan.scope.value,
                'target_floor_id': plan.target_floor_id,
                'target_room_id': plan.target_room_id,
                'total_cost': plan.total_cost,
                'planning_time': plan.planning_time,
                'planner_used': plan.planner_used,
                'raw_plan': plan.raw_plan,
                'created_at': plan.created_at.isoformat(),
                'filtered_plan': plan.filtered_plan,
                'cleaning_plan': plan.cleaning_plan,
                'steps': []
            }
            
            # Include plan steps
            for step in plan.steps:
                step_data = {
                    'id': step.id,
                    'step_order': step.step_order,
                    'action_name': step.action_name,
                    'raw_step': step.raw_step,
                    'target_device_ids': step.target_device_ids
                }
                plan_data['steps'].append(step_data)
            
            plans_data.append(plan_data)
        
        return jsonify({
            'floor_number': floor_number,
            'floor_name': floor.floor_name,
            'plans': plans_data,
            'total_plans': len(plans_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get all plans for a specific room
@pddl_api.route('/api/planning/rooms/<string:room_number>/plans/list', methods=['GET'])
def list_plans_for_room(room_number):
    """Get all PDDL plans for a specific room by room number"""
    try:
        room = models.Room.query.filter_by(room_number=room_number).first()
        if not room:
            return jsonify({'error': f'Room {room_number} does not exist'}), 404
        
        plans = models.PDDLPlan.query.filter_by(target_room_id=room.id).order_by(models.PDDLPlan.created_at.desc()).all()
        
        plans_data = []
        for plan in plans:
            plan_data = {
                'id': plan.id,
                'scope': plan.scope.value,
                'target_floor_id': plan.target_floor_id,
                'target_room_id': plan.target_room_id,
                'total_cost': plan.total_cost,
                'planning_time': plan.planning_time,
                'planner_used': plan.planner_used,
                'raw_plan': plan.raw_plan,
                'created_at': plan.created_at.isoformat(),
                'steps': []
            }
            
            # Include plan steps
            for step in plan.steps:
                step_data = {
                    'id': step.id,
                    'step_order': step.step_order,
                    'action_name': step.action_name,
                    'raw_step': step.raw_step,
                    'target_device_ids': step.target_device_ids
                }
                plan_data['steps'].append(step_data)
            
            plans_data.append(plan_data)
        
        return jsonify({
            'room_number': room_number,
            'room_type': room.room_type,
            'plans': plans_data,
            'total_plans': len(plans_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get the latest plan (most recent)
@pddl_api.route('/api/planning/plans/latest', methods=['GET'])
def get_latest_plan():
    """Get the most recent PDDL plan"""
    try:
        plan = models.PDDLPlan.query.order_by(models.PDDLPlan.created_at.desc()).first()
        
        if not plan:
            return jsonify({'error': 'No plans found'}), 404
        
        plan_data = {
            'id': plan.id,
            'scope': plan.scope.value,
            'target_floor_id': plan.target_floor_id,
            'target_room_id': plan.target_room_id,
            'total_cost': plan.total_cost,
            'planning_time': plan.planning_time,
            'planner_used': plan.planner_used,
            'raw_plan': plan.raw_plan,
            'created_at': plan.created_at.isoformat(),
            'filtered_plan': plan.filtered_plan,
            'cleaning_plan': plan.cleaning_plan,
            'steps': []
        }
        
        # Include plan steps
        for step in plan.steps:
            step_data = {
                'id': step.id,
                'step_order': step.step_order,
                'action_name': step.action_name,
                'raw_step': step.raw_step,
                'target_device_ids': step.target_device_ids
            }
            plan_data['steps'].append(step_data)
        
        return jsonify(plan_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get the latest plan for a specific floor
@pddl_api.route('/api/planning/floors/<int:floor_number>/plans/latest', methods=['GET'])
def get_latest_plan_for_floor(floor_number):
    """Get the most recent PDDL plan for a specific floor by floor number"""
    try:
        floor = models.Floor.query.filter_by(floor_number=floor_number).first()
        if not floor:
            return jsonify({'error': f'Floor {floor_number} does not exist'}), 404
        
        plan = models.PDDLPlan.query.filter_by(target_floor_id=floor.id).order_by(models.PDDLPlan.created_at.desc()).first()
        
        if not plan:
            return jsonify({'error': f'No plans found for floor {floor_number}'}), 404
        
        plan_data = {
            'id': plan.id,
            'scope': plan.scope.value,
            'target_floor_id': plan.target_floor_id,
            'target_room_id': plan.target_room_id,
            'total_cost': plan.total_cost,
            'planning_time': plan.planning_time,
            'planner_used': plan.planner_used,
            'raw_plan': plan.raw_plan,
            'created_at': plan.created_at.isoformat(),
            'steps': []
        }
        
        # Include plan steps
        for step in plan.steps:
            step_data = {
                'id': step.id,
                'step_order': step.step_order,
                'action_name': step.action_name,
                'raw_step': step.raw_step,
                'target_device_ids': step.target_device_ids
            }
            plan_data['steps'].append(step_data)
        
        return jsonify({
            'floor_number': floor_number,
            'floor_name': floor.floor_name,
            'latest_plan': plan_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get the latest plan for a specific room
@pddl_api.route('/api/planning/rooms/<string:room_number>/plans/latest', methods=['GET'])
def get_latest_plan_for_room(room_number):
    """Get the most recent PDDL plan for a specific room by room number"""
    try:
        room = models.Room.query.filter_by(room_number=room_number).first()
        if not room:
            return jsonify({'error': f'Room {room_number} does not exist'}), 404
        
        plan = models.PDDLPlan.query.filter_by(target_room_id=room.id).order_by(models.PDDLPlan.created_at.desc()).first()
        
        if not plan:
            return jsonify({'error': f'No plans found for room {room_number}'}), 404
        
        plan_data = {
            'id': plan.id,
            'scope': plan.scope.value,
            'target_floor_id': plan.target_floor_id,
            'target_room_id': plan.target_room_id,
            'total_cost': plan.total_cost,
            'planning_time': plan.planning_time,
            'planner_used': plan.planner_used,
            'raw_plan': plan.raw_plan,
            'created_at': plan.created_at.isoformat(),
            'filtered_plan': plan.filtered_plan,
            'cleaning_plan': plan.cleaning_plan,
            'detected_activity_plan': plan.detected_activity_plan,
            'steps': []
        }
        
        # Include plan steps
        for step in plan.steps:
            step_data = {
                'id': step.id,
                'step_order': step.step_order,
                'action_name': step.action_name,
                'raw_step': step.raw_step,
                'target_device_ids': step.target_device_ids
            }
            plan_data['steps'].append(step_data)
        
        return jsonify({
            'room_number': room_number,
            'room_type': room.room_type,
            'latest_plan': plan_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@pddl_api.route('/api/planning/run_planner', methods=['GET'])
def run_planner_all():
    """Run planner for entire building"""
    try:
        plan = run_planner_with_db_data(True)
        plan_data = {
            'id': plan.id,
            'scope': plan.scope.value,
            'target_floor_id': plan.target_floor_id,
            'target_room_id': plan.target_room_id,
            'total_cost': plan.total_cost,
            'planning_time': plan.planning_time,
            'planner_used': plan.planner_used,
            'raw_plan': plan.raw_plan,
            'created_at': plan.created_at.isoformat(),
            'filtered_plan': plan.filtered_plan,
            'cleaning_plan': plan.cleaning_plan,
            'detected_activity_plan': plan.detected_activity_plan,
            'steps': []
        }
        
        # Include plan steps
        for step in plan.steps:
            step_data = {
                'id': step.id,
                'step_order': step.step_order,
                'action_name': step.action_name,
                'raw_step': step.raw_step,
                'target_device_ids': step.target_device_ids
            }
            plan_data['steps'].append(step_data)
        
        return jsonify(plan_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@pddl_api.route('/api/planning/run_planner/room/<string:room_number>', methods=['GET'])
def run_planner_specific_room(room_number):
    """Run planner for a specific room"""
    try:
        plan = run_planner_with_db_data(False, {}, [], room_number)
        plan_data = {
            'id': plan.id,
            'scope': plan.scope.value,
            'target_floor_id': plan.target_floor_id,
            'target_room_id': plan.target_room_id,
            'total_cost': plan.total_cost,
            'planning_time': plan.planning_time,
            'planner_used': plan.planner_used,
            'raw_plan': plan.raw_plan,
            'created_at': plan.created_at.isoformat(),
            'filtered_plan': plan.filtered_plan,
            'cleaning_plan': plan.cleaning_plan,
            'detected_activity_plan': plan.detected_activity_plan,
            'steps': []
        }
        
        # Include plan steps
        for step in plan.steps:
            step_data = {
                'id': step.id,
                'step_order': step.step_order,
                'action_name': step.action_name,
                'raw_step': step.raw_step,
                'target_device_ids': step.target_device_ids
            }
            plan_data['steps'].append(step_data)
        
        return jsonify(plan_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500