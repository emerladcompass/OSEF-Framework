"""
Example 4: OSEF Training Mode
Real-time feedback for pilot training in simulator
"""

import sys
sys.path.insert(0, '..')

from osef import LimitCycleModel, OSEF, print_banner
import numpy as np
import time

print_banner()

print("\n" + "="*70)
print("Example 4: OSEF Training Mode for Simulator")
print("="*70 + "\n")

print("🎓 Training Scenario: Engine Failure During Takeoff")
print("   Objective: Navigate through CCZ and restore stable LC")
print()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Setup
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
lc_model = LimitCycleModel.from_baladi_params(phase="approach")
lc_model.compute_limit_cycle(verbose=False)

osef = OSEF(lc_model, window_size=100, sampling_rate=8.0, verbose=False)

# Generate training scenario data
print("Generating training scenario...")
duration = 120  # 2 minutes
sampling_rate = 8.0
n_samples = int(duration * sampling_rate)
time_vec = np.linspace(0, duration, n_samples)

# Create scenario: engine failure at 30 seconds
failure_time = 30
failure_idx = np.where(time_vec >= failure_time)[0][0]

P = 2.0 + 0.3 * np.sin(time_vec/10)
B = -1.5 + 0.2 * np.cos(time_vec/12)
W = np.full_like(time_vec, 0.85)

# Add engine failure
W[failure_idx:] = 0.4 + 0.1 * np.sin(time_vec[failure_idx:]/8)
P[failure_idx:] += 3.0 * np.exp(-(time_vec[failure_idx:] - failure_time)/20)
B[failure_idx:] -= 4.0 * np.exp(-(time_vec[failure_idx:] - failure_time)/25)

print("Scenario loaded. Processing...")
print("=" * 70)

# Training feedback
feedback_log = []
feedback_count = 0

for i in range(n_samples):
    result = osef.process_sample(
        t=time_vec[i],
        P=P[i],
        B=B[i],
        W=W[i]
    )
    
    # Real-time training feedback (show only some to avoid spam)
    if result['alert'] and feedback_count < 5:
        feedback = {
            'time': time_vec[i],
            'alert': result['alert'],
            'state': result['state']
        }
        feedback_log.append(feedback)
        feedback_count += 1
        
        print(f"\n⚠️  TRAINING FEEDBACK [t={time_vec[i]:.1f}s]")
        print(f"   Alert: {result['alert']['message']}")
        print(f"   State: {result['state']}")
        
        # Simulate guidance feedback
        if result['state'] == 'Creative_Chaos_Zone':
            print(f"   Guidance: Reduce workload, focus on basic aircraft control")
        elif result['state'] == 'Converging_to_LC':
            print(f"   Guidance: Maintain current control inputs")
        elif result['d_LC'] and result['d_LC'] > 1.0:
            print(f"   Guidance: Adjust pitch and bank to reduce deviation")

print("\n" + "=" * 70)
print("TRAINING SESSION SUMMARY")
print("=" * 70)

report = osef.get_summary_report()

print(f"\n📊 Performance Metrics:")
print(f"  Total time: {duration} seconds")
print(f"  CCZ entries: {report['ccz_statistics']['total_entries']}")
print(f"  Time in CCZ: {report['ccz_statistics']['total_time_sec']:.1f}s")
print(f"  Recovery time: {report['ccz_statistics']['average_recovery_time_sec']:.1f}s")
print(f"  Alerts received: {report['alerts']['total_generated']}")

# Scoring
score = 100

if report['ccz_statistics']['total_time_sec'] > 40:
    score -= 10
    print(f"\n  ⚠️  Extended CCZ duration (-10 points)")

if report['stability_metrics']['chaos_entries'] > 0:
    score -= 20
    print(f"  ⚠️  Entered chaos state (-20 points)")

if report['ccz_statistics']['successful_recoveries'] > 0:
    score += 10
    print(f"  ✓ Successful LC recovery (+10 points)")

print(f"\n🏆 Training Score: {score}/100")

if score >= 90:
    print("   Grade: EXCELLENT - Ready for line operations")
elif score >= 75:
    print("   Grade: GOOD - Minor areas for improvement")
elif score >= 60:
    print("   Grade: SATISFACTORY - Additional practice recommended")
else:
    print("   Grade: NEEDS IMPROVEMENT - Repeat training")

print("\n✅ Training session completed!\n")
