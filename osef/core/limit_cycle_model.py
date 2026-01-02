"""
Limit Cycle Model based on Van der Pol Oscillator
Implements the foundational dynamics from Baladi et al. (2026)
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.fft import fft, fftfreq
from typing import Dict, Tuple, Optional, List
import json
import os


class LimitCycleModel:
    """
    Van der Pol based limit cycle model for flight dynamics.
    
    Implements 3D dynamics in (P, B, W) state space:
    - P: Pitch (Technical Rigor)
    - B: Bank (Operational Flexibility)  
    - W: Power/Memory (Institutional Memory)
    
    Based on: Baladi, S. et al. (2026). Limit Cycle Flight Dynamics...
    DOI: 10.17605/OSF.IO/RJBDK
    """
    
    def __init__(self, 
                 mu: float = 0.47,
                 omega_0: float = 1.23,
                 k_B: float = 0.12,
                 k_P: float = 0.09,
                 lambda_memory: float = 0.031):
        """
        Initialize Limit Cycle Model.
        
        Args:
            mu: Nonlinearity parameter (default from Baladi et al., approach phase)
            omega_0: Natural frequency in rad/s
            k_B: Bank coupling coefficient
            k_P: Pitch coupling coefficient
            lambda_memory: Memory decay rate in 1/s
        """
        self.mu = mu
        self.omega_0 = omega_0
        self.k_B = k_B
        self.k_P = k_P
        self.lambda_memory = lambda_memory
        
        # Limit cycle properties (computed after compute_limit_cycle())
        self.LC_reference = None
        self.LC_computed = False
        self.LC_period = None
        self.LC_center = None
        self.LC_radius = None
        
    @classmethod
    def from_baladi_params(cls, phase: str = "approach") -> 'LimitCycleModel':
        """
        Create model from pre-calibrated Baladi et al. parameters.
        
        Args:
            phase: Flight phase - "approach", "cruise", or "emergency"
            
        Returns:
            LimitCycleModel instance with validated parameters
        """
        # Load parameters from JSON file
        params_file = os.path.join(
            os.path.dirname(__file__), 
            '../data/parameters/baladi_params.json'
        )
        
        try:
            with open(params_file, 'r') as f:
                data = json.load(f)
            
            phase_params = data['parameters'].get(f"{phase}_phase")
            if phase_params is None:
                raise ValueError(f"Unknown phase: {phase}")
            
            return cls(
                mu=phase_params['mu'],
                omega_0=phase_params['omega_0'],
                k_B=phase_params['k_B'],
                k_P=phase_params['k_P'],
                lambda_memory=phase_params['lambda_memory']
            )
        except FileNotFoundError:
            print(f"Warning: Parameters file not found. Using default values.")
            return cls()
    
    def dynamics(self, t: float, state: np.ndarray) -> List[float]:
        """
        Van der Pol 3D dynamics equations.
        
        State vector: [P, V_p, B, V_b, W]
        - P: Pitch angle
        - V_p: Pitch velocity (dP/dt)
        - B: Bank angle
        - V_b: Bank velocity (dB/dt)
        - W: Power/Memory state
        
        Args:
            t: Time (not explicitly used, autonomous system)
            state: Current state vector [P, V_p, B, V_b, W]
            
        Returns:
            List of derivatives [dP/dt, dV_p/dt, dB/dt, dV_b/dt, dW/dt]
        """
        P, V_p, B, V_b, W = state
        
        # Pitch dynamics (Van der Pol oscillator)
        dP = V_p
        dV_p = self.mu * (1 - P**2) * V_p - self.omega_0**2 * P + self.k_B * B
        
        # Bank dynamics (coupled Van der Pol)
        dB = V_b
        dV_b = self.mu * (1 - B**2) * V_b - self.omega_0**2 * B + self.k_P * P
        
        # Power/Memory dynamics (exponential decay + documentation)
        dW = -self.lambda_memory * W + self._documentation_rate(P, B)
        
        return [dP, dV_p, dB, dV_b, dW]
    
    def _documentation_rate(self, P: float, B: float) -> float:
        """
        Documentation rate based on deviations.
        
        Larger deviations require more documentation/memory updates.
        
        Args:
            P: Pitch angle
            B: Bank angle
            
        Returns:
            Documentation rate
        """
        return 0.1 * (abs(P) + abs(B))
    
    def compute_limit_cycle(self, 
                           duration: float = 1000,
                           n_points: int = 10000,
                           initial_state: Optional[np.ndarray] = None,
                           verbose: bool = True) -> Dict:
        """
        Compute reference limit cycle trajectory.
        
        This is done offline during initialization by integrating
        the system for a long time until it converges to the limit cycle.
        
        Args:
            duration: Integration duration (seconds)
            n_points: Number of time points
            initial_state: Initial conditions [P, V_p, B, V_b, W]
            verbose: Print progress messages
            
        Returns:
            Dictionary containing limit cycle trajectory and characteristics
        """
        if verbose:
            print(f"Computing reference limit cycle (T={duration}s)...")
        
        # Initial conditions (small perturbation from origin)
        if initial_state is None:
            initial_state = [0.1, 0.0, 0.1, 0.0, 0.5]
        
        # Integrate system
        t_span = (0, duration)
        t_eval = np.linspace(0, duration, n_points)
        
        sol = solve_ivp(
            self.dynamics,
            t_span,
            initial_state,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-6,
            atol=1e-9
        )
        
        if not sol.success:
            raise RuntimeError(f"Integration failed: {sol.message}")
        
        # Extract last cycles (steady state)
        # Use last 10% of trajectory as limit cycle reference
        n_last = int(0.1 * n_points)
        
        self.LC_reference = {
            'P': sol.y[0, -n_last:],
            'V_p': sol.y[1, -n_last:],
            'B': sol.y[2, -n_last:],
            'V_b': sol.y[3, -n_last:],
            'W': sol.y[4, -n_last:],
            'time': sol.t[-n_last:],
            'trajectory': np.vstack([
                sol.y[0, -n_last:],  # P
                sol.y[2, -n_last:],  # B
                sol.y[4, -n_last:]   # W
            ]).T
        }
        
        # Compute limit cycle characteristics
        self.LC_period = self._estimate_period()
        self.LC_center = np.mean(self.LC_reference['trajectory'], axis=0)
        self.LC_radius = np.std(self.LC_reference['trajectory'], axis=0)
        
        self.LC_computed = True
        
        if verbose:
            print(f"✓ LC computed successfully:")
            print(f"  Period:  T = {self.LC_period:.2f} s")
            print(f"  Center:  {self.LC_center}")
            print(f"  Radius:  {self.LC_radius}")
        
        return self.LC_reference
    
    def _estimate_period(self) -> float:
        """
        Estimate limit cycle period using FFT.
        
        Returns:
            Period in seconds
        """
        P = self.LC_reference['P']
        n = len(P)
        
        # Remove mean
        P_centered = P - np.mean(P)
        
        # FFT
        P_fft = fft(P_centered)
        freqs = fftfreq(n, d=1.0)  # Assuming unit time steps
        
        # Find dominant frequency (exclude DC component)
        positive_freqs = freqs[1:n//2]
        positive_fft = np.abs(P_fft[1:n//2])
        
        if len(positive_fft) > 0:
            idx = np.argmax(positive_fft)
            dominant_freq = positive_freqs[idx]
            
            if dominant_freq > 0:
                return 1.0 / dominant_freq
        
        # Fallback to default from Baladi et al.
        return 5.1
    
    def get_closest_lc_point(self, 
                            current_state: np.ndarray) -> Tuple[np.ndarray, int]:
        """
        Find closest point on limit cycle to current state.
        
        Args:
            current_state: Current [P, B, W] state
            
        Returns:
            Tuple of (closest_lc_point, index)
        """
        if not self.LC_computed:
            raise RuntimeError("Limit cycle not computed. Call compute_limit_cycle() first.")
        
        # Compute distances to all LC points
        distances = np.linalg.norm(
            self.LC_reference['trajectory'] - current_state,
            axis=1
        )
        
        # Find minimum distance
        min_idx = np.argmin(distances)
        closest_point = self.LC_reference['trajectory'][min_idx]
        
        return closest_point, min_idx
    
    def simulate(self, 
                t_span: Tuple[float, float],
                initial_state: np.ndarray,
                n_points: int = 1000) -> Dict:
        """
        Simulate system from given initial conditions.
        
        Args:
            t_span: Time span (t_start, t_end)
            initial_state: Initial state [P, V_p, B, V_b, W]
            n_points: Number of time points
            
        Returns:
            Dictionary with time and state trajectories
        """
        t_eval = np.linspace(t_span[0], t_span[1], n_points)
        
        sol = solve_ivp(
            self.dynamics,
            t_span,
            initial_state,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-6
        )
        
        return {
            'time': sol.t,
            'P': sol.y[0],
            'V_p': sol.y[1],
            'B': sol.y[2],
            'V_b': sol.y[3],
            'W': sol.y[4],
            'success': sol.success,
            'message': sol.message
        }
    
    def __repr__(self) -> str:
        return (f"LimitCycleModel(mu={self.mu:.3f}, omega_0={self.omega_0:.3f}, "
                f"k_B={self.k_B:.3f}, k_P={self.k_P:.3f}, "
                f"lambda_memory={self.lambda_memory:.4f})")
    
    def get_parameters(self) -> Dict:
        """Get model parameters as dictionary."""
        return {
            'mu': self.mu,
            'omega_0': self.omega_0,
            'k_B': self.k_B,
            'k_P': self.k_P,
            'lambda_memory': self.lambda_memory,
            'LC_computed': self.LC_computed,
            'LC_period': self.LC_period,
            'LC_center': self.LC_center.tolist() if self.LC_center is not None else None,
            'LC_radius': self.LC_radius.tolist() if self.LC_radius is not None else None,
        }
