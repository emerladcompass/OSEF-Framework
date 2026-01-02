"""
Trajectory Guidance System
Provides corrections to guide aircraft back to stable limit cycle
"""

import numpy as np
from typing import Dict, Optional


class GuidanceSystem:
    """
    Computes guidance vectors to restore stable limit cycle operations.
    
    The guidance system provides suggested corrections in P, B, W dimensions
    based on current deviation from the nominal limit cycle.
    """
    
    def __init__(self,
                 gain_stable: float = 0.0,
                 gain_ccz: float = 0.5,
                 gain_chaos: float = 1.0,
                 gain_converging: float = 0.7):
        """
        Initialize guidance system.
        
        Args:
            gain_stable: Guidance gain when in stable LC (typically 0)
            gain_ccz: Guidance gain in Creative Chaos Zone
            gain_chaos: Guidance gain in chaos (max correction)
            gain_converging: Guidance gain when converging to LC
        """
        self.gains = {
            'Stable_LC': gain_stable,
            'Creative_Chaos_Zone': gain_ccz,
            'Chaos': gain_chaos,
            'Converging_to_LC': gain_converging,
        }
    
    def compute_guidance(self,
                        current_state: np.ndarray,
                        lc_nearest: np.ndarray,
                        system_state: str,
                        d_LC: float) -> Dict:
        """
        Compute guidance vector toward limit cycle.
        
        Args:
            current_state: Current [P, B, W] state
            lc_nearest: Nearest point on limit cycle [P, B, W]
            system_state: System state classification
            d_LC: Normalized distance to LC
            
        Returns:
            Dictionary with guidance information:
            {
                'direction': unit vector toward LC,
                'magnitude': suggested correction strength,
                'components': {P, B, W} individual corrections,
                'recommended_action': human-readable action
            }
        """
        # Vector from current to nearest LC point
        direction_raw = lc_nearest - current_state
        distance = np.linalg.norm(direction_raw)
        
        if distance < 1e-6:
            # Already on LC
            return {
                'direction': np.zeros(3),
                'magnitude': 0.0,
                'components': {'P': 0.0, 'B': 0.0, 'W': 0.0},
                'recommended_action': 'Maintain current trajectory'
            }
        
        # Unit direction vector
        direction_unit = direction_raw / distance
        
        # Magnitude based on state and distance
        gain = self.gains.get(system_state, 0.5)
        magnitude = gain * d_LC
        
        # Component corrections
        correction_P = direction_unit[0] * magnitude
        correction_B = direction_unit[1] * magnitude
        correction_W = direction_unit[2] * magnitude
        
        # Generate human-readable recommendation
        action = self._generate_recommendation(
            correction_P, correction_B, correction_W, system_state
        )
        
        return {
            'direction': direction_unit,
            'magnitude': magnitude,
            'components': {
                'P': correction_P,
                'B': correction_B,
                'W': correction_W
            },
            'recommended_action': action
        }
    
    def _generate_recommendation(self,
                                 P_corr: float,
                                 B_corr: float,
                                 W_corr: float,
                                 state: str) -> str:
        """
        Generate human-readable recommendation.
        
        Args:
            P_corr: Pitch correction
            B_corr: Bank correction
            W_corr: Power correction
            state: System state
            
        Returns:
            Recommendation string
        """
        threshold = 0.1
        actions = []
        
        if abs(P_corr) > threshold:
            direction = "increase" if P_corr > 0 else "decrease"
            actions.append(f"{direction} pitch")
        
        if abs(B_corr) > threshold:
            direction = "increase" if B_corr > 0 else "decrease"
            actions.append(f"{direction} bank")
        
        if abs(W_corr) > threshold:
            direction = "increase" if W_corr > 0 else "decrease"
            actions.append(f"{direction} power")
        
        if not actions:
            return "Maintain current trajectory"
        
        action_str = ", ".join(actions)
        
        # Add urgency based on state
        if state == "Chaos":
            return f"URGENT: {action_str}"
        elif state == "Creative_Chaos_Zone":
            return f"Consider: {action_str}"
        else:
            return f"Suggested: {action_str}"
    
    def set_gain(self, state: str, gain: float):
        """
        Update guidance gain for a specific state.
        
        Args:
            state: State name
            gain: New gain value (0.0 to 1.0)
        """
        if state in self.gains:
            self.gains[state] = np.clip(gain, 0.0, 1.0)
        else:
            raise ValueError(f"Unknown state: {state}")
    
    def get_gains(self) -> Dict[str, float]:
        """Get current guidance gains."""
        return self.gains.copy()
