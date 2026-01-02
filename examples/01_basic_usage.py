#!/usr/bin/env python
"""
01_basic_usage.py - Basic OSEF Usage
Simple working example
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

def safe_format(value, format_str):
    """Safely format a value that might be None"""
    if value is None:
        return "N/A"
    try:
        return format_str.format(value)
    except:
        return str(value)

def main():
    print("🧭 OSEF Framework - Basic Usage Example")
    print("=" * 60)
    
    try:
        # Import OSEF
        import osef
        osef.print_banner()
        
        # Import core components
        from osef.core.limit_cycle_model import LimitCycleModel
        from osef.core.stability_monitor import OSEF
        
        print("\n1. Creating Limit Cycle Model...")
        model = LimitCycleModel.from_baladi_params()
        model.compute_limit_cycle()
        params = model.get_parameters()
        print(f"   ✓ Model created: μ={params['mu']:.3f}, ω₀={params['omega_0']:.3f}")
        
        print("\n2. Initializing OSEF Monitor...")
        monitor = OSEF(model, sampling_rate=8)
        print(f"   ✓ Monitor: {monitor}")
        
        print("\n3. Processing Sample Data...")
        print("   " + "-" * 40)
        
        # Sample flight data
        samples = [
            {"t": 0.0, "P": 0.0, "B": 0.0, "W": 0.8},
            {"t": 1.0, "P": 1.5, "B": -2.3, "W": 0.82},
            {"t": 2.0, "P": 2.1, "B": -3.7, "W": 0.78},
            {"t": 3.0, "P": 1.8, "B": -2.9, "W": 0.81},
        ]
        
        for sample in samples:
            result = monitor.process_sample(**sample)
            
            # Safe extraction
            state = result.get('state', 'Unknown')
            lambda_val = result.get('lambda')
            d_lc_val = result.get('d_LC')
            
            # Safe formatting
            lambda_str = safe_format(lambda_val, "{:6.3f}")
            d_lc_str = safe_format(d_lc_val, "{:5.2f}")
            
            print(f"   t={sample['t']:4.1f}s | State: {state:15} | "
                  f"λ={lambda_str:>6} | d_LC={d_lc_str:>5}")
        
        print("\n" + "=" * 60)
        print("✅ Example Completed Successfully!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
