"""
Example 4: OSEF Training Mode
Real-time feedback for pilot training in simulator
"""

import sys
sys.path.insert(0, '..')

from osef import LimitCycleModel, OSEF, print_banner
from osef.data.synthetic_data import generate_ccz_scenario
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

# Generate scenario
scenario_data = generate_ccz_scenario('engine_failure')

print("Scenario loaded. Processing...")
print("=" * 70)

# Training feedback
feedback_log = []

for idx, row in scenario_data.iterrows():
    result = osef.process_sample(
        t=row['time'],
        P=row['P'],
        B=row['B'],
        W=row['W']
    )
    
    # Real-time training feedback
    if result['alert']:
        feedback = {
            'time': row['time'],
            'alert': result['alert'],
            'guidance': result['guidance'],
            'state': result['state']
        }
        feedback_log.append(feedback)
        
        print(f"\n⚠️  TRAINING FEEDBACK [t={row['time']:.1f}s]")
        print(f"   Alert: {result['alert']['message']}")
        
        if result['guidance']:
            print(f"   Guidance: {result['guidance']['recommended_action']}")
            print(f"   Corrections needed:")
            print(f"     Pitch (P): {result['guidance']['components']['P']:+.2f}°")
            print(f"     Bank (B): {result['guidance']['components']['B']:+.2f}°")
            print(f"     Power (W): {result['guidance']['components']['W']:+.3f}")
    
    # Slow down for visualization (optional)
    # time.sleep(0.01)

print("\n" + "=" * 70)
print("TRAINING SESSION SUMMARY")
print("=" * 70)

report = osef.get_summary_report()

print(f"\n📊 Performance Metrics:")
print(f"  CCZ entries: {report['ccz_statistics']['total_entries']}")
print(f"  Time in CCZ: {report['ccz_statistics']['total_time_sec']:.1f}s")
print(f"  Recovery time: {report['ccz_statistics']['average_recovery_time_sec']:.1f}s")
print(f"  Alerts received: {report['alerts']['total_generated']}")

# Scoring
score = 100
if report['ccz_statistics']['total_time_sec'] > 60:
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
