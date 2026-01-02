"""
Unit tests for Guidance System
"""

import unittest
import numpy as np
from osef.core.guidance import GuidanceSystem


class TestGuidanceSystem(unittest.TestCase):
    """Test cases for Guidance System."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.guidance = GuidanceSystem()
    
    def test_initialization(self):
        """Test guidance system initialization."""
        self.assertIsNotNone(self.guidance)
        self.assertIn('Stable_LC', self.guidance.gains)
        self.assertIn('Creative_Chaos_Zone', self.guidance.gains)
    
    def test_compute_guidance_on_lc(self):
        """Test guidance when already on LC."""
        current = np.array([0.5, 1.0, 0.8])
        lc_nearest = np.array([0.5, 1.0, 0.8])  # Same point
        
        guidance = self.guidance.compute_guidance(
            current, lc_nearest, 'Stable_LC', d_LC=0.0
        )
        
        self.assertEqual(guidance['magnitude'], 0.0)
        self.assertEqual(guidance['components']['P'], 0.0)
    
    def test_compute_guidance_off_lc(self):
        """Test guidance when off LC."""
        current = np.array([2.0, 3.0, 0.6])
        lc_nearest = np.array([0.5, 1.0, 0.8])
        
        guidance = self.guidance.compute_guidance(
            current, lc_nearest, 'Converging_to_LC', d_LC=1.5
        )
        
        self.assertGreater(guidance['magnitude'], 0.0)
        self.assertEqual(len(guidance['direction']), 3)
        
        # Direction should point toward LC
        expected_direction = (lc_nearest - current) / np.linalg.norm(lc_nearest - current)
        np.testing.assert_array_almost_equal(guidance['direction'], expected_direction)
    
    def test_compute_guidance_in_ccz(self):
        """Test guidance in CCZ."""
        current = np.array([1.5, 2.0, 0.7])
        lc_nearest = np.array([0.5, 1.0, 0.8])
        
        guidance = self.guidance.compute_guidance(
            current, lc_nearest, 'Creative_Chaos_Zone', d_LC=0.8
        )
        
        # CCZ should have moderate guidance
        self.assertGreater(guidance['magnitude'], 0.0)
        self.assertLess(guidance['magnitude'], 1.0)
    
    def test_compute_guidance_in_chaos(self):
        """Test guidance in chaos state."""
        current = np.array([5.0, 8.0, 0.3])
        lc_nearest = np.array([0.5, 1.0, 0.8])
        
        guidance = self.guidance.compute_guidance(
            current, lc_nearest, 'Chaos', d_LC=3.0
        )
        
        # Chaos should have strong guidance
        self.assertGreater(guidance['magnitude'], 1.0)
    
    def test_recommended_action_generation(self):
        """Test recommendation generation."""
        current = np.array([2.0, 1.0, 0.8])
        lc_nearest = np.array([0.5, 1.0, 0.8])
        
        guidance = self.guidance.compute_guidance(
            current, lc_nearest, 'Converging_to_LC', d_LC=1.0
        )
        
        # Should recommend pitch correction
        self.assertIn('pitch', guidance['recommended_action'].lower())
    
    def test_set_gain(self):
        """Test setting custom gains."""
        original_gain = self.guidance.gains['Stable_LC']
        
        self.guidance.set_gain('Stable_LC', 0.5)
        self.assertEqual(self.guidance.gains['Stable_LC'], 0.5)
        
        # Restore
        self.guidance.set_gain('Stable_LC', original_gain)
    
    def test_get_gains(self):
        """Test getting gains dictionary."""
        gains = self.guidance.get_gains()
        
        self.assertIsInstance(gains, dict)
        self.assertIn('Stable_LC', gains)
        self.assertIn('Chaos', gains)


if __name__ == '__main__':
    unittest.main()
