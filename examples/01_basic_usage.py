"""
Example 1: Basic OSEF Usage
Demonstrates the simplest way to use OSEF
"""

import sys
sys.path.insert(0, '..')  # Add parent directory to path

from osef import LimitCycleModel, OSEF, print_banner
import numpy as np

# Print OSEF banner
print_banner()

print("\n" + "="*60)
print("Example 1: Basic OSEF Usage")
print("="*60 + "\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 1: Create Limit Cycle Model
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Step 1: Loading pre-calibrated Limit Cycle Model...")
lc_model = LimitCycleModel.from_baladi_params(phase="approach")
print(f"✓ Model loaded: {lc_model}")

# Compute limit cycle
print("\nComputing reference limit cycle...")
lc_model.compute_limit_cycle(duration=500, verbose=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 2: Initialize OSEF
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "-"*60)
print("Step 2: Initializing OSEF...")
osef = OSEF(lc_model, window_size=100, sampling_rate=8.0, verbose=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 3: Process some sample data
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "-"*60)
print("Step 3: Processing sample flight data...")
print("-"*60)

# Simulate 10 seconds of flight near limit cycle
for i in range(80):  # 80 samples at 8 Hz = 10 seconds
    t = i / 8.0
    
    # State near limit cycle (small oscillations)
    P = 0.5 * np.sin(2 * np.pi * t / 5.1)
    B = 1.3 * np.sin(2 * np.pi * t / 5.1 - np.pi/4)
    W = 0.8 + 0.02 * np.sin(2 * np.pi * t / 5.1 - np.pi/2)
    
    # Add small noise
    P += np.random.randn() * 0.05
    B += np.random.randn() * 0.1
    W += np.random.randn() * 0.01
    
    # Process through OSEF
    result = osef.process_sample(t, P, B, W)
    
    # Print every second
    if i % 8 == 0:
        print(f"[t={t:5.1f}s] State: {result['state']:20s} "
              f"λ={result['lambda'] if result['lambda'] is not None else 'N/A':>6} d_LC={result['d_LC']:5.2f}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 4: Get Summary Report
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "="*60)
print("Step 4: Summary Report")
print("="*60)

report = osef.get_summary_report()

print(f"\nSummary:")
print(f"  Total samples processed: {report['summary']['total_samples_processed']}")
print(f"  Current state: {report['summary']['current_state']}")

print(f"\nPerformance:")
print(f"  Average latency: {report['performance']['average_latency_ms']:.2f} ms")
print(f"  Max latency: {report['performance']['max_latency_ms']:.2f} ms")
print(f"  Real-time capable: {report['performance']['realtime_capable']}")

print("\n✓ Example completed successfully!\n")
