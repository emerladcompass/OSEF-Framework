"""
Unit tests for OSEF stability monitoring
"""

import unittest
import numpy as np
from osef import LimitCycleModel, OSEF
from osef.data.synthetic_data import generate_synthetic_flight


class TestOSEF(unittest.TestCase):
    """Test cases for OSEF stability monitoring."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.lc_model = LimitCycleModel.from_baladi_params()
        self.lc_model.compute_limit_cycle(duration=200, verbose=False)
        self.osef = OSEF(self.lc_model, window_size=100, sampling_rate=8.0, verbose=False)
    
    def test_initialization(self):
        """Test OSEF initialization."""
        self.assertIsNotNone(self.osef)
        self.assertEqual(self.osef.current_state, 'Initializing')
        self.assertEqual(self.osef.sampling_rate, 8.0)
        self.assertTrue(self.osef.enable_guidance)
    
    def test_process_sample_initializing(self):
        """Test processing during initialization phase."""
        result = self.osef.process_sample(0.0, 0.5, 1.0, 0.8)
        
        self.assertEqual(result['state'], 'Initializing')
        self.assertIsNone(result['lambda'])
        self.assertIsNone(result['d_LC'])
    
    def test_process_sample_after_warmup(self):
        """Test processing after warmup period."""
        # Fill buffer with 100 samples
        for i in range(100):
            t = i / 8.0
            P = 0.5 * np.sin(2 * np.pi * t / 5.1)
            B = 1.3 * np.sin(2 * np.pi * t / 5.1 - np.pi/4)
            W = 0.8
            self.osef.process_sample(t, P, B, W)
        
        # Next sample should have valid results
        result = self.osef.process_sample(12.5, 0.3, 0.8, 0.79)
        
        self.assertIsNotNone(result['lambda'])
        self.assertIsNotNone(result['d_LC'])
        self.assertIn(result['state'], ['Stable_LC', 'Creative_Chaos_Zone', 
                                         'Chaos', 'Converging_to_LC'])
    
    def test_state_classification(self):
        """Test state classification logic."""
        # Stable LC
        state = self.osef._classify_state(lambda_val=0.05, d_LC=0.1)
        self.assertEqual(state, 'Stable_LC')
        
        # CCZ
        state = self.osef._classify_state(lambda_val=0.2, d_LC=0.5)
        self.assertEqual(state, 'Creative_Chaos_Zone')
        
        # Chaos
        state = self.osef._classify_state(lambda_val=0.8, d_LC=0.5)
        self.assertEqual(state, 'Chaos')
    
    def test_alert_generation(self):
        """Test alert generation."""
        # No alert for stable LC
        alert = self.osef._generate_alert('Stable_LC', 5.0, 0.05, 0.1, 10.0)
        self.assertIsNone(alert)
        
        # Alert for CCZ entry
        alert = self.osef._generate_alert('Creative_Chaos_Zone', 2.0, 0.3, 0.5, 12.0)
        self.assertIsNotNone(alert)
        self.assertEqual(alert['level'], 'INFO')
    
    def test_metrics_tracking(self):
        """Test metrics are properly tracked."""
        # Process some samples
        flight_data = generate_synthetic_flight(duration=30, sampling_rate=8.0, 
                                               include_disturbance=False)
        
        for _, row in flight_data.iterrows():
            self.osef.process_sample(row['time'], row['P'], row['B'], row['W'])
        
        report = self.osef.get_summary_report()
        
        self.assertGreater(report['summary']['total_samples_processed'], 0)
        self.assertIn('ccz_statistics', report)
        self.assertIn('performance', report)
    
    def test_reset_metrics(self):
        """Test metrics reset."""
        # Process some samples
        for i in range(150):
            self.osef.process_sample(i/8.0, 0.5, 1.0, 0.8)
        
        # Reset
        self.osef.reset_metrics()
        
        self.assertEqual(self.osef.metrics['total_samples_processed'], 0)
        self.assertEqual(self.osef.metrics['ccz_entries'], 0)
    
    def test_full_flight_simulation(self):
        """Test processing a complete flight."""
        flight_data = generate_synthetic_flight(
            duration=60,
            sampling_rate=8.0,
            include_disturbance=True,
            disturbance_time=30.0
        )
        
        results = []
        for _, row in flight_data.iterrows():
            result = self.osef.process_sample(row['time'], row['P'], row['B'], row['W'])
            results.append(result)
        
        # Check that CCZ was detected
        ccz_detected = any(r['state'] == 'Creative_Chaos_Zone' for r in results 
                          if r['state'] is not None)
        self.assertTrue(ccz_detected, "CCZ should have been detected during disturbance")
        
        # Check report
        report = self.osef.get_summary_report()
        self.assertGreater(report['ccz_statistics']['total_entries'], 0)
    
    def test_performance_latency(self):
        """Test that processing latency meets requirements."""
        # Warmup
        for i in range(100):
            self.osef.process_sample(i/8.0, 0.5, 1.0, 0.8)
        
        # Measure latency
        latencies = []
        for i in range(100, 200):
            result = self.osef.process_sample(i/8.0, 0.5, 1.0, 0.8)
            if result['latency_ms'] is not None:
                latencies.append(result['latency_ms'])
        
        avg_latency = np.mean(latencies)
        
        # Should be under 10ms for real-time capability
        self.assertLess(avg_latency, 10.0, 
                       f"Average latency {avg_latency:.2f}ms exceeds 10ms target")


if __name__ == '__main__':
    unittest.main()
