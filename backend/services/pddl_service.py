# backend/services/pddl_service.py
import requests
import logging
from typing import Dict, Optional, List
from flask import current_app, jsonify, request
import time
from backend.services.utils.plannerParsers import parse_values_lama_first, parse_values_delfi, parse_values_dual_bfws_ffparser

class PDDLPlannerService:
    """Service to interact with the PDDL Planning-as-a-Service API"""
    
    def __init__(self, planner_url: str = None):
        self.planner_url = planner_url
        self.logger = logging.getLogger(__name__)
        self.app = None
        
        if planner_url:
            self.logger.info(f"PDDL Planner Service initialized with URL: {self.planner_url}")
    
    def init_app(self, app):
        """Initialize the service with the Flask app"""
        self.app = app
        self.planner_url = app.config.get('PLANNER_SERVICE_URL')
        self.logger.info(f"PDDL Planner Service initialized with URL: {self.planner_url}")
    
    def solve_planning_problem(self, domain: str, problem: str, planner: str) -> Optional[Dict]:
        """
        Solve a PDDL planning problem
        
        Args:
            domain: PDDL domain definition as string
            problem: PDDL problem definition as string
            planner: Name of the planner to use
        
        Returns:
            Dictionary containing the solution or None if failed
        """
        try:
            # Prepare the request payload
            payload = {
                "domain": domain,
                "problem": problem,
            }
            
            if not planner:
                self.logger.warning("planner not set using default planner")
                planner = "lama-first"  # Default planner if not specified
            
            # Step 1: Send job request to solve endpoint
            response = requests.post(
                f"{self.planner_url}/package/{planner}/solve",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10  # 10 seconds timeout
            )
            
            response.raise_for_status()
            job_response = response.json()
            
            if 'result' not in job_response:
                self.logger.error(f"No job ID received: {job_response}")
                return {'success': False, 'error': 'No job ID received from planning service'}
            
            job_url = job_response['result']
            self.logger.info(f"Planning job submitted, polling URL: {job_url}")

            # Step 2: Poll the job result endpoint until completion
            celery_result = requests.post(self.planner_url + job_url)
            
            while celery_result.json().get("status", "") == 'PENDING':
                # Query the result every 0.5 seconds while the job is executing
                celery_result = requests.post(self.planner_url + job_url)
                time.sleep(0.5)
            
            result = celery_result.json()
            
            if result.get('status') == 'ok':
                self.logger.info(f"Planning problem solved successfully")
                plan_result = result.get('result', {})
                
                if planner == "lama-first":
                    plan_actions, cost, planner_time, raw_plan = parse_values_lama_first(plan_result)
                elif planner == "dual-bfws-ffparser":
                    plan_actions, cost, planner_time, raw_plan = parse_values_dual_bfws_ffparser(plan_result)
                elif planner == "delfi":
                    plan_actions, cost, planner_time, raw_plan = parse_values_delfi(plan_result)
                else:
                    # Default to lama-first parser for unknown planners
                    plan_actions, cost, planner_time, raw_plan = parse_values_lama_first(plan_result)

                return {
                    'success': True,
                    'plan': plan_actions,
                    'cost': cost,
                    'time': planner_time,
                    'raw_plan': raw_plan,
                    'stdout': plan_result.get('stdout', ''),
                    'stderr': plan_result.get('stderr', '')
                }
            else:
                self.logger.error(f"Planning failed: {result.get('result', 'Unknown error')}")
                return {
                    'success': False,
                    'error': result.get('result', 'Unknown error')
                }
                
        except requests.Timeout:
            self.logger.error("Planning request timed out")
            return {'success': False, 'error': 'Planning request timed out'}
        
        except requests.RequestException as e:
            self.logger.error(f"Failed to solve planning problem: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_solvers(self) -> Dict:
        """Get available solvers from the planner service"""
        try:
            response = requests.get(f"{self.planner_url}/package")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Failed to connect to the PDDL planning service: {e}")
            return {}

# Example usage functions for your backend routes
def create_sample_planning_routes(app):
    """Example routes showing how to use the PDDL service"""
    from backend.extensions import pddl_service
    
    @app.route('/api/planning/solve', methods=['POST'])
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

    @app.route('/api/planning/solvers/list', methods=['GET'])
    def list_solvers():
        """List available planning solvers"""
        solvers = pddl_service.get_solvers()
        if solvers:
            return jsonify(solvers), 200
        else:
            return jsonify({"error": "No solvers available"}), 503
    
    @app.route('/api/planning/test', methods=['POST'])
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
    