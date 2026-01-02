"""
Real-time display for OSEF monitoring
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
from typing import Optional
import warnings


class RealtimeDisplay:
    """
    Real-time visualization of OSEF monitoring.
    
    Updates plots as new data arrives, suitable for
    live flight monitoring or simulator integration.
    """
    
    def __init__(self, window_size: int = 500, update_interval: int = 100):
        """
        Initialize real-time display.
        
        Args:
            window_size: Number of points to display
            update_interval: Update interval in milliseconds
        """
        self.window_size = window_size
        self.update_interval = update_interval
        
        # Data buffers
        self.time_buffer = deque(maxlen=window_size)
        self.P_buffer = deque(maxlen=window_size)
        self.B_buffer = deque(maxlen=window_size)
        self.W_buffer = deque(maxlen=window_size)
        self.lambda_buffer = deque(maxlen=window_size)
        self.d_LC_buffer = deque(maxlen=window_size)
        self.state_buffer = deque(maxlen=window_size)
        
        # Setup figure
        self.fig, self.axes = plt.subplots(4, 1, figsize=(12, 10))
        self.fig.suptitle('OSEF Real-Time Monitoring', fontsize=16, fontweight='bold')
        
        # Initialize empty lines
        self.lines = {}
        self._setup_plots()
        
        # Current state display
        self.state_text = self.fig.text(0.02, 0.98, '', fontsize=12,
                                        verticalalignment='top')
    
    def _setup_plots(self):
        """Setup subplot configuration."""
        # Plot 1: P and B
        self.lines['P'], = self.axes[0].plot([], [], 'b-', label='Pitch (P)')
        self.lines['B'], = self.axes[0].plot([], [], 'g-', label='Bank (B)')
        self.axes[0].set_ylabel('Angle (degrees)')
        self.axes[0].legend(loc='upper right')
        self.axes[0].grid(True, alpha=0.3)
        self.axes[0].set_title('Aircraft Attitude')
        
        # Plot 2: W
        self.lines['W'], = self.axes[1].plot([], [], 'orange', label='Power (W)')
        self.axes[1].set_ylabel('Power (normalized)')
        self.axes[1].legend(loc='upper right')
        self.axes[1].grid(True, alpha=0.3)
        self.axes[1].set_title('Power/Memory')
        
        # Plot 3: Lambda
        self.lines['lambda'], = self.axes[2].plot([], [], 'purple', label='λ')
        self.axes[2].axhline(y=0.01, color='green', linestyle=':', alpha=0.5)
        self.axes[2].axhline(y=0.5, color='red', linestyle=':', alpha=0.5)
        self.axes[2].axhspan(0.01, 0.5, alpha=0.1, color='yellow')
        self.axes[2].set_ylabel('λ')
        self.axes[2].legend(loc='upper right')
        self.axes[2].grid(True, alpha=0.3)
        self.axes[2].set_title('Lyapunov Exponent')
        
        # Plot 4: d_LC
        self.lines['d_LC'], = self.axes[3].plot([], [], 'brown', label='d_LC')
        self.axes[3].axhline(y=0.2, color='green', linestyle=':', alpha=0.5)
        self.axes[3].axhline(y=0.8, color='red', linestyle=':', alpha=0.5)
        self.axes[3].axhspan(0.2, 0.8, alpha=0.1, color='yellow')
        self.axes[3].set_xlabel('Time (seconds)')
        self.axes[3].set_ylabel('d_LC')
        self.axes[3].legend(loc='upper right')
        self.axes[3].grid(True, alpha=0.3)
        self.axes[3].set_title('Distance to Limit Cycle')
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    def update(self, osef_result: dict):
        """
        Update display with new OSEF result.
        
        Args:
            osef_result: Result dictionary from OSEF.process_sample()
        """
        # Add to buffers
        self.time_buffer.append(osef_result['timestamp'])
        self.P_buffer.append(osef_result['current_position']['P'])
        self.B_buffer.append(osef_result['current_position']['B'])
        self.W_buffer.append(osef_result['current_position']['W'])
        
        if osef_result['lambda'] is not None:
            self.lambda_buffer.append(osef_result['lambda'])
        if osef_result['d_LC'] is not None:
            self.d_LC_buffer.append(osef_result['d_LC'])
        
        self.state_buffer.append(osef_result['state'])
        
        # Update plots
        time_array = np.array(self.time_buffer)
        
        self.lines['P'].set_data(time_array, np.array(self.P_buffer))
        self.lines['B'].set_data(time_array, np.array(self.B_buffer))
        self.lines['W'].set_data(time_array, np.array(self.W_buffer))
        
        if len(self.lambda_buffer) > 0:
            self.lines['lambda'].set_data(time_array[-len(self.lambda_buffer):],
                                         np.array(self.lambda_buffer))
        
        if len(self.d_LC_buffer) > 0:
            self.lines['d_LC'].set_data(time_array[-len(self.d_LC_buffer):],
                                       np.array(self.d_LC_buffer))
        
        # Update axis limits
        for ax in self.axes:
            ax.relim()
            ax.autoscale_view()
        
        # Update state text
        state = osef_result['state']
        lambda_val = osef_result['lambda'] if osef_result['lambda'] else 0.0
        d_LC_val = osef_result['d_LC'] if osef_result['d_LC'] else 0.0
        
        state_str = f"State: {state}  |  λ: {lambda_val:.3f}  |  d_LC: {d_LC_val:.2f}"
        self.state_text.set_text(state_str)
        
        # Color code by state
        color_map = {
            'Stable_LC': 'green',
            'Creative_Chaos_Zone': 'orange',
            'Chaos': 'red',
            'Converging_to_LC': 'blue',
            'Initializing': 'gray'
        }
        self.state_text.set_color(color_map.get(state, 'black'))
        
        # Refresh
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def show(self):
        """Show the display window."""
        plt.show(block=False)
    
    def close(self):
        """Close the display window."""
        plt.close(self.fig)
