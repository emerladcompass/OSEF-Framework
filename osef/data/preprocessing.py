"""
Data preprocessing utilities for FDR data.
"""

import numpy as np
from typing import Dict, List, Optional, Union, Any

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None


def preprocess_fdr_data(df: Any, 
                       time_col: str = 'time',
                       pitch_col: str = 'P',
                       bank_col: str = 'B',
                       power_col: str = 'W',
                       resample_rate: Optional[float] = None,
                       smooth: bool = True):
    """
    Preprocess FDR data for OSEF analysis.
    
    Args:
        df: Input data (DataFrame, dict, or list)
        time_col: Name of time column
        pitch_col: Name of pitch column
        bank_col: Name of bank column
        power_col: Name of power column
        resample_rate: Target sampling rate in Hz
        smooth: Apply smoothing filter
        
    Returns:
        Preprocessed data
    """
    # Convert input to numpy arrays
    if PANDAS_AVAILABLE and pd is not None and isinstance(df, pd.DataFrame):
        time = df[time_col].values
        pitch = df[pitch_col].values
        bank = df[bank_col].values
        power = df[power_col].values
    elif isinstance(df, dict):
        time = np.array(df.get(time_col, df.get('time', [])))
        pitch = np.array(df.get(pitch_col, df.get('P', [])))
        bank = np.array(df.get(bank_col, df.get('B', [])))
        power = np.array(df.get(power_col, df.get('W', [])))
    else:
        raise ValueError("Unsupported input type")
    
    # Check data
    if len(time) == 0:
        raise ValueError("No data provided")
    
    # Remove outliers (3-sigma filter)
    pitch = _remove_outliers(pitch)
    bank = _remove_outliers(bank)
    power = _remove_outliers(power)
    
    # Apply smoothing if requested
    if smooth:
        pitch = _smooth_data(pitch)
        bank = _smooth_data(bank)
        power = _smooth_data(power)
    
    # Resample if requested
    if resample_rate is not None:
        time, pitch = _resample_uniform(time, pitch, resample_rate)
        _, bank = _resample_uniform(time, bank, resample_rate)
        _, power = _resample_uniform(time, power, resample_rate)
    
    # Package results
    result = {
        'time': time,
        'P': pitch,
        'B': bank,
        'W': power
    }
    
    # Convert back to DataFrame if input was DataFrame
    if PANDAS_AVAILABLE and pd is not None and isinstance(df, pd.DataFrame):
        result = pd.DataFrame(result)
    
    return result


def _remove_outliers(data: np.ndarray, sigma_threshold: float = 3.0) -> np.ndarray:
    """
    Remove outliers using sigma clipping.
    
    Args:
        data: Input array
        sigma_threshold: Threshold for outlier removal
        
    Returns:
        Filtered array
    """
    if len(data) == 0:
        return data
    
    mean = np.mean(data)
    std = np.std(data)
    
    if std == 0:
        return data
    
    # Replace outliers with median
    mask = np.abs(data - mean) < sigma_threshold * std
    median_val = np.median(data[mask])
    
    result = data.copy()
    result[~mask] = median_val
    
    return result


def _smooth_data(data: np.ndarray, window_size: int = 5) -> np.ndarray:
    """
    Apply simple moving average smoothing.
    
    Args:
        data: Input array
        window_size: Size of moving average window
        
    Returns:
        Smoothed array
    """
    if len(data) <= window_size:
        return data
    
    window = np.ones(window_size) / window_size
    smoothed = np.convolve(data, window, mode='same')
    
    # Handle edges
    for i in range(window_size // 2):
        smoothed[i] = np.mean(data[:i + window_size // 2 + 1])
        smoothed[-i-1] = np.mean(data[-i - window_size // 2 - 1:])
    
    return smoothed


def _resample_uniform(time: np.ndarray, data: np.ndarray, target_rate: float) -> tuple:
    """
    Resample data to uniform sampling rate.
    
    Args:
        time: Original time vector
        data: Original data
        target_rate: Target sampling rate in Hz
        
    Returns:
        Tuple of (new_time, resampled_data)
    """
    if len(time) < 2:
        return time, data
    
    # Create uniform time grid
    t_start = time[0]
    t_end = time[-1]
    dt = 1.0 / target_rate
    n_points = int((t_end - t_start) * target_rate) + 1
    time_uniform = np.linspace(t_start, t_end, n_points)
    
    # Interpolate data
    data_resampled = np.interp(time_uniform, time, data)
    
    return time_uniform, data_resampled


def normalize_power(power_data: np.ndarray) -> np.ndarray:
    """
    Normalize power data to 0-1 range.
    
    Args:
        power_data: Power data (could be in percent or absolute)
        
    Returns:
        Normalized power (0-1)
    """
    if len(power_data) == 0:
        return power_data
    
    # If data looks like percentages (0-100), normalize
    if np.max(power_data) > 1.5:
        power_norm = power_data / 100.0
        # Clip to 0-1
        power_norm = np.clip(power_norm, 0.0, 1.0)
        return power_norm
    
    # Already normalized or unknown scale
    return power_data


def compute_derivatives(time: np.ndarray, data: np.ndarray) -> np.ndarray:
    """
    Compute time derivatives of data.
    
    Args:
        time: Time vector
        data: Data vector
        
    Returns:
        Derivative vector
    """
    if len(time) < 2 or len(data) < 2:
        return np.zeros_like(data)
    
    # Compute dt for each point
    dt = np.diff(time)
    # Handle zero or negative dt
    dt = np.where(dt <= 0, np.mean(dt[dt > 0]) if np.any(dt > 0) else 1.0, dt)
    
    # Compute derivative
    derivative = np.zeros_like(data)
    derivative[:-1] = np.diff(data) / dt
    
    # Last point uses backward difference
    if len(data) > 1:
        derivative[-1] = (data[-1] - data[-2]) / dt[-1] if len(dt) > 0 else 0
    
    return derivative
