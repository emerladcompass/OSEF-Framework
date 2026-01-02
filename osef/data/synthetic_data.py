"""
Synthetic flight data generation for testing
"""

import numpy as np
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Note: pandas not available, using numpy alterna>
from typing import Dict, Optional, List, Tuple
import warnings
import os


def generate_synthetic_flight(duration: float = 300,
                              sampling_rate: float = 8.0,
                              include_disturbance: bool = True,
                              disturbance_time: Optional[float] = None,
                              noise_level: float = 0.1) -> pd.DataFrame:
    """
    Generate synthetic flight data for testing OSEF.
    
    Creates a trajectory that:
    1. Starts near limit cycle
    2. Includes a disturbance event (optional)
    3. Returns to limit cycle
    
    Args:
        duration: Flight duration in seconds
        sampling_rate: Sampling rate in Hz
        include_disturbance: Include disturbance event
        disturbance_time: When disturbance occurs (default: duration/3)
        noise_level: Measurement noise level
        
    Returns:
        DataFrame with time, P, B, W columns
    """
    dt = 1.0 / sampling_rate
    n_points = int(duration * sampling_rate)
    time = np.arange(n_points) * dt
    
    # Limit cycle parameters (from Baladi et al.)
    T_period = 5.1  # seconds
    omega = 2 * np.pi / T_period
    
    # Base limit cycle trajectory
    P_base = 0.5 * np.sin(omega * time)
    B_base = 1.3 * np.sin(omega * time - np.pi/4)
    W_base = 0.8 + 0.02 * np.sin(omega * time - np.pi/2)
    
    # Add disturbance if requested
    if include_disturbance:
        if disturbance_time is None:
            disturbance_time = duration / 3
        
        dist_start = int(disturbance_time * sampling_rate)
        dist_duration = int(50 * sampling_rate)  # 50 seconds
        dist_end = min(dist_start + dist_duration, n_points)
        
        # Disturbance envelope (ramps up then down)
        dist_env = np.zeros(n_points)
        ramp_up = np.linspace(0, 1, dist_duration // 3)
        steady = np.ones(dist_duration // 3)
        ramp_down = np.linspace(1, 0, dist_duration - 2*(dist_duration // 3))
        
        envelope = np.concatenate([ramp_up, steady, ramp_down])
        envelope = envelope[:dist_end - dist_start]
        dist_env[dist_start:dist_end] = envelope
        
        # Add disturbance
        P_base += dist_env * 3.0
        B_base += dist_env * 5.0
        W_base -= dist_env * 0.15
    
    # Add measurement noise
    P = P_base + np.random.randn(n_points) * noise_level
    B = B_base + np.random.randn(n_points) * noise_level
    W = W_base + np.random.randn(n_points) * (noise_level * 0.05)
    
    # Clip to valid ranges
    P = np.clip(P, -10, 30)
    B = np.clip(B, -60, 60)
    W = np.clip(W, 0, 1)
    
    return pd.DataFrame({
        'time': time,
        'P': P,
        'B': B,
        'W': W
    })


def generate_ccz_scenario(scenario: str = 'engine_failure') -> pd.DataFrame:
    """
    Generate specific CCZ scenario for testing.
    
    Scenarios:
    - 'engine_failure': Engine failure at V1
    - 'weather': Sudden weather deterioration
    - 'automation': Automation mismatch
    
    Args:
        scenario: Scenario name
        
    Returns:
        DataFrame with scenario data
    """
    if scenario == 'engine_failure':
        return _generate_engine_failure()
    elif scenario == 'weather':
        return _generate_weather_scenario()
    elif scenario == 'automation':
        return _generate_automation_mismatch()
    else:
        raise ValueError(f"Unknown scenario: {scenario}")


def _generate_engine_failure() -> pd.DataFrame:
    """Engine failure during takeoff."""
    duration = 120  # 2 minutes
    df = generate_synthetic_flight(
        duration=duration,
        include_disturbance=True,
        disturbance_time=10.0  # 10 seconds after start
    )
    
    # Simulate engine failure effects
    failure_idx = int(10 * 8)  # 8 Hz sampling
    
    # Asymmetric thrust
    df.loc[failure_idx:, 'B'] += 5.0  # Bank correction needed
    df.loc[failure_idx:, 'W'] *= 0.85  # Reduced power
    
    return df


def _generate_weather_scenario() -> pd.DataFrame:
    """Sudden weather deterioration on approach."""
    duration = 180  # 3 minutes
    df = generate_synthetic_flight(
        duration=duration,
        include_disturbance=True,
        disturbance_time=90.0  # Halfway through
    )
    
    # Turbulence effects
    turb_start = int(90 * 8)
    df.loc[turb_start:, 'P'] += np.random.randn(len(df) - turb_start) * 0.5
    df.loc[turb_start:, 'B'] += np.random.randn(len(df) - turb_start) * 1.5
    
    return df


def _generate_automation_mismatch() -> pd.DataFrame:
    """Automation commands unexpected maneuver."""
    duration = 150
    df = generate_synthetic_flight(
        duration=duration,
        include_disturbance=True,
        disturbance_time=60.0
    )
    
    # Sudden automation input
    auto_idx = int(60 * 8)
    df.loc[auto_idx:auto_idx+40, 'B'] += 10.0  # Unexpected bank
    
    return df
