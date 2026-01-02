"""
Unit tests for data processing
"""

import unittest
import numpy as np
import pandas as pd
from osef.data.fdr_reader import FDRReader
from osef.data.preprocessing import preprocess_fdr_data, normalize_state
from osef.data.synthetic_data import generate_synthetic_flight, generate_ccz_scenario


class TestDataProcessing(unittest.TestCase):
    """Test cases for data processing."""
    
    def test_fdr_reader_initialization(self):
        """Test FDR reader initialization."""
        reader = FDRReader(sampling_rate=8.0)
        self.assertEqual(reader.sampling_rate, 8.0)
        self.assertEqual(reader.dt, 0.125)
    
    def test_synthetic_flight_generation(self):
        """Test synthetic flight data generation."""
        df = generate_synthetic_flight(duration=60, sampling_rate=8.0)
        
        self.assertIn('time', df.columns)
        self.assertIn('P', df.columns)
        self.assertIn('B', df.columns)
        self.assertIn('W', df.columns)
        
        # Check length
        expected_length = 60 * 8
        self.assertEqual(len(df), expected_length)
        
        # Check ranges
        self.assertTrue((df['P'] >= -10).all() and (df['P'] <= 30).all())
        self.assertTrue((df['B'] >= -60).all() and (df['B'] <= 60).all())
        self.assertTrue((df['W'] >= 0).all() and (df['W'] <= 1).all())
    
    def test_synthetic_flight_with_disturbance(self):
        """Test synthetic flight with disturbance event."""
        df = generate_synthetic_flight(
            duration=120,
            include_disturbance=True,
            disturbance_time=60.0
        )
        
        self.assertEqual(len(df), 120 * 8)
        
        # Check for increased variance during disturbance
        pre_disturbance = df[df['time'] < 60]
        during_disturbance = df[(df['time'] >= 60) & (df['time'] < 110)]
        
        pre_var = pre_disturbance['P'].var()
        during_var = during_disturbance['P'].var()
        
        self.assertGreater(during_var, pre_var)
    
    def test_ccz_scenario_generation(self):
        """Test CCZ scenario generation."""
        scenarios = ['engine_failure', 'weather', 'automation']
        
        for scenario in scenarios:
            df = generate_ccz_scenario(scenario)
            
            self.assertIsInstance(df, pd.DataFrame)
            self.assertIn('time', df.columns)
            self.assertGreater(len(df), 0)
    
    def test_preprocess_fdr_data(self):
        """Test FDR data preprocessing."""
        # Generate noisy data
        df = generate_synthetic_flight(duration=30, sampling_rate=8.0, noise_level=0.3)
        
        # Add some outliers
        df.loc[50, 'P'] = 100.0  # Outlier
        df.loc[100, 'B'] = -200.0  # Outlier
        
        # Preprocess
        df_clean = preprocess_fdr_data(df, remove_outliers=True)
        
        # Check outliers removed
        self.assertLess(df_clean['P'].max(), 50.0)
        self.assertGreater(df_clean['B'].min(), -100.0)
    
    def test_normalize_state(self):
        """Test state normalization."""
        # Power in percent
        state = normalize_state(P=5.0, B=10.0, W=75.0)
        
        self.assertEqual(state[0], 5.0)  # P unchanged
        self.assertEqual(state[1], 10.0)  # B unchanged
        self.assertEqual(state[2], 0.75)  # W normalized to 0-1
        
        # Power already normalized
        state2 = normalize_state(P=5.0, B=10.0, W=0.75)
        np.testing.assert_array_equal(state, state2)


if __name__ == '__main__':
    unittest.main()
