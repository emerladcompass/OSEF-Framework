"""
OSEF: Operational Stability Envelope Framework
Real-time stability monitoring and supervision system
"""

import numpy as np
from collections import deque
from typing import Dict, Optional, List
import time
import warnings

from osef.core.limit_cycle_model import LimitCycleModel
from osef.core.lyapunov import estimate_lyapunov_fast, is_in_ccz
from osef.core.guidance import GuidanceSystem


class OSEF:
    """
    Operational Stability Envelope Framework
    
    Real-time supervisor for limit cycle-based flight dynamics.
    Continuously monitors aircraft trajectory, detects Creative Chaos Zones,
    and provides guidance toward stable limit cycle operations.
    
    Based on:
        Baladi, S. et al. (2026). Limit Cycle Flight Dynamics as a Framework
        for Adaptive Aviation Safety Protocols.
        DOI: 10.17605/OSF.IO/RJBDK
    
    Attributes:
        lc_model: Underlying limit cycle model
        current_state: Current system state classification
        current_lambda: Current Lyapunov exponent
        current_d_LC: Current normalized distance to limit cycle
        metrics: Performance and event tracking metrics
    """
    
    # System states
    STATE_STABLE_LC = "Stable_LC"
    STATE_CCZ = "Creative_Chaos_Zone"
    STATE_CHAOS = "Chaos"
    STATE_CONVERGING = "Converging_to_LC"
    STATE_INITIALIZING = "Initializing"
    
    # CCZ thresholds (from Baladi et al., 2026, Section 2.4)
    LAMBDA_MIN = 0.01
    LAMBDA_MAX = 0.5
    DLC_MIN = 0.2
    DLC_MAX = 0.8
    
    def __init__(self,
                 lc_model: LimitCycleModel,
                 window_size: int = 100,
                 sampling_rate: float = 8.0,
                 enable_guidance: bool = True,
                 verbose: bool = False):
        """
        Initialize OSEF monitoring system.
        
        Args:
            lc_model: LimitCycleModel instance with computed limit cycle
            window_size: Number of samples for Lyapunov calculation
            sampling_rate: Data sampling rate in Hz
            enable_guidance: Enable trajectory guidance system
            verbose: Print detailed status messages
        """
        self.lc_model = lc_model
        self.window_size = window_size
        self.sampling_rate = sampling_rate
        self.dt = 1.0 / sampling_rate
        self.verbose = verbose
        
        # Ensure limit cycle is computed
        if not lc_model.LC_computed:
            if self.verbose:
                print("Computing limit cycle for OSEF initialization...")
            lc_model.compute_limit_cycle(verbose=verbose)
        
        # Initialize guidance system
        self.enable_guidance = enable_guidance
        if enable_guidance:
            self.guidance_system = GuidanceSystem()
        else:
            self.guidance_system = None
        
        # Data buffers for real-time processing
        self.state_buffer = deque(maxlen=window_size)
        self.time_buffer = deque(maxlen=window_size)
        
        # Current state tracking
        self.current_state = self.STATE_INITIALIZING
        self.current_lambda = 0.0
        self.current_d_LC = 0.0
        self.current_d_LC_absolute = 0.0
        self.time_in_state = 0.0
        self.state_entry_time = 0.0
        
        # Performance metrics
        self.metrics = {
            'total_samples_processed': 0,
            'ccz_entries': 0,
            'ccz_total_time': 0.0,
            'ccz_episodes': [],
            'lc_recovery_times': [],
            'max_lambda_observed': 0.0,
            'max_deviation_observed': 0.0,
            'chaos_entries': 0,
            'alerts_generated': 0,
            'processing_times': [],
        }
        
        # Alert history (prevent spam)
        self.last_alert_time = 0.0
        self.alert_cooldown = 5.0  # seconds
        
        if self.verbose:
            print(f"✓ OSEF initialized")
            print(f"  Sampling rate: {sampling_rate} Hz")
            print(f"  Window size: {window_size} samples")
            print(f"  Guidance: {'Enabled' if enable_guidance else 'Disabled'}")
    
    def process_sample(self,
                      t: float,
                      P: float,
                      B: float,
                      W: float) -> Dict:
        """
        Process single timestep of flight data.
        
        This is the main real-time processing function called at each
        sampling interval (typically 8 Hz).
        
        Args:
            t: Current time in seconds
            P: Pitch angle in degrees
            B: Bank angle in degrees
            W: Power/memory state (0-1 normalized)
            
        Returns:
            Dictionary containing:
            {
                'state': current system state,
                'lambda': Lyapunov exponent,
                'd_LC': normalized distance to limit cycle,
                'd_LC_absolute': absolute distance,
                'guidance': guidance vector (if enabled),
                'alert': alert message (if any),
                'time_in_state': seconds in current state,
                'latency_ms': processing latency in milliseconds,
                'metrics_snapshot': current metrics
            }
        """
        start_time = time.perf_counter()
        
        # Create state vector
        current_X = np.array([P, B, W])
        
        # Update buffers
        self.state_buffer.append(current_X)
        self.time_buffer.append(t)
        self.metrics['total_samples_processed'] += 1
        
        # Need minimum window for analysis
        if len(self.state_buffer) < self.window_size:
            latency = (time.perf_counter() - start_time) * 1000
            return {
                'state': self.STATE_INITIALIZING,
                'lambda': None,
                'd_LC': None,
                'd_LC_absolute': None,
                'guidance': None,
                'alert': None,
                'time_in_state': 0.0,
                'latency_ms': latency,
                'metrics_snapshot': self._get_metrics_snapshot(),
                'buffer_fill': len(self.state_buffer) / self.window_size
            }
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 1: Compute Lyapunov Exponent
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        try:
            state_array = np.array(self.state_buffer)
            self.current_lambda = estimate_lyapunov_fast(
                state_array,
                window_size=self.window_size
            )
        except Exception as e:
            warnings.warn(f"Lyapunov calculation failed: {e}")
            self.current_lambda = 0.0
        
        # Update max lambda observed
        self.metrics['max_lambda_observed'] = max(
            self.metrics['max_lambda_observed'],
            abs(self.current_lambda)
        )
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 2: Compute Distance to Limit Cycle
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        try:
            LC_nearest, LC_idx = self.lc_model.get_closest_lc_point(current_X)
            
            # Absolute distance
            self.current_d_LC_absolute = np.linalg.norm(current_X - LC_nearest)
            
            # Normalized distance
            LC_radius_norm = np.linalg.norm(self.lc_model.LC_radius)
            self.current_d_LC = self.current_d_LC_absolute / (LC_radius_norm + 1e-6)
            
        except Exception as e:
            warnings.warn(f"Distance calculation failed: {e}")
            self.current_d_LC = 0.0
            self.current_d_LC_absolute = 0.0
            LC_nearest = current_X
        
        # Update max deviation observed
        self.metrics['max_deviation_observed'] = max(
            self.metrics['max_deviation_observed'],
            self.current_d_LC
        )
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 3: State Classification
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        new_state = self._classify_state(
            self.current_lambda,
            self.current_d_LC
        )
        
        # Handle state transitions
        if new_state != self.current_state:
            self._handle_state_transition(
                self.current_state,
                new_state,
                t
            )
            self.current_state = new_state
            self.state_entry_time = t
        
        # Update time in state
        self.time_in_state = t - self.state_entry_time
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 4: Compute Guidance (if enabled)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        guidance = None
        if self.enable_guidance and self.guidance_system:
            try:
                guidance = self.guidance_system.compute_guidance(
                    current_X,
                    LC_nearest,
                    self.current_state,
                    self.current_d_LC
                )
            except Exception as e:
                warnings.warn(f"Guidance computation failed: {e}")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 5: Generate Alert (if needed)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        alert = self._generate_alert(
            self.current_state,
            self.time_in_state,
            self.current_lambda,
            self.current_d_LC,
            t
        )
        
        if alert:
            self.metrics['alerts_generated'] += 1
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # STEP 6: Compute Latency
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        latency = (time.perf_counter() - start_time) * 1000  # ms
        self.metrics['processing_times'].append(latency)
        
        # Keep only last 1000 samples to avoid memory growth
        if len(self.metrics['processing_times']) > 1000:
            self.metrics['processing_times'].pop(0)
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Return Results
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        return {
            'timestamp': t,
            'state': self.current_state,
            'lambda': self.current_lambda,
            'd_LC': self.current_d_LC,
            'd_LC_absolute': self.current_d_LC_absolute,
            'guidance': guidance,
            'alert': alert,
            'time_in_state': self.time_in_state,
            'latency_ms': latency,
            'current_position': {'P': P, 'B': B, 'W': W},
            'lc_nearest': {'P': LC_nearest[0], 'B': LC_nearest[1], 'W': LC_nearest[2]},
            'metrics_snapshot': self._get_metrics_snapshot()
        }
    
    def _classify_state(self, lambda_val: float, d_LC: float) -> str:
        """
        Classify system state based on λ and d_LC.
        
        Classification rules from Baladi et al. (2026):
        - CCZ: 0.01 < λ < 0.5 AND 0.2 < d_LC < 0.8
        - Stable LC: λ < 0.01 AND d_LC < 0.2
        - Chaos: λ > 0.5
        - Converging: Otherwise (transitional states)
        
        Args:
            lambda_val: Lyapunov exponent
            d_LC: Normalized distance to limit cycle
            
        Returns:
            State classification string
        """
        # Check for CCZ
        if is_in_ccz(lambda_val, d_LC, 
                     self.LAMBDA_MIN, self.LAMBDA_MAX,
                     self.DLC_MIN, self.DLC_MAX):
            return self.STATE_CCZ
        
        # Stable limit cycle
        elif lambda_val < self.LAMBDA_MIN and d_LC < self.DLC_MIN:
            return self.STATE_STABLE_LC
        
        # Full chaos
        elif lambda_val > self.LAMBDA_MAX:
            return self.STATE_CHAOS
        
        # Converging or transitional
        else:
            return self.STATE_CONVERGING
    
    def _handle_state_transition(self,
                                 old_state: str,
                                 new_state: str,
                                 t: float):
        """
        Handle state transitions and update metrics.
        
        Args:
            old_state: Previous state
            new_state: New state
            t: Current time
        """
        # Exiting CCZ
        if old_state == self.STATE_CCZ:
            ccz_duration = t - self.state_entry_time
            self.metrics['ccz_total_time'] += ccz_duration
            
            # Record CCZ episode
            self.metrics['ccz_episodes'].append({
                'start_time': self.state_entry_time,
                'end_time': t,
                'duration': ccz_duration,
                'exit_state': new_state
            })
            
            # Successful LC recovery
            if new_state == self.STATE_STABLE_LC:
                self.metrics['lc_recovery_times'].append(ccz_duration)
        
        # Entering CCZ
        if new_state == self.STATE_CCZ:
            self.metrics['ccz_entries'] += 1
        
        # Entering Chaos
        if new_state == self.STATE_CHAOS:
            self.metrics['chaos_entries'] += 1
        
        if self.verbose:
            print(f"[{t:8.1f}s] State transition: {old_state} → {new_state}")
    
    def _generate_alert(self,
                       state: str,
                       time_in_state: float,
                       lambda_val: float,
                       d_LC: float,
                       current_time: float) -> Optional[Dict]:
        """
        Generate alert message if needed.
        
        Args:
            state: Current system state
            time_in_state: Time spent in current state
            lambda_val: Lyapunov exponent
            d_LC: Distance to limit cycle
            current_time: Current time
            
        Returns:
            Alert dictionary or None
        """
        # Check cooldown to prevent alert spam
        if current_time - self.last_alert_time < self.alert_cooldown:
            return None
        
        alert = None
        
        # Stable LC - no alert
        if state == self.STATE_STABLE_LC:
            return None
        
        # Creative Chaos Zone alerts
        elif state == self.STATE_CCZ:
            if time_in_state < 10:
                alert = {
                    'level': 'INFO',
                    'message': 'Entering Creative Chaos Zone - Enhanced workload expected',
                    'code': 'CCZ_ENTRY'
                }
            elif time_in_state > 120:  # 2 minutes
                alert = {
                    'level': 'CAUTION',
                    'message': f'Extended CCZ duration ({time_in_state:.0f}s) - '
                              f'Consider LC recovery actions',
                    'code': 'CCZ_EXTENDED'
                }
        
        # Chaos state
        elif state == self.STATE_CHAOS:
            alert = {
                'level': 'WARNING',
                'message': f'High instability detected (λ={lambda_val:.2f}) - '
                          f'Immediate corrective action recommended',
                'code': 'CHAOS_DETECTED'
            }
        
        # Large deviation
        elif state == self.STATE_CONVERGING:
            if d_LC > 1.5:
                alert = {
                    'level': 'CAUTION',
                    'message': f'Significant deviation from LC (d={d_LC:.2f}) - '
                              f'Monitor trajectory',
                    'code': 'LARGE_DEVIATION'
                }
            elif 0.5 < d_LC <= 1.5:
                alert = {
                    'level': 'INFO',
                    'message': f'Converging to stable LC (d={d_LC:.2f})',
                    'code': 'CONVERGING'
                }
        
        # Update last alert time if alert generated
        if alert:
            self.last_alert_time = current_time
            alert['timestamp'] = current_time
        
        return alert
    
    def _get_metrics_snapshot(self) -> Dict:
        """Get current metrics snapshot."""
        return {
            'total_samples': self.metrics['total_samples_processed'],
            'ccz_entries': self.metrics['ccz_entries'],
            'ccz_total_time': self.metrics['ccz_total_time'],
            'max_lambda': self.metrics['max_lambda_observed'],
            'max_deviation': self.metrics['max_deviation_observed'],
            'chaos_entries': self.metrics['chaos_entries'],
            'alerts_count': self.metrics['alerts_generated'],
        }
    
    def get_summary_report(self) -> Dict:
        """
        Generate comprehensive summary report.
        
        Returns:
            Dictionary with performance metrics and statistics
        """
        # Compute average recovery time
        avg_recovery_time = (
            np.mean(self.metrics['lc_recovery_times'])
            if self.metrics['lc_recovery_times']
            else 0.0
        )
        
        # Compute average processing latency
        avg_latency = (
            np.mean(self.metrics['processing_times'])
            if self.metrics['processing_times']
            else 0.0
        )
        
        max_latency = (
            np.max(self.metrics['processing_times'])
            if self.metrics['processing_times']
            else 0.0
        )
        
        # CCZ statistics
        ccz_durations = [ep['duration'] for ep in self.metrics['ccz_episodes']]
        avg_ccz_duration = np.mean(ccz_durations) if ccz_durations else 0.0
        
        return {
            'summary': {
                'total_samples_processed': self.metrics['total_samples_processed'],
                'total_time_monitored': (
                    self.metrics['total_samples_processed'] * self.dt
                ),
                'current_state': self.current_state,
            },
            'ccz_statistics': {
                'total_entries': self.metrics['ccz_entries'],
                'total_time_sec': self.metrics['ccz_total_time'],
                'average_duration_sec': avg_ccz_duration,
                'successful_recoveries': len(self.metrics['lc_recovery_times']),
                'average_recovery_time_sec': avg_recovery_time,
            },
            'stability_metrics': {
                'max_lambda_observed': self.metrics['max_lambda_observed'],
                'max_deviation_observed': self.metrics['max_deviation_observed'],
                'chaos_entries': self.metrics['chaos_entries'],
                'current_lambda': self.current_lambda,
                'current_d_LC': self.current_d_LC,
            },
            'performance': {
                'average_latency_ms': avg_latency,
                'max_latency_ms': max_latency,
                'p99_latency_ms': (
                    np.percentile(self.metrics['processing_times'], 99)
                    if len(self.metrics['processing_times']) > 100
                    else max_latency
                ),
                'realtime_capable': avg_latency < 10.0,  # < 10ms target
            },
            'alerts': {
                'total_generated': self.metrics['alerts_generated'],
            },
            'model_parameters': self.lc_model.get_parameters(),
        }
    
    def reset_metrics(self):
        """Reset all metrics counters."""
        self.metrics = {
            'total_samples_processed': 0,
            'ccz_entries': 0,
            'ccz_total_time': 0.0,
            'ccz_episodes': [],
            'lc_recovery_times': [],
            'max_lambda_observed': 0.0,
            'max_deviation_observed': 0.0,
            'chaos_entries': 0,
            'alerts_generated': 0,
            'processing_times': [],
        }
        if self.verbose:
            print("✓ Metrics reset")
    
    def export_ccz_episodes(self) -> List[Dict]:
        """
        Export CCZ episodes for analysis.
        
        Returns:
            List of CCZ episode dictionaries
        """
        return self.metrics['ccz_episodes'].copy()
    
    def __repr__(self) -> str:
        return (f"OSEF(state={self.current_state}, "
                f"λ={self.current_lambda:.3f}, "
                f"d_LC={self.current_d_LC:.2f}, "
                f"samples={self.metrics['total_samples_processed']})")
