"""
Stability analysis visualization
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, List, Tuple


def plot_stability_map(lambda_vals: np.ndarray,
                      d_LC_vals: np.ndarray,
                      time: np.ndarray,
                      title: str = "Stability Map",
                      figsize: tuple = (10, 6),
                      save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot stability map showing λ vs d_LC with CCZ boundaries.
    
    Args:
        lambda_vals: Lyapunov exponent values
        d_LC_vals: Distance to LC values
        time: Time array (for color coding)
        title: Plot title
        figsize: Figure size
        save_path: Save path
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # CCZ boundaries
    ax.axhline(y=0.01, color='green', linestyle='--', alpha=0.5, label='Stable LC boundary')
    ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Chaos boundary')
    ax.axvline(x=0.2, color='blue', linestyle='--', alpha=0.5)
    ax.axvline(x=0.8, color='blue', linestyle='--', alpha=0.5)
    
    # CCZ region
    ax.axhspan(0.01, 0.5, 0.2, 0.8, alpha=0.1, color='yellow', label='CCZ')
    
    # Plot trajectory colored by time
    scatter = ax.scatter(d_LC_vals, lambda_vals, c=time, cmap='viridis',
                        s=20, alpha=0.6, edgecolors='none')
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Time (seconds)')
    
    ax.set_xlabel('Distance to Limit Cycle (d_LC)', fontsize=12)
    ax.set_ylabel('Lyapunov Exponent (λ)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # Set reasonable axis limits
    ax.set_xlim(0, max(2.0, d_LC_vals.max() * 1.1))
    ax.set_ylim(-0.1, max(1.0, lambda_vals.max() * 1.1))
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_lyapunov_timeline(time: np.ndarray,
                          lambda_vals: np.ndarray,
                          states: Optional[List[str]] = None,
                          title: str = "Lyapunov Exponent Timeline",
                          figsize: tuple = (12, 6),
                          save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot Lyapunov exponent over time with state annotations.
    
    Args:
        time: Time array
        lambda_vals: Lyapunov exponent values
        states: System state classifications (optional)
        title: Plot title
        figsize: Figure size
        save_path: Save path
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot lambda
    ax.plot(time, lambda_vals, 'b-', linewidth=2, label='λ (Lyapunov)')
    
    # Threshold lines
    ax.axhline(y=0.01, color='green', linestyle=':', alpha=0.5, label='Stable LC threshold')
    ax.axhline(y=0.5, color='red', linestyle=':', alpha=0.5, label='Chaos threshold')
    
    # CCZ region
    ax.axhspan(0.01, 0.5, alpha=0.1, color='yellow', label='CCZ range')
    
    # Color background by state if provided
    if states:
        state_colors = {
            'Stable_LC': 'lightgreen',
            'Creative_Chaos_Zone': 'yellow',
            'Chaos': 'lightcoral',
            'Converging_to_LC': 'lightblue',
            'Initializing': 'lightgray'
        }
        
        current_state = states[0]
        start_idx = 0
        
        for i, state in enumerate(states + ['END']):
            if state != current_state or i == len(states):
                # State transition
                end_idx = i
                color = state_colors.get(current_state, 'white')
                ax.axvspan(time[start_idx], time[end_idx-1] if end_idx > 0 else time[start_idx],
                          alpha=0.2, color=color)
                
                if i < len(states):
                    current_state = state
                    start_idx = i
    
    ax.set_xlabel('Time (seconds)', fontsize=12)
    ax.set_ylabel('λ (Lyapunov Exponent)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_parameter_stability_map(mu_range: Tuple[float, float],
                                 omega_range: Tuple[float, float],
                                 n_points: int = 50,
                                 figsize: tuple = (10, 8),
                                 save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot stability map in parameter space (μ vs ω₀).
    
    Args:
        mu_range: Range for μ parameter
        omega_range: Range for ω₀ parameter
        n_points: Grid resolution
        figsize: Figure size
        save_path: Save path
        
    Returns:
        Matplotlib figure
    """
    from osef import LimitCycleModel
    
    mu_vals = np.linspace(mu_range[0], mu_range[1], n_points)
    omega_vals = np.linspace(omega_range[0], omega_range[1], n_points)
    
    stability_map = np.zeros((n_points, n_points))
    
    print("Computing stability map... (this may take a while)")
    
    for i, mu in enumerate(mu_vals):
        for j, omega in enumerate(omega_vals):
            try:
                # Create model with these parameters
                model = LimitCycleModel(mu=mu, omega_0=omega)
                model.compute_limit_cycle(duration=200, verbose=False)
                
                # Check if stable LC exists
                if model.LC_computed and model.LC_period > 0:
                    stability_map[j, i] = 1  # Stable
                else:
                    stability_map[j, i] = 0  # Unstable
            except:
                stability_map[j, i] = -1  # Failed
    
    # Plot
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.imshow(stability_map, extent=[mu_range[0], mu_range[1],
                                          omega_range[0], omega_range[1]],
                   origin='lower', cmap='RdYlGn', aspect='auto')
    
    # Mark Baladi et al. parameters
    ax.plot(0.47, 1.23, 'b*', markersize=15, label='Approach (Baladi)')
    ax.plot(0.83, 0.41, 'r*', markersize=15, label='Emergency (QF32)')
    
    ax.set_xlabel('μ (Nonlinearity)', fontsize=12)
    ax.set_ylabel('ω₀ (Natural Frequency)', fontsize=12)
    ax.set_title('Parameter Stability Map', fontsize=14)
    ax.legend()
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Stability')
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig
