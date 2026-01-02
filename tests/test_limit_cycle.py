"""
Unit tests for LimitCycleModel
"""

import unittest
import numpy as np
from osef.core.limit_cycle_model import LimitCycleModel


class TestLimitCycleModel(unittest.TestCase):
    """Test cases for Limit Cycle Model."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.model = LimitCycleModel()
    
    def test_initialization(self):
        """Test model initialization."""
        self.assertEqual(self.model.mu, 0.47)
        self.assertEqual(self.model.omega_0, 1.23)
        self.assertFalse(self.model.LC_computed)
    
    def test_from_baladi_params(self):
        """Test loading from Baladi parameters."""
        model = LimitCycleModel.from_baladi_params(phase="approach")
        self.assertIsNotNone(model)
        self.assertEqual(model.mu, 0.47)
    
    def test_dynamics(self):
        """Test dynamics function."""
        state = [0.1, 0.0, 0.1, 0.0, 0.5]
        dstate = self.model.dynamics(0.0, state)
        
        self.assertEqual(len(dstate), 5)
        self.assertIsInstance(dstate[0], (float, np.floating))
    
    def test_compute_limit_cycle(self):
        """Test limit cycle computation."""
        lc = self.model.compute_limit_cycle(duration=200, verbose=False)
        
        self.assertTrue(self.model.LC_computed)
        self.assertIsNotNone(self.model.LC_period)
        self.assertGreater(self.model.LC_period, 0)
        self.assertIn('trajectory', lc)
    
    def test_get_closest_lc_point(self):
        """Test finding closest LC point."""
        self.model.compute_limit_cycle(duration=200, verbose=False)
        
        current_state = np.array([0.5, 1.0, 0.8])
        closest, idx = self.model.get_closest_lc_point(current_state)
        
        self.assertEqual(len(closest), 3)
        self.assertIsInstance(idx, (int, np.integer))
    
    def test_simulate(self):
        """Test trajectory simulation."""
        initial_state = [0.1, 0.0, 0.1, 0.0, 0.5]
        result = self.model.simulate((0, 10), initial_state, n_points=100)
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['P']), 100)
    
    def test_get_parameters(self):
        """Test parameter retrieval."""
        params = self.model.get_parameters()
        
        self.assertIn('mu', params)
        self.assertIn('omega_0', params)
        self.assertEqual(params['mu'], 0.47)


if __name__ == '__main__':
    unittest.main()
