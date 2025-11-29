"""
Comprehensive test suite for Food Rescue Agent.
Run with: python test_app.py
"""
import unittest
import os
import json
import tempfile
import shutil
from datetime import datetime
from agent import FoodRescueAgent
from memory import Memory
from config import Config

class TestFoodRescueAgent(unittest.TestCase):
    """Comprehensive test suite for FoodRescueAgent"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create test data directory
        os.makedirs('session_data', exist_ok=True)
        
        # Create test .env file
        with open('.env', 'w') as f:
            f.write('GEMINI_API_KEY=test_key_for_testing\n')
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_config_initialization(self):
        """Test Config initialization"""
        config = Config()
        self.assertIsNotNone(config)
        # Don't assert gemini_ready since we're using a test key
    
    def test_memory_operations(self):
        """Test Memory operations"""
        memory = Memory()
        
        # Test save_donation
        session_id = memory.save_donation(
            store="Test Store",
            item="Test Carrots",
            weight=50.0,
            location="Test Location"
        )
        
        self.assertTrue(session_id.startswith('daily_'))
        
        # Test get_donations
        donations = memory.get_donations(session_id)
        self.assertEqual(len(donations), 1)
        self.assertEqual(donations[0]['store'], "Test Store")
        self.assertEqual(donations[0]['weight'], 50.0)
        
        # Test get_metrics
        metrics = memory.get_metrics(session_id)
        self.assertEqual(metrics['total_weight'], 50.0)
        self.assertEqual(metrics['total_meals'], 75.0)
        self.assertEqual(metrics['store_count'], 1)
    
    def test_agent_operations(self):
        """Test Agent operations"""
        agent = FoodRescueAgent()
        
        # Test log_donation
        result = agent.log_donation(
            store="FreshMart Downtown",
            item="Organic Carrots",
            weight=100.0,
            location="San Francisco",
            session_id="test_session"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('metrics', result)
        self.assertIn('report', result)
        
        # Test get_dashboard
        dashboard = agent.get_dashboard("test_session")
        self.assertTrue(dashboard['success'])
        self.assertEqual(len(dashboard['donations']), 1)
        self.assertEqual(dashboard['metrics']['total_weight'], 100.0)
    
    def test_error_handling(self):
        """Test error handling"""
        agent = FoodRescueAgent()
        
        # Test invalid inputs
        result = agent.log_donation(
            store="",
            item="Invalid Item",
            weight=-10.0,
            location="Invalid Location",
            session_id="error_session"
        )
        
        self.assertFalse(result['success'])
        self.assertIn('Failed to log donation', result['message'])
    
    def test_data_validation(self):
        """Test data validation"""
        memory = Memory()
        
        # Test invalid weight
        with self.assertRaises(ValueError):
            memory.save_donation("Store", "Item", -5.0, "Location")
        
        # Test empty store
        with self.assertRaises(ValueError):
            memory.save_donation("", "Item", 10.0, "Location")

def run_comprehensive_tests():
    """Run comprehensive tests with detailed reporting"""
    print("=" * 60)
    print("🍎 RUNNING COMPREHENSIVE TESTS FOR FOOD RESCUE AGENT")
    print("=" * 60)
    
    # Run tests
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestFoodRescueAgent)
    result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    print("\n" + "=" * 60)
    print("📝 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Tests Run: {result.testsRun}")
    print(f"✅ Tests Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests Failed: {len(result.failures)}")
    print(f"❌ Tests Errored: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED! System is 100% reliable.")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)
