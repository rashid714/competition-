"""
Health check endpoint for Cloud Run deployment.
This file is referenced by the HEALTHCHECK command in Dockerfile.
"""
import os
import sys
import json

def check_health():
    """Perform comprehensive health checks"""
    health_status = {
        'status': 'healthy',
        'checks': {},
        'timestamp': None
    }
    
    try:
        # Check data directory
        data_dir = "session_data"
        if os.path.exists(data_dir) and os.access(data_dir, os.W_OK):
            health_status['checks']['data_directory'] = 'healthy'
        else:
            health_status['checks']['data_directory'] = 'unhealthy'
            health_status['status'] = 'unhealthy'
        
        # Check environment variables
        gemini_key = os.getenv('GEMINI_API_KEY', '')
        if gemini_key and len(gemini_key) > 30 and 'your_' not in gemini_key.lower():
            health_status['checks']['gemini_api'] = 'healthy'
        else:
            health_status['checks']['gemini_api'] = 'unhealthy'
            # Don't mark whole system as unhealthy - Gemini is optional
        
        # Check required files
        required_files = ['app.py', 'config.py', 'memory.py', 'agent.py']
        for file in required_files:
            if os.path.exists(file):
                health_status['checks'][f'file_{file}'] = 'healthy'
            else:
                health_status['checks'][f'file_{file}'] = 'unhealthy'
                health_status['status'] = 'unhealthy'
        
        health_status['timestamp'] = datetime.datetime.now().isoformat()
        return health_status
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.datetime.now().isoformat()
        }

if __name__ == "__main__":
    health = check_health()
    print(json.dumps(health, indent=2))
    
    if health['status'] != 'healthy':
        sys.exit(1)
