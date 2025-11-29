from memory import Memory
import datetime
import logging
from typing import Dict, Any, Optional
from prototype_agents import run_parallel_agents

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FoodRescueAgent:
    """
    Reliable agent system with comprehensive error handling and validation.
    Every method includes fallbacks and returns predictable results.
    """
    
    def __init__(self):
        """Initialize agent with validated components"""
        self.memory = Memory()
        logger.info("FoodRescueAgent initialized successfully")

    def run_multi_agents(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Run the parallel agent prototype and return consolidated results."""
        if not session_id:
            session_id = f"daily_{datetime.date.today().strftime('%Y%m%d')}"

        try:
            orchestration = run_parallel_agents(self.memory, session_id)
            logger.info(f"Parallel agents completed for session {session_id}")
            return {
                'success': True,
                'session_id': session_id,
                'orchestration': orchestration
            }
        except Exception as e:
            logger.error(f"Parallel agents failed: {str(e)}")
            return {
                'success': False,
                'session_id': session_id,
                'orchestration': None,
                'error': str(e)
            }
    
    def _validate_donation_inputs(self, store: str, item: str, weight: float, location: str) -> None:
        """Validate donation inputs with clear error messages"""
        if not store or not store.strip():
            raise ValueError("Store name cannot be empty")
        
        if not item or not item.strip():
            raise ValueError("Food item cannot be empty")
        
        if weight <= 0:
            raise ValueError("Weight must be greater than zero")
        
        if not location or not location.strip():
            raise ValueError("Location cannot be empty")
    
    def log_donation(self, store: str, item: str, weight: float, location: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Log donation with comprehensive validation and error handling.
        Always returns a consistent result structure.
        """
        try:
            if not session_id:
                session_id = f"daily_{datetime.date.today().strftime('%Y%m%d')}"
            
            # Validate inputs
            self._validate_donation_inputs(store, item, weight, location)
            
            # Save donation
            self.memory.save_donation(store, item, weight, location, session_id)
            
            # Get updated metrics and report
            metrics = self.memory.get_metrics(session_id)
            report = self.memory.generate_impact_report(session_id)
            
            result = {
                'success': True,
                'message': f"Successfully logged {weight} lbs of {item} from {store}",
                'session_id': session_id,
                'metrics': metrics,
                'report': report
            }
            
            logger.info(f"Donation logged successfully: {result}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Donation logging failed: {error_msg}")
            
            # Return consistent error structure
            return {
                'success': False,
                'message': f"Failed to log donation: {error_msg}",
                'session_id': session_id or f"daily_{datetime.date.today().strftime('%Y%m%d')}",
                'metrics': self.memory.get_metrics(session_id),
                'report': self.memory.generate_impact_report(session_id)
            }
    
    def get_dashboard(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get dashboard data with error handling.
        Always returns a complete dashboard structure.
        """
        if not session_id:
            session_id = f"daily_{datetime.date.today().strftime('%Y%m%d')}"
        
        try:
            donations = self.memory.get_donations(session_id)
            metrics = self.memory.get_metrics(session_id)
            report = self.memory.generate_impact_report(session_id)
            
            result = {
                'success': True,
                'session_id': session_id,
                'donations': donations,
                'metrics': metrics,
                'report': report,
                'last_updated': datetime.datetime.now().isoformat()
            }
            
            logger.info(f"Dashboard retrieved successfully for session: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Dashboard retrieval failed: {str(e)}")
            
            # Return safe fallback structure
            return {
                'success': False,
                'session_id': session_id,
                'donations': [],
                'metrics': {
                    'total_weight': 0.0,
                    'total_meals': 0.0,
                    'store_count': 0,
                    'donation_count': 0,
                    'average_weight': 0.0
                },
                'report': "🍎 No data available. Please check your setup.",
                'last_updated': datetime.datetime.now().isoformat()
            }
