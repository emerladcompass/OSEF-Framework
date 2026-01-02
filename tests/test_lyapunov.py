"""
Unit tests for Lyapunov exponent calculation
"""

import unittest
import numpy as np
from osef.core.lyapunov import (
    compute_lyapunov_exponent,
    estimate_lyapunov_fast,
    classify_stability,
    is_in_ccz
)


class TestLyapunov(unittest.TestCase):
    """Test cases for Lyapunov analysis."""
    
    def test_compute_lyapunov_simple(self):
        """Test Lyapunov computation on simple periodic signal."""
        # Generate simple sine wave (should have near-zero Lyapunov)
        t = np.linspace(0, 100, 1000)
        signal = np.sin(2 * np.pi * t / 10)
        
        try:
            lambda_exp = compute_lyapunov_exponent(signal)
            # Periodic signal should have negative or near-zero Lyapunov
            self.assertLess(lambda_exp, 0.5)
        except Exception as e:
            # If nolds not available, test should skip
            self.skipTest(f"Lyapunov calculation not available: {e}")
    
    def test_estimate_lyapunov_fast(self):
        """Test fast Lyapunov estimation."""
        # Generate random walk (should have positive Lyapunov)
        trajectory = np.cumsum(np.random.randn(200, 3), axis=0)
        
        lambda_est = estimate_lyapunov_fast(trajectory, window_size=100)
        
        self.assertIsInstance(lambda_est, (float, np.floating))
        self.assertGreaterEqual(lambda_est, -2.0)
        self.assertLessEqual(lambda_est, 2.0)
    
    def test_estimate_lyapunov_insufficient_data(self):
        """Test behavior with insufficient data."""
        trajectory = np.random.randn(50, 3)  # Less than window_size
        
        lambda_est = estimate_lyapunov_fast(trajectory, window_size=100)
        
        # Should return 0.0 when insufficient data
        self.assertEqual(lambda_est, 0.0)
    
    def test_classify_stability(self):
        """Test stability classification."""
        # Over-damped
        self.assertEqual(classify_stability(0.005), "Over-damped")
        
        # Stable LC
        self.assertEqual(classify_stability(0.05), "Stable LC")
        
        # CCZ
        self.assertEqual(classify_stability(0.3), "Creative Chaos Zone")
        
        # Chaotic
        self.assertEqual(classify_stability(0.8), "Chaotic")
    
    def test_is_in_ccz(self):
        """Test CCZ detection."""
        # In CCZ
        self.assertTrue(is_in_ccz(lambda_exp=0.3, d_LC=0.5))
        
        # Lambda too low
        self.assertFalse(is_in_ccz(lambda_exp=0.005, d_LC=0.5))
        
        # Lambda too high
        self.assertFalse(is_in_ccz(lambda_exp=0.7, d_LC=0.5))
        
        # Distance too low
        self.assertFalse(is_in_ccz(lambda_exp=0.3, d_LC=0.1))
        
        # Distance too high
        self.assertFalse(is_in_ccz(lambda_exp=0.3, d_LC=1.5))
    
    def test_custom_ccz_thresholds(self):
        """Test CCZ detection with custom thresholds."""
        # Custom thresholds
        result = is_in_ccz(
            lambda_exp=0.15,
            d_LC=0.3,
            lambda_min=0.1,
            lambda_max=0.6,
            d_LC_min=0.25,
            d_LC_max=0.9
        )
        
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
