"""
Configuration management for OSEF
"""

import json
import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class OSEFConfig:
    """
    Configuration dataclass for OSEF parameters.
    """
    # Model parameters
    mu: float = 0.47
    omega_0: float = 1.23
    k_B: float = 0.12
    k_P: float = 0.09
    lambda_memory: float = 0.031
    
    # OSEF parameters
    window_size: int = 100
    sampling_rate: float = 8.0
    enable_guidance: bool = True
    
    # CCZ thresholds
    lambda_min: float = 0.01
    lambda_max: float = 0.5
    d_LC_min: float = 0.2
    d_LC_max: float = 0.8
    
    # Alert settings
    alert_cooldown: float = 5.0
    ccz_warning_duration: float = 120.0
    
    # Performance
    target_latency_ms: float = 10.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'model': {
                'mu': self.mu,
                'omega_0': self.omega_0,
                'k_B': self.k_B,
                'k_P': self.k_P,
                'lambda_memory': self.lambda_memory,
            },
            'osef': {
                'window_size': self.window_size,
                'sampling_rate': self.sampling_rate,
                'enable_guidance': self.enable_guidance,
            },
            'thresholds': {
                'lambda_min': self.lambda_min,
                'lambda_max': self.lambda_max,
                'd_LC_min': self.d_LC_min,
                'd_LC_max': self.d_LC_max,
            },
            'alerts': {
                'cooldown': self.alert_cooldown,
                'ccz_warning_duration': self.ccz_warning_duration,
            },
            'performance': {
                'target_latency_ms': self.target_latency_ms,
            }
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'OSEFConfig':
        """Create from dictionary."""
        return cls(
            mu=config_dict.get('model', {}).get('mu', 0.47),
            omega_0=config_dict.get('model', {}).get('omega_0', 1.23),
            k_B=config_dict.get('model', {}).get('k_B', 0.12),
            k_P=config_dict.get('model', {}).get('k_P', 0.09),
            lambda_memory=config_dict.get('model', {}).get('lambda_memory', 0.031),
            window_size=config_dict.get('osef', {}).get('window_size', 100),
            sampling_rate=config_dict.get('osef', {}).get('sampling_rate', 8.0),
            enable_guidance=config_dict.get('osef', {}).get('enable_guidance', True),
            lambda_min=config_dict.get('thresholds', {}).get('lambda_min', 0.01),
            lambda_max=config_dict.get('thresholds', {}).get('lambda_max', 0.5),
            d_LC_min=config_dict.get('thresholds', {}).get('d_LC_min', 0.2),
            d_LC_max=config_dict.get('thresholds', {}).get('d_LC_max', 0.8),
            alert_cooldown=config_dict.get('alerts', {}).get('cooldown', 5.0),
            ccz_warning_duration=config_dict.get('alerts', {}).get('ccz_warning_duration', 120.0),
            target_latency_ms=config_dict.get('performance', {}).get('target_latency_ms', 10.0),
        )


def load_baladi_params(phase: str = "approach") -> Dict[str, float]:
    """
    Load pre-calibrated parameters from Baladi et al. (2026).
    
    Args:
        phase: Flight phase - "approach", "cruise", or "emergency"
        
    Returns:
        Dictionary of parameters
    """
    params_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data/parameters/baladi_params.json'
    )
    
    try:
        with open(params_file, 'r') as f:
            data = json.load(f)
        
        phase_key = f"{phase}_phase"
        if phase_key not in data['parameters']:
            raise ValueError(f"Unknown phase: {phase}")
        
        return data['parameters'][phase_key]
        
    except FileNotFoundError:
        print(f"Warning: Parameters file not found at {params_file}")
        print("Using default approach phase parameters")
        return {
            'mu': 0.47,
            'omega_0': 1.23,
            'k_B': 0.12,
            'k_P': 0.09,
            'lambda_memory': 0.031,
        }
