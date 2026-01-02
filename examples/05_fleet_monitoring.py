"""
Example 5: Fleet Monitoring with OSEF
Aggregate analysis across multiple flights
"""

import sys
import os

# تصحيح المسار لضمان عمل الاستيراد حتى لو تم تشغيل الملف من داخل مجلد examples
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from osef import LimitCycleModel, OSEF
from osef.data.synthetic_data import generate_synthetic_flight
import pandas as pd
import numpy as np

print("\n" + "="*70)
print("Example 5: OSEF Fleet Monitoring System")
print("="*70 + "\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Simulate Fleet of Flights
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
n_flights = 10
print(f"Simulating {n_flights} flights for fleet analysis...")

# Setup OSEF
lc_model = LimitCycleModel.from_baladi_params()
lc_model.compute_limit_cycle(verbose=False)

fleet_data = []

for flight_id in range(1, n_flights + 1):
    print(f"  Processing Flight {flight_id:02d}...", end='', flush=True)
    
    # Generate flight
    include_disturbance = np.random.rand() > 0.6  # 40% have disturbances
    flight_df = generate_synthetic_flight(
        duration=300,
        include_disturbance=include_disturbance
    )
    
    # Create fresh OSEF instance for each flight
    osef = OSEF(lc_model, window_size=100, sampling_rate=8.0, verbose=False)
    
    # Process
    for _, row in flight_df.iterrows():
        osef.process_sample(row['time'], row['P'], row['B'], row['W'])
    
    # Get report
    report = osef.get_summary_report()
    
    fleet_data.append({
        'flight_id': flight_id,
        'ccz_entries': report['ccz_statistics']['total_entries'],
        'ccz_time': report['ccz_statistics']['total_time_sec'],
        'max_lambda': report['stability_metrics']['max_lambda_observed'],
        'max_deviation': report['stability_metrics']['max_deviation_observed'],
        'chaos_entries': report['stability_metrics']['chaos_entries'],
        'alerts': report['alerts']['total_generated'],
        'avg_latency': report['performance']['average_latency_ms'],
        'had_disturbance': include_disturbance
    })
    
    print(" ✓")

print()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Fleet Analysis
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
df = pd.DataFrame(fleet_data)

print("="*70)
print("FLEET ANALYSIS SUMMARY")
print("="*70)

print(f"\n📊 Overall Fleet Statistics ({n_flights} flights):")
print(f"  Total CCZ entries: {df['ccz_entries'].sum()}")
print(f"  Average CCZ entries per flight: {df['ccz_entries'].mean():.1f}")
print(f"  Average CCZ time per flight: {df['ccz_time'].mean():.1f} seconds")
print(f"  Flights with chaos entries: {(df['chaos_entries'] > 0).sum()}")

print(f"\n📈 Performance Metrics:")
print(f"  Average max λ: {df['max_lambda'].mean():.3f}")
print(f"  Average max deviation: {df['max_deviation'].mean():.2f}")
print(f"  Average processing latency: {df['avg_latency'].mean():.2f} ms")

# Identify problematic flights
print(f"\n⚠️  Flights Requiring Attention:")
problematic = df[(df['ccz_entries'] > 2) | (df['chaos_entries'] > 0)]

if len(problematic) > 0:
    for _, flight in problematic.iterrows():
        print(f"  Flight {int(flight['flight_id'])}: "
              f"{flight['ccz_entries']} CCZ entries, "
              f"{flight['chaos_entries']} chaos entries")
else:
    print("  None - All flights operated normally")

# Top performers
print(f"\n🏆 Top Performing Flights (lowest CCZ time):")
top_flights = df.nsmallest(3, 'ccz_time')
for _, flight in top_flights.iterrows():
    print(f"  Flight {int(flight['flight_id'])}: {flight['ccz_time']:.1f}s in CCZ")

# Fleet trends
print(f"\n📉 Fleet Trends:")
disturbance_flights = df[df['had_disturbance'] == True]
normal_flights = df[df['had_disturbance'] == False]

if len(disturbance_flights) > 0 and len(normal_flights) > 0:
    print(f"  Flights with disturbances: {len(disturbance_flights)}")
    print(f"    Average CCZ time: {disturbance_flights['ccz_time'].mean():.1f}s")
    print(f"  Normal flights: {len(normal_flights)}")
    print(f"    Average CCZ time: {normal_flights['ccz_time'].mean():.1f}s")
    
    if disturbance_flights['ccz_time'].mean() > normal_flights['ccz_time'].mean() * 2:
        print(f"  ⚠️  Disturbances significantly increase CCZ time")

# Recommendations
print(f"\n💡 Fleet Management Recommendations:")
if df['ccz_entries'].mean() > 1.5:
    print(f"  • High CCZ frequency detected - Review operational procedures")
if (df['chaos_entries'] > 0).sum() > 0:
    print(f"  • Chaos events detected - Consider additional crew training")
if df['max_lambda'].mean() > 0.3:
    print(f"  • Elevated instability levels - Monitor crew workload")
if df['alerts'].mean() > 5:
    print(f"  • High alert frequency - Review alert thresholds")

print("\n✅ Fleet analysis completed!\n")
