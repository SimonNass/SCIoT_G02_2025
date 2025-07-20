import requests
import logging
from typing import Dict, Optional
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
    
    def solve_planning_problem(self, domain: str, problem: str, planner: str, save_to_db: bool = True, scope=None,
                          target_floor_id: Optional[str] = None, target_room_id: Optional[str] = None) -> Optional[Dict]:
        """
        Solve a PDDL planning problem
        
        Args:
            domain: PDDL domain definition as string
            problem: PDDL problem definition as string
            planner: Name of the planner to use
            save_to_db: Whether to save the plan to database
            scope: The scope of the plan (building, floor, or room)
            target_floor_id: Optional floor ID if scope is floor or room
            target_room_id: Optional room ID if scope is room
        
        Returns:
            Dictionary containing the solution or None if failed
        """
        # Import inside the function to avoid circular imports
        from backend.models.models import PlanScope
        logging.info(f"solve_planning_problem called")
        
        # Set default scope if not provided
        if scope is None:
            scope = PlanScope.BUILDING
            
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
                celery_result = requests.post(self.planner_url + job_url)
                time.sleep(0.1)
            
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

                result_data = {
                    'success': True,
                    'plan': plan_actions,
                    'cost': cost,
                    'time': planner_time,
                    'raw_plan': raw_plan,
                    'stdout': plan_result.get('stdout', ''),
                    'stderr': plan_result.get('stderr', '')
                }
                if save_to_db:
                    from backend.services.utils.dbUtils import save_plan_to_database
                    save_plan_to_database(result_data, planner, scope, target_floor_id, target_room_id)

                return result_data
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