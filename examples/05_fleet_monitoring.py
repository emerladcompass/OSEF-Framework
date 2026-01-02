"""
Example 5: Fleet Monitoring with OSEF
Aggregate analysis across multiple flights
"""

import sys
sys.path.insert(0, '..')

from osef import LimitCycleModel, OSEF
import numpy as np

print("\n" + "="*70)
print("Example 5: OSEF Fleet Monitoring System")
print("="*70 + "\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Simulate Fleet of Flights
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
n_flights = 5  # Reduced for faster testing
print(f"Simulating {n_flights} flights for fleet analysis...")

# Setup base model
lc_model = LimitCycleModel.from_baladi_params()
lc_model.compute_limit_cycle(verbose=False)

fleet_data = []

for flight_id in range(1, n_flights + 1):
    print(f"  Processing Flight {flight_id:02d}...", end='', flush=True)
    
    # Create fresh OSEF instance for each flight
    osef = OSEF(lc_model, window_size=100, sampling_rate=4.0, verbose=False)
    
    # Generate synthetic flight data
    duration = 60  # 1 minute per flight for faster testing
    sampling_rate = 4.0
    n_samples = int(duration * sampling_rate)
    time_vec = np.linspace(0, duration, n_samples)
    
    # Random parameters for each flight
    np.random.seed(flight_id)  # For reproducibility
    
    P_base = 2.0 + np.random.randn() * 0.5
    B_base = -1.5 + np.random.randn() * 0.5
    W_base = 0.8 + np.random.randn() * 0.1
    
    include_disturbance = np.random.rand() > 0.6  # 40% have disturbances
    
    P = P_base + 0.3 * np.sin(time_vec/8 + np.random.rand())
    B = B_base + 0.2 * np.cos(time_vec/10 + np.random.rand())
    W = np.full_like(time_vec, W_base)
    
    # Add disturbance if needed
    if include_disturbance and duration > 20:
        disturbance_time = duration * 0.3
        disturbance_idx = np.where(time_vec >= disturbance_time)[0][0]
        W[disturbance_idx:] *= 0.6
        P[disturbance_idx:] += np.random.randn() * 1.0
    
    # Process flight
    for i in range(n_samples):
        osef.process_sample(time_vec[i], P[i], B[i], W[i])
    
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
print("="*70)
print("FLEET ANALYSIS SUMMARY")
print("="*70)

# Calculate statistics manually (without pandas)
total_ccz_entries = sum(f['ccz_entries'] for f in fleet_data)
total_alerts = sum(f['alerts'] for f in fleet_data)
flights_with_chaos = sum(1 for f in fleet_data if f['chaos_entries'] > 0)
flights_with_disturbance = sum(1 for f in fleet_data if f['had_disturbance'])

avg_ccz_entries = total_ccz_entries / n_flights
avg_ccz_time = sum(f['ccz_time'] for f in fleet_data) / n_flights
avg_max_lambda = sum(f['max_lambda'] for f in fleet_data) / n_flights
avg_max_deviation = sum(f['max_deviation'] for f in fleet_data) / n_flights
avg_latency = sum(f['avg_latency'] for f in fleet_data) / n_flights

print(f"\n📊 Overall Fleet Statistics ({n_flights} flights):")
print(f"  Total CCZ entries: {total_ccz_entries}")
print(f"  Average CCZ entries per flight: {avg_ccz_entries:.1f}")
print(f"  Average CCZ time per flight: {avg_ccz_time:.1f} seconds")
print(f"  Flights with chaos entries: {flights_with_chaos}")

print(f"\n📈 Performance Metrics:")
print(f"  Average max λ: {avg_max_lambda:.3f}")
print(f"  Average max deviation: {avg_max_deviation:.2f}")
print(f"  Average processing latency: {avg_latency:.2f} ms")
print(f"  Total alerts: {total_alerts}")

# Identify problematic flights
print(f"\n⚠️  Flights Requiring Attention:")
problematic = [f for f in fleet_data if f['ccz_entries'] > 2 or f['chaos_entries'] > 0]

if problematic:
    for flight in problematic:
        print(f"  Flight {flight['flight_id']}: "
              f"{flight['ccz_entries']} CCZ entries, "
              f"{flight['chaos_entries']} chaos entries")
else:
    print("  None - All flights operated normally")

# Top performers (lowest CCZ time)
print(f"\n🏆 Top Performing Flights (lowest CCZ time):")
sorted_flights = sorted(fleet_data, key=lambda x: x['ccz_time'])
for flight in sorted_flights[:3]:  # Top 3
    print(f"  Flight {flight['flight_id']}: {flight['ccz_time']:.1f}s in CCZ")

# Fleet trends
print(f"\n📉 Fleet Trends:")
if flights_with_disturbance > 0:
    disturbance_ccz_time = sum(f['ccz_time'] for f in fleet_data if f['had_disturbance']) / flights_with_disturbance
    normal_ccz_time = sum(f['ccz_time'] for f in fleet_data if not f['had_disturbance']) / (n_flights - flights_with_disturbance)
    
    print(f"  Flights with disturbances: {flights_with_disturbance}")
    print(f"    Average CCZ time: {disturbance_ccz_time:.1f}s")
    print(f"  Normal flights: {n_flights - flights_with_disturbance}")
    print(f"    Average CCZ time: {normal_ccz_time:.1f}s")
    
    if disturbance_ccz_time > normal_ccz_time * 1.5:
        print(f"  ⚠️  Disturbances increase CCZ time significantly")

# Recommendations
print(f"\n💡 Fleet Management Recommendations:")
if avg_ccz_entries > 1.0:
    print(f"  • Moderate CCZ frequency - Monitor operational procedures")
if flights_with_chaos > 0:
    print(f"  • Chaos events detected - Consider crew training refresh")
if avg_max_lambda > 0.2:
    print(f"  • Elevated instability levels - Review aircraft handling")
if avg_latency > 10:
    print(f"  • Higher latency - Optimize monitoring system")

print("\n✅ Fleet analysis completed!\n")
