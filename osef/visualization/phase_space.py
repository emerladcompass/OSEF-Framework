"""
Phase space visualization tools
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import Optional, Dict
import warnings


def plot_phase_space_3d(trajectory: np.ndarray,
                        lc_reference: Optional[np.ndarray] = None,
                        title: str = "3D Phase Space",
                        labels: tuple = ('P (Pitch)', 'B (Bank)', 'W (Power)'),
                        figsize: tuple = (10, 8),
                        save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot 3D phase space trajectory with optional limit cycle reference.
    
    Args:
        trajectory: N x 3 array of [P, B, W] states
        lc_reference: Reference limit cycle trajectory (optional)
        title: Plot title
        labels: Axis labels (P, B, W)
        figsize: Figure size
        save_path: Path to save figure (optional)
        
    Returns:
        Matplotlib figure
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot trajectory
    ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2],
            'b-', linewidth=1.5, label='Trajectory', alpha=0.7)
    
    # Plot start and end points
    ax.scatter(trajectory[0, 0], trajectory[0, 1], trajectory[0, 2],
               c='green', s=100, marker='o', label='Start', zorder=5)
    ax.scatter(trajectory[-1, 0], trajectory[-1, 1], trajectory[-1, 2],
               c='red', s=100, marker='x', label='End', zorder=5)
    
    # Plot limit cycle reference if provided
    if lc_reference is not None:
        ax.plot(lc_reference[:, 0], lc_reference[:, 1], lc_reference[:, 2],
                'r--', linewidth=2, label='Limit Cycle', alpha=0.5)
    
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])
    ax.set_zlabel(labels[2])
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_limit_cycle_2d(lc_reference: np.ndarray,
                       trajectory: Optional[np.ndarray] = None,
                       projection: str = 'PB',
                       title: Optional[str] = None,
                       figsize: tuple = (8, 8),
                       save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot 2D projection of limit cycle and trajectory.
    
    Args:
        lc_reference: Reference limit cycle (N x 3)
        trajectory: Actual trajectory (optional)
        projection: Which 2D projection - 'PB', 'PW', or 'BW'
        title: Plot title
        figsize: Figure size
        save_path: Path to save figure
        
    Returns:
        Matplotlib figure
    """
    # Determine indices for projection
    proj_map = {
        'PB': (0, 1, 'Pitch (P)', 'Bank (B)'),
        'PW': (0, 2, 'Pitch (P)', 'Power (W)'),
        'BW': (1, 2, 'Bank (B)', 'Power (W)')
    }
    
    if projection not in proj_map:
        raise ValueError(f"Unknown projection: {projection}")
    
    idx1, idx2, label1, label2 = proj_map[projection]
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot limit cycle
    ax.plot(lc_reference[:, idx1], lc_reference[:, idx2],
            'r-', linewidth=2, label='Limit Cycle', alpha=0.7)
    
    # Plot trajectory if provided
    if trajectory is not None:
        ax.plot(trajectory[:, idx1], trajectory[:, idx2],
                'b-', linewidth=1.5, label='Trajectory', alpha=0.7)
        
        # Mark start/end
        ax.scatter(trajectory[0, idx1], trajectory[0, idx2],
                   c='green', s=100, marker='o', label='Start', zorder=5)
        ax.scatter(trajectory[-1, idx1], trajectory[-1, idx2],
                   c='red', s=100, marker='x', label='End', zorder=5)
    
    ax.set_xlabel(label1, fontsize=12)
    ax.set_ylabel(label2, fontsize=12)
    
    if title is None:
        title = f'Limit Cycle - {projection} Projection'
    ax.set_title(title, fontsize=14)
    
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def plot_state_evolution(time: np.ndarray,
                        P: np.ndarray,
                        B: np.ndarray,
                        W: np.ndarray,
                        ccz_segments: Optional[list] = None,
                        title: str = "State Evolution",
                        figsize: tuple = (12, 8),
                        save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot time evolution of P, B, W states with CCZ highlighting.
    
    Args:
        time: Time array
        P: Pitch array
        B: Bank array
        W: Power array
        ccz_segments: List of (start_time, end_time) tuples for CCZ
        title: Plot title
        figsize: Figure size
        save_path: Save path
        
    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)
    
    # Plot P
    axes[0].plot(time, P, 'b-', linewidth=1.5)
    axes[0].set_ylabel('Pitch (P) [degrees]')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_title(title)
    
    # Plot B
    axes[1].plot(time, B, 'g-', linewidth=1.5)
    axes[1].set_ylabel('Bank (B) [degrees]')
    axes[1].grid(True, alpha=0.3)
    
    # Plot W
    axes[2].plot(time, W, 'r-', linewidth=1.5)
    axes[2].set_ylabel('Power (W) [normalized]')
    axes[2].set_xlabel('Time (seconds)')
    axes[2].grid(True, alpha=0.3)
    
    # Highlight CCZ segments
    if ccz_segments:
        for start_t, end_t in ccz_segments:
            for ax in axes:
                ax.axvspan(start_t, end_t, alpha=0.2, color='yellow', label='CCZ')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig
