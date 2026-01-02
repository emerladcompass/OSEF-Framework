"""
Data preprocessing utilities
"""

import numpy as np
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None  # لاستخدامه لاحقاً
    print("Note: pandas not available, using numpy alternative")
from typing import Dict, Optional, List, Tuple
from scipy.signal import butter, filtfilt
import warnings


def preprocess_fdr_data(df: pd.DataFrame,
                       remove_outliers: bool = True,
                       filter_data: bool = True,
                       fill_gaps: bool = True) -> pd.DataFrame:
    """
    Preprocess FDR data for OSEF analysis.
    
    Steps:
    1. Remove outliers
    2. Fill gaps (interpolation)
    3. Apply low-pass filter
    4. Validate ranges
    
    Args:
        df: DataFrame with time, P, B, W columns
        remove_outliers: Remove statistical outliers
        filter_data: Apply low-pass filter
        fill_gaps: Interpolate small gaps
        
    Returns:
        Preprocessed DataFrame
    """
    df = df.copy()
    
    # 1. Remove outliers
    if remove_outliers:
        df = _remove_outliers(df)
    
    # 2. Fill gaps
    if fill_gaps:
        df = _fill_gaps(df)
    
    # 3. Filter
    if filter_data:
        df = _apply_filter(df)
    
    # 4. Validate
    df = _validate_ranges(df)
    
    return df


def _remove_outliers(df: pd.DataFrame, 
                    n_std: float = 3.0) -> pd.DataFrame:
    """
    Remove statistical outliers using z-score method.
    
    Args:
        df: Input DataFrame
        n_std: Number of standard deviations for outlier threshold
        
    Returns:
        DataFrame with outliers removed (NaN)
    """
    for col in ['P', 'B', 'W']:
        mean = df[col].mean()
        std = df[col].std()
        
        # Mark outliers as NaN
        outliers = np.abs(df[col] - mean) > (n_std * std)
        df.loc[outliers, col] = np.nan
        
        if outliers.sum() > 0:
            warnings.warn(f"Removed {outliers.sum()} outliers from {col}")
    
    return df


def _fill_gaps(df: pd.DataFrame, 
              max_gap_seconds: float = 5.0) -> pd.DataFrame:
    """
    Fill small gaps using linear interpolation.
    
    Args:
        df: Input DataFrame
        max_gap_seconds: Maximum gap size to fill
        
    Returns:
        DataFrame with gaps filled
    """
    # Compute time differences
    time_diffs = np.diff(df['time'])
    median_dt = np.median(time_diffs)
    max_gap_samples = int(max_gap_seconds / median_dt)
    
    # Interpolate each column
    for col in ['P', 'B', 'W']:
        df[col] = df[col].interpolate(
            method='linear',
            limit=max_gap_samples,
            limit_direction='both'
        )
    
    return df


def _apply_filter(df: pd.DataFrame,
                 cutoff_hz: float = 2.0,
                 order: int = 4) -> pd.DataFrame:
    """
    Apply low-pass Butterworth filter to remove high-frequency noise.
    
    Args:
        df: Input DataFrame
        cutoff_hz: Cutoff frequency in Hz
        order: Filter order
        
    Returns:
        Filtered DataFrame
    """
    # Determine sampling rate
    time_diffs = np.diff(df['time'])
    fs = 1.0 / np.median(time_diffs)
    
    # Design filter
    nyquist = fs / 2.0
    normal_cutoff = cutoff_hz / nyquist
    
    if normal_cutoff >= 1.0:
        warnings.warn(f"Cutoff frequency too high ({cutoff_hz} Hz), skipping filter")
        return df
    
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    
    # Apply to each column
    for col in ['P', 'B', 'W']:
        # Only filter if no NaN
        if not df[col].isna().any():
            df[col] = filtfilt(b, a, df[col])
    
    return df


def _validate_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clip values to physically reasonable ranges.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Validated DataFrame
    """
    # Typical ranges
    ranges = {
        'P': (-10, 30),   # Pitch: -10° to +30°
        'B': (-60, 60),   # Bank: -60° to +60°
        'W': (0, 1.2)     # Power: 0 to 120% (allow slight overshoot)
    }
    
    for col, (min_val, max_val) in ranges.items():
        # Count violations
        violations = (df[col] < min_val) | (df[col] > max_val)
        if violations.sum() > 0:
            warnings.warn(f"{violations.sum()} values outside range for {col}")
        
        # Clip
        df[col] = np.clip(df[col], min_val, max_val)
    
    return df


def normalize_state(P: float, B: float, W: float) -> np.ndarray:
    """
    Normalize state vector to standard scale.
    
    Normalization:
    - P: degrees (no change)
    - B: degrees (no change)
    - W: 0-1 (ensure normalized)
    
    Args:
        P: Pitch angle (degrees)
        B: Bank angle (degrees)
        W: Power (0-1 or 0-100)
        
    Returns:
        Normalized state vector [P, B, W]
    """
    # Normalize W if needed
    if W > 1.5:
        W = W / 100.0
    
    return np.array([P, B, W])


def compute_derivatives(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute time derivatives of P, B, W.
    
    Args:
        df: DataFrame with time, P, B, W
        
    Returns:
        DataFrame with added dP, dB, dW columns
    """
    df = df.copy()
    
    # Compute dt
    dt = np.diff(df['time'])
    
    # Compute derivatives (forward difference)
    for col in ['P', 'B', 'W']:
        diff = np.diff(df[col])
        rate = diff / dt
        
        # Pad with zero at the end
        rate = np.append(rate, 0)
        
        df[f'd{col}'] = rate
    
    return df


def segment_by_phase(df: pd.DataFrame,
                     phase_col: str = 'phase') -> Dict[str, pd.DataFrame]:
    """
    Segment data by flight phase.
    
    Args:
        df: DataFrame with flight phase column
        phase_col: Name of phase column
        
    Returns:
        Dictionary mapping phase name to DataFrame segment
    """
    if phase_col not in df.columns:
        warnings.warn(f"Phase column '{phase_col}' not found")
        return {'full_flight': df}
    
    segments = {}
    for phase in df[phase_col].unique():
        segments[phase] = df[df[phase_col] == phase].copy()
    
    return segments
