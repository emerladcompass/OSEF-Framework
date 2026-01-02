# 🚀 Quick Start Guide

Get started with OSEF in 5 minutes!

---

## Installation

### Using pip

```bash
pip install osef
From source
git clone https://github.com/emeraldcompass/OSEF-Framework.git
cd OSEF-Framework
pip install -e .
Basic Usage
1. Import OSEF
from osef import LimitCycleModel, OSEF, print_banner

# Print welcome banner
print_banner()
2. Create Limit Cycle Model
# Load pre-calibrated parameters from Baladi et al. (2026)
lc_model = LimitCycleModel.from_baladi_params(phase="approach")

# Compute reference limit cycle
lc_model.compute_limit_cycle()
Available phases:
"approach" - Approach phase (default)
"cruise" - Cruise phase
"emergency" - Emergency scenarios (e.g., QF32)
3. Initialize OSEF
osef = OSEF(
    lc_model=lc_model,
    window_size=100,      # Samples for Lyapunov calculation
    sampling_rate=8.0,    # Hz
    enable_guidance=True  # Enable trajectory guidance
)
4. Process Flight Data
# Real-time processing (8 Hz)
result = osef.process_sample(
    t=10.5,    # Time in seconds
    P=2.3,     # Pitch angle (degrees)
    B=-5.1,    # Bank angle (degrees)
    W=0.78     # Power (0-1 normalized)
)

# Check result
print(f"State: {result['state']}")
print(f"Lyapunov (λ): {result['lambda']:.3f}")
print(f"Distance to LC: {result['d_LC']:.2f}")

# Get guidance if needed
if result['guidance']:
    print(f"Guidance: {result['guidance']['recommended_action']}")
Complete Example
from osef import LimitCycleModel, OSEF
from osef.data.synthetic_data import generate_synthetic_flight

# Setup
lc_model = LimitCycleModel.from_baladi_params()
lc_model.compute_limit_cycle(verbose=False)
osef = OSEF(lc_model, sampling_rate=8.0)

# Generate test flight
flight_data = generate_synthetic_flight(duration=300)

# Process
for _, row in flight_data.iterrows():
    result = osef.process_sample(
        t=row['time'],
        P=row['P'],
        B=row['B'],
        W=row['W']
    )
    
    # Display alerts
    if result['alert']:
        print(f"[{row['time']:.1f}s] {result['alert']['message']}")

# Get summary
report = osef.get_summary_report()
print(f"CCZ entries: {report['ccz_statistics']['total_entries']}")
print(f"Average latency: {report['performance']['average_latency_ms']:.2f} ms")
Understanding Results
System States
State
Description
λ Range
d_LC Range
Stable_LC
On limit cycle, optimal
< 0.01
< 0.2
Creative_Chaos_Zone
Transitional, adaptive
0.01-0.5
0.2-0.8
Chaos
High instability
> 0.5
Any
Converging_to_LC
Returning to stable
Varies
> 0.8
Key Metrics
λ (Lyapunov exponent): Stability indicator
λ < 0: Stable (converging)
λ ≈ 0: Neutrally stable (limit cycle)
λ > 0: Unstable (diverging)
d_LC: Distance from nominal limit cycle
0 = on limit cycle
< 0.2 = very close
1.0 = significant deviation
Next Steps
📖 Read Architecture Overview
🎓 Try Example Scripts
📊 Explore API Reference
🧪 Run Unit Tests
Troubleshooting
Common Issues
Q: nolds library not found
pip install nolds
Q: Plots not showing
import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg'
Q: Slow performance
Reduce window_size (default 100)
Use estimate_lyapunov_fast() instead of full calculation
Getting Help
📧 Email: emeraldcompass@gmail.com
🐛 Issues: GitHub Issues
📚 Docs: Full Documentation
---
