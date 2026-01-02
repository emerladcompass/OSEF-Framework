"""
Lyapunov Exponent Calculation
Real-time and offline methods for stability assessment
"""

import numpy as np
from typing import Optional, Tuple
import warnings


def compute_lyapunov_exponent(trajectory: np.ndarray,
                              embedding_dim: int = 3,
                              delay: int = 1,
                              min_nb: Optional[int] = None,
                              max_nb: Optional[int] = None) -> float:
    """
    Compute largest Lyapunov exponent using Rosenstein's algorithm.
    
    This is the primary method, but can be slow for real-time use.
    For real-time applications, use estimate_lyapunov_fast().
    
    Args:
        trajectory: Time series data (N x D array) or (N,) 1D array
        embedding_dim: Embedding dimension for phase space reconstruction
        delay: Time delay for embedding
        min_nb: Minimum temporal separation for neighbors
        max_nb: Maximum temporal separation for neighbors
        
    Returns:
        Largest Lyapunov exponent λ
        
    Raises:
        ValueError: If trajectory has insufficient data points
        
    References:
        Rosenstein, M. T. et al. (1993). A practical method for calculating 
        largest Lyapunov exponents from small data sets.
    """
    # Convert to numpy array
    if isinstance(trajectory, list):
        trajectory = np.array(trajectory)
    
    # Ensure 2D
    if trajectory.ndim == 1:
        trajectory = trajectory.reshape(-1, 1)
    
    n_points, n_dims = trajectory.shape
    
    # Validate input
    if n_points < 100:
        raise ValueError(f"Trajectory too short ({n_points} points). Need at least 100.")
    
    # Use nolds library (already in requirements)
    try:
        from nolds import lyap_e
        
        # Use first dimension if multi-dimensional
        data = trajectory[:, 0] if n_dims > 1 else trajectory.flatten()
        
        lambda_exp = lyap_e(
            data,
            emb_dim=embedding_dim,
            lag=delay,
            min_tsep=min_nb,
            max_tsep=max_nb
        )
        
        return float(lambda_exp)
        
    except ImportError:
        warnings.warn("nolds library not available. Using fallback method.")
        return _lyapunov_fallback(trajectory)
    except Exception as e:
        warnings.warn(f"Lyapunov calculation failed: {e}. Using fallback.")
        return _lyapunov_fallback(trajectory)


def estimate_lyapunov_fast(trajectory: np.ndarray,
                          window_size: int = 100) -> float:
    """
    Fast Lyapunov estimation for real-time applications.
    
    Uses local divergence rate over a sliding window.
    Trade-off: Speed vs. accuracy.
    
    Args:
        trajectory: Recent trajectory data (N x D array)
        window_size: Number of points to use (default 100)
        
    Returns:
        Estimated Lyapunov exponent λ
    """
    if len(trajectory) < window_size:
        # Not enough data yet
        return 0.0
    
    # Use last window_size points
    data = trajectory[-window_size:]
    
    try:
        # Quick and dirty: measure exponential divergence
        # Compute distances between consecutive points
        diffs = np.diff(data, axis=0)
        distances = np.linalg.norm(diffs, axis=1)
        
        # Avoid log(0)
        distances = np.maximum(distances, 1e-10)
        
        # Estimate exponential rate
        log_distances = np.log(distances)
        time_steps = np.arange(len(log_distances))
        
        # Linear fit: log(d) ~ λ*t
        if len(time_steps) > 10:
            coeffs = np.polyfit(time_steps, log_distances, 1)
            lambda_est = coeffs[0]
            
            # Clamp to reasonable range [-2, 2]
            lambda_est = np.clip(lambda_est, -2.0, 2.0)
            
            return float(lambda_est)
        else:
            return 0.0
            
    except Exception as e:
        warnings.warn(f"Fast Lyapunov estimation failed: {e}")
        return 0.0


def _lyapunov_fallback(trajectory: np.ndarray) -> float:
    """
    Fallback method if nolds is not available.
    Very simple estimate based on variance growth.
    
    Args:
        trajectory: Time series data
        
    Returns:
        Rough Lyapunov estimate
    """
    # Measure variance growth over time
    n_points = len(trajectory)
    n_segments = 5
    segment_size = n_points // n_segments
    
    variances = []
    for i in range(n_segments):
        start = i * segment_size
        end = start + segment_size
        if end > n_points:
            break
        segment = trajectory[start:end]
        var = np.var(segment, axis=0).mean()
        variances.append(var)
    
    if len(variances) < 2:
        return 0.0
    
    # Exponential growth rate of variance
    variances = np.array(variances)
    variances = np.maximum(variances, 1e-10)
    
    log_var = np.log(variances)
    time_steps = np.arange(len(log_var))
    
    coeffs = np.polyfit(time_steps, log_var, 1)
    lambda_est = coeffs[0] / 2.0  # Divide by 2 (variance ~ amplitude^2)
    
    return float(np.clip(lambda_est, -2.0, 2.0))


def classify_stability(lambda_exp: float) -> str:
    """
    Classify system stability based on Lyapunov exponent.
    
    Based on Baladi et al. (2026) thresholds:
    - λ < 0.01: Over-damped (too rigid)
    - 0.01 < λ < 0.1: Stable limit cycle (optimal)
    - 0.1 < λ < 0.5: Creative Chaos Zone (CCZ)
    - λ > 0.5: Full chaos (dangerous)
    
    Args:
        lambda_exp: Lyapunov exponent
        
    Returns:
        Classification string
    """
    if lambda_exp < 0.01:
        return "Over-damped"
    elif lambda_exp < 0.1:
        return "Stable LC"
    elif lambda_exp < 0.5:
        return "Creative Chaos Zone"
    else:
        return "Chaotic"


def is_in_ccz(lambda_exp: float, 
              d_LC: float,
              lambda_min: float = 0.01,
              lambda_max: float = 0.5,
              d_LC_min: float = 0.2,
              d_LC_max: float = 0.8) -> bool:
    """
    Determine if system is in Creative Chaos Zone.
    
    CCZ criteria from Baladi et al.:
    - 0.01 < λ < 0.5 AND
    - 0.2 < d_LC < 0.8
    
    Args:
        lambda_exp: Lyapunov exponent
        d_LC: Normalized distance to limit cycle
        lambda_min: Lower λ threshold (default 0.01)
        lambda_max: Upper λ threshold (default 0.5)
        d_LC_min: Lower d_LC threshold (default 0.2)
        d_LC_max: Upper d_LC threshold (default 0.8)
        
    Returns:
        True if in CCZ, False otherwise
    """
    lambda_condition = lambda_min < lambda_exp < lambda_max
    distance_condition = d_LC_min < d_LC < d_LC_max
    
    return lambda_condition and distance_condition
