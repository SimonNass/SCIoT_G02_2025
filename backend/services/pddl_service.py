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
    
    def get_available_planners(self) -> List[str]:
        """Get list of available planners from the service"""
        try:
            response = requests.get(f"{self.planner_url}/planners")
            response.raise_for_status()
            return response.json().get('planners', [])
        except requests.RequestException as e:
            self.logger.error(f"Failed to get available planners: {e}")
            return []
    
    def solve_planning_problem(self, 
                             domain: str, 
                             problem: str, 
                             planner: str = "ff") -> Optional[Dict]:
        """
        Solve a PDDL planning problem
        
        Args:
            domain: PDDL domain definition as string
            problem: PDDL problem definition as string
            planner: Name of the planner to use (default: "ff")
        
        Returns:
            Dictionary containing the solution or None if failed
        """
        try:
            # Prepare the request payload
            payload = {
                "domain": domain,
                "problem": problem,
                "planner": planner
            }
            
            # Send request to planner service
            response = requests.post(
                f"{self.planner_url}/solve",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60  # 60 seconds timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('status') == 'ok':
                self.logger.info(f"Planning problem solved successfully with {planner}")
                return {
                    'success': True,
                    'plan': result.get('result', {}).get('plan', []),
                    'cost': result.get('result', {}).get('cost'),
                    'time': result.get('result', {}).get('time'),
                    'planner_used': planner
                }
            else:
                self.logger.error(f"Planning failed: {result.get('result', 'Unknown error')}")
                return {
                    'success': False,
                    'error': result.get('result', 'Unknown error'),
                    'planner_used': planner
                }
                
        except requests.Timeout:
            self.logger.error("Planning request timed out")
            return {'success': False, 'error': 'Planning request timed out'}
        
        except requests.RequestException as e:
            self.logger.error(f"Failed to solve planning problem: {e}")
            return {'success': False, 'error': str(e)}
    
    def health_check(self) -> bool:
        """Check if the planner service is available"""
        try:
            response = requests.get(f"{self.planner_url}/", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def validate_pddl(self, domain: str, problem: str) -> Dict:
        """
        Validate PDDL domain and problem files
        
        Args:
            domain: PDDL domain definition as string
            problem: PDDL problem definition as string
        
        Returns:
            Dictionary containing validation results
        """
        try:
            payload = {
                "domain": domain,
                "problem": problem
            }
            
            response = requests.post(
                f"{self.planner_url}/validate",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                'valid': result.get('status') == 'ok',
                'errors': result.get('result', {}).get('errors', []) if result.get('status') != 'ok' else []
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to validate PDDL: {e}")
            return {'valid': False, 'errors': [str(e)]}


# Example usage functions for your backend routes
def create_sample_planning_routes(app, pddl_service: PDDLPlannerService):
    """Example routes showing how to use the PDDL service"""
    
    @app.route('/api/planning/solve', methods=['POST'])
    def solve_problem():
        """Solve a planning problem"""
        from flask import request, jsonify
        
        data = request.get_json()
        domain = data.get('domain')
        problem = data.get('problem')
        planner = data.get('planner', 'ff')
        
        if not domain or not problem:
            return jsonify({'error': 'Domain and problem are required'}), 400
        
        result = pddl_service.solve_planning_problem(domain, problem, planner)
        return jsonify(result)
    
    @app.route('/api/planning/validate', methods=['POST'])
    def validate_pddl():
        """Validate PDDL files"""
        from flask import request, jsonify
        
        data = request.get_json()
        domain = data.get('domain')
        problem = data.get('problem')
        
        if not domain or not problem:
            return jsonify({'error': 'Domain and problem are required'}), 400
        
        result = pddl_service.validate_pddl(domain, problem)
        return jsonify(result)
    
    @app.route('/api/planning/health', methods=['GET'])
    def planning_health():
        """Check planner service health"""
        from flask import jsonify
        
        is_healthy = pddl_service.health_check()
        return jsonify({'healthy': is_healthy})
    
    @app.route('/api/planning/test', methods=['GET'])
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
        import logging

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
    