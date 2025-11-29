import json
import os
import datetime
import logging
from config import Config
from jsonschema import validate, ValidationError
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# JSON Schema for validation
DONATION_SCHEMA = {
    "type": "object",
    "required": ["store", "item", "weight", "location", "timestamp", "session_id"],
    "properties": {
        "store": {"type": "string", "minLength": 1},
        "item": {"type": "string", "minLength": 1},
        "weight": {"type": "number", "minimum": 0.1},
        "location": {"type": "string", "minLength": 1},
        "timestamp": {"type": "string", "format": "date-time"},
        "session_id": {"type": "string", "minLength": 1}
    }
}

class Memory:
    """
    Bulletproof memory system with comprehensive error handling,
    data validation, and fallback mechanisms.
    """
    
    def __init__(self):
        """Initialize memory system with validation"""
        self.config = Config()
        self.data_dir = "session_data"
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists with proper permissions"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            # Test directory writability
            test_file = os.path.join(self.data_dir, ".test_write")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            logger.info(f"Data directory '{self.data_dir}' created and verified writable")
        except Exception as e:
            logger.error(f"Data directory setup failed: {str(e)}")
            raise RuntimeError(f"Cannot access data directory: {str(e)}")
    
    def _get_session_path(self, session_id: str) -> str:
        """Get validated session file path"""
        # Sanitize session_id to prevent path traversal
        safe_session_id = "".join(c for c in session_id if c.isalnum() or c in ['_', '-'])
        return os.path.join(self.data_dir, f"{safe_session_id}.json")
    
    def _validate_donation(self, donation: Dict[str, Any]) -> bool:
        """Validate donation data against schema"""
        try:
            validate(instance=donation, schema=DONATION_SCHEMA)
            return True
        except ValidationError as e:
            logger.error(f"Donation validation failed: {str(e)}")
            return False
    
    def save_donation(self, store: str, item: str, weight: float, location: str, session_id: Optional[str] = None) -> str:
        """
        Save donation with comprehensive error handling and validation.
        Returns session_id on success, raises exception on failure.
        """
        if not session_id:
            session_id = f"daily_{datetime.date.today().strftime('%Y%m%d')}"
        
        # Validate inputs
        if not all([store, item, location]):
            raise ValueError("Store, item, and location cannot be empty")
        
        if weight <= 0:
            raise ValueError("Weight must be greater than zero")
        
        # Create donation record
        donation = {
            'store': str(store).strip(),
            'item': str(item).strip(),
            'weight': float(weight),
            'location': str(location).strip(),
            'timestamp': datetime.datetime.now().isoformat(),
            'session_id': str(session_id).strip()
        }
        
        # Validate donation
        if not self._validate_donation(donation):
            raise ValueError("Donation data validation failed")
        
        try:
            session_path = self._get_session_path(session_id)
            
            # Load existing data or create new
            if os.path.exists(session_path):
                with open(session_path, 'r') as f:
                    try:
                        data = json.load(f)
                        if not isinstance(data, dict) or 'donations' not in data:
                            logger.warning(f"Session file {session_id} had invalid format, resetting")
                            data = {'donations': []}
                    except json.JSONDecodeError:
                        logger.warning(f"Session file {session_id} was corrupt, resetting")
                        data = {'donations': []}
            else:
                data = {'donations': []}
            
            # Add donation and save
            data['donations'].append(donation)
            
            with open(session_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Successfully saved donation to session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to save donation: {str(e)}")
            raise RuntimeError(f"Data storage failed: {str(e)}")
    
    def get_donations(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get donations with error handling for missing/invalid files.
        Returns empty list if no data available.
        """
        if not session_id:
            session_id = f"daily_{datetime.date.today().strftime('%Y%m%d')}"
        
        try:
            session_path = self._get_session_path(session_id)
            
            if not os.path.exists(session_path):
                logger.info(f"No data found for session: {session_id}")
                return []
            
            with open(session_path, 'r') as f:
                try:
                    data = json.load(f)
                    donations = data.get('donations', [])
                    
                    # Validate each donation
                    valid_donations = []
                    for donation in donations:
                        if self._validate_donation(donation):
                            valid_donations.append(donation)
                        else:
                            logger.warning(f"Invalid donation found in session {session_id}, skipping")
                    
                    logger.info(f"Retrieved {len(valid_donations)} valid donations for session: {session_id}")
                    return valid_donations
                    
                except json.JSONDecodeError:
                    logger.error(f"Session file {session_id} is corrupt")
                    return []
                except Exception as e:
                    logger.error(f"Error reading session file {session_id}: {str(e)}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to get donations: {str(e)}")
            return []
    
    def get_metrics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate metrics with zero-division protection and error handling.
        Returns default metrics if calculation fails.
        """
        donations = self.get_donations(session_id)
        
        try:
            total_weight = sum(d['weight'] for d in donations if 'weight' in d)
            total_meals = total_weight * 1.5  # 1 lb = 1.5 meals
            store_count = len(set(d['store'] for d in donations if 'store' in d))
            donation_count = len(donations)
            
            metrics = {
                'total_weight': float(total_weight),
                'total_meals': float(total_meals),
                'store_count': int(store_count),
                'donation_count': int(donation_count),
                'average_weight': float(total_weight / donation_count) if donation_count > 0 else 0.0
            }
            
            logger.info(f"Calculated metrics for session {session_id}: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics calculation failed: {str(e)}")
            return {
                'total_weight': 0.0,
                'total_meals': 0.0,
                'store_count': 0,
                'donation_count': 0,
                'average_weight': 0.0
            }
    
    def generate_impact_report(self, session_id: Optional[str] = None) -> str:
        """
        Generate impact report with comprehensive fallbacks.
        Always returns a valid report string.
        """
        if not session_id:
            session_id = f"daily_{datetime.date.today().strftime('%Y%m%d')}"
        
        metrics = self.get_metrics(session_id)
        
        if metrics['total_weight'] == 0:
            return "🍎 No donations logged yet. Start making an impact today!"
        
        try:
            return self.config.generate_impact_report(
                metrics['total_weight'],
                metrics['total_meals'],
                metrics['store_count']
            )
        except Exception as e:
            logger.error(f"Impact report generation failed: {str(e)}")
            return f"🍎 {metrics['total_weight']:.1f} lbs rescued today, providing {metrics['total_meals']:.0f} meals to families in need!"
