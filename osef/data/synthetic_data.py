"""
Synthetic flight data generation for OSEF testing.
"""

import numpy as np
from typing import Dict, Optional, Any

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None
    print("Note: pandas not available, using numpy alternative")


def generate_synthetic_flight(duration=300.0, sampling_rate=8.0, include_disturbance=True, disturbance_time=100.0):
    """
    Generate synthetic flight data for testing.
    
    Args:
        duration: Flight duration in seconds
        sampling_rate: Sampling rate in Hz
        include_disturbance: Include engine failure disturbance
        disturbance_time: Time of disturbance in seconds
        
    Returns:
        Flight data as DataFrame or dict
    """
    # Calculate number of samples
    n_samples = int(duration * sampling_rate)
    
    # Generate time vector
    time = np.linspace(0, duration, n_samples)
    
    # Generate nominal flight parameters
    P = 2.0 + 0.5 * np.sin(time/10) + 0.1 * np.random.randn(n_samples)
    B = -3.0 + 1.0 * np.cos(time/15) + 0.1 * np.random.randn(n_samples)
    W = np.full_like(time, 0.8)  # Normal power
    
    # Add disturbance (engine failure) - فقط إذا كان disturbance_time ضمن النطاق
    if include_disturbance and disturbance_time < duration:
        # Find index where time >= disturbance_time
        indices = np.where(time >= disturbance_time)[0]
        if len(indices) > 0:
            disturbance_idx = indices[0]
            # Sudden power loss
            W[disturbance_idx:] = 0.3 + 0.1 * np.random.randn(n_samples - disturbance_idx)
            # Increased oscillations in pitch
            P[disturbance_idx:] += 3.0 * np.sin(time[disturbance_idx:]/5)
            # Bank angle disturbance
            B[disturbance_idx:] -= 5.0 * np.exp(-(time[disturbance_idx:] - disturbance_time)/20.0)
    
    # Add noise
    P += 0.05 * np.random.randn(n_samples)
    B += 0.05 * np.random.randn(n_samples)
    
    # Package data
    if PANDAS_AVAILABLE and pd is not None:
        data = pd.DataFrame({
            'time': time,
            'P': P,
            'B': B,
            'W': W
        })
    else:
        data = {
            'time': time,
            'P': P,
            'B': B,
            'W': W
        }
    
    return data


def create_simple_flight_data():
    """
    Create simple flight data without any dependencies.
    
    Returns:
        Dictionary with time, P, B, W arrays
    """
    time = np.linspace(0, 60, 480)  # 1 minute at 8 Hz
    
    return {
        'time': time,
        'P': 2.0 + 0.5 * np.sin(time/10),
        'B': -3.0 + 1.0 * np.cos(time/15),
        'W': np.full_like(time, 0.8)
    }
