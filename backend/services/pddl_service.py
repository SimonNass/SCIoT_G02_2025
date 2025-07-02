# backend/services/pddl_service.py
import requests
import logging
from typing import Dict, Optional, List
from flask import current_app, jsonify, request
import requests
import time

class PDDLPlannerService:
    """Service to interact with the PDDL Planning-as-a-Service API"""
    
    def __init__(self, planner_url: str = None):
        self.planner_url = planner_url
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"PDDL Planner Service initialized with URL: {self.planner_url}")
    
    def solve_planning_problem(self, domain: str, problem: str, planner: str) -> Optional[Dict]:
        """
        Solve a PDDL planning problem
        
        Args:
            domain: PDDL domain definition as string
            problem: PDDL problem definition as string
        
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
                self.logger.error("planner not set using default planner")
                planner = "lama-first"  # Default planner if not specified
            
            
            # Send request to planner service
            response = requests.post(
                f"{self.planner_url}/{planner}/solve",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10  # 10 seconds timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('status') == 'ok':
                self.logger.info(f"Planning problem solved successfully")
                return {
                    'success': True,
                    'plan': result.get('result', {}).get('plan', []),
                    'cost': result.get('result', {}).get('cost'),
                    'time': result.get('result', {}).get('time')
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
    
    def get_solvers(self) -> bool:
        """Check if the planner service is available"""
        try:
            response = requests.get(f"{self.planner_url}/package")
            return response.json()
        except requests.RequestException:
            self.logger.error("Failed to connect to the PDDL planning service")
            return False

# Example usage functions for your backend routes
def create_sample_planning_routes(app, pddl_service: PDDLPlannerService):
    """Example routes showing how to use the PDDL service"""
    
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
        
        if "planner" not in request_data:
            return jsonify({"error": "Missing required field: planner"}), 400
        
        solve_problem = pddl_service.solve_planning_problem(
            domain=request_data["domain"],
            problem=request_data["problem"],
            planner=request_data["planner"],
        )
        
        if solve_problem.get('success'):
            return jsonify({
                "success": True,
                "plan": solve_problem.get('plan'),
                "cost": solve_problem.get('cost'),
                "time": solve_problem.get('time')
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": solve_problem.get('error', 'Unknown error')
            }), 503
    
    @app.route('/api/planning/solvers/list', methods=['GET'])
    def list_solvers():
        """List available planning solvers"""
        from flask import jsonify
        
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
    