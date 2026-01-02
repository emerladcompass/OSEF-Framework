"""
OSEF: Operational Stability Envelope Framework
Real-Time Implementation Layer for Limit Cycle-Based Aviation Safety Models

Author: Samir Baladi
License: MIT
Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "Samir Baladi"
__email__ = "emeraldcompass@gmail.com"
__license__ = "MIT"

# Core imports
from osef.core.limit_cycle_model import LimitCycleModel
from osef.core.stability_monitor import OSEF
from osef.core.lyapunov import compute_lyapunov_exponent, estimate_lyapunov_fast

# Utilities
from osef.utils.config import load_baladi_params, OSEFConfig

__all__ = [
    # Core classes
    'LimitCycleModel',
    'OSEF',
    
    # Functions
    'compute_lyapunov_exponent',
    'estimate_lyapunov_fast',
    'load_baladi_params',
    'OSEFConfig',
    
    # Metadata
    '__version__',
    '__author__',
]

# Banner
def print_banner():
    """Print OSEF banner with version info"""
    banner = f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🧭 OSEF: Operational Stability Envelope Framework 🧭   ║
    ║                                                           ║
    ║   Real-Time Aviation Safety Supervision                  ║
    ║   Built on Limit Cycle Dynamics Theory                   ║
    ║                                                           ║
    ║   Version: {__version__:<44} ║
    ║   Author:  {__author__:<44} ║
    ║                                                           ║
    ║   Research: https://doi.org/10.17605/OSF.IO/RJBDK        ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
