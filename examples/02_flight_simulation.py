"""
Example 2: Complete Flight Simulation with OSEF
Simulates a 5-minute flight with engine failure event
"""

import sys
sys.path.insert(0, '..')

from osef import LimitCycleModel, OSEF, print_banner
import numpy as np

# فحص التوفر الاختياري للمكتبات
try:
    from osef.data.synthetic_data import generate_synthetic_flight
    SYNTH_DATA_AVAILABLE = True
except ImportError:
    SYNTH_DATA_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

print_banner()

print("\n" + "="*70)
print("Example 2: Flight Simulation with Disturbance Event")
print("="*70 + "\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Setup
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Initializing system...")

# Create model and OSEF
lc_model = LimitCycleModel.from_baladi_params(phase="approach")
lc_model.compute_limit_cycle(duration=500, verbose=False)
osef = OSEF(lc_model, window_size=100, sampling_rate=8.0, verbose=False)

print("✓ System initialized\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Generate Flight Data
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Generating synthetic flight data...")
print("  Duration: 300 seconds (5 minutes)")
print("  Sampling rate: 8 Hz")
print("  Disturbance: Engine failure at t=100s\n")

# توليد البيانات مع fallback
if SYNTH_DATA_AVAILABLE:
    try:
        flight_data = generate_synthetic_flight(
            duration=300,
            sampling_rate=8.0,
            include_disturbance=True,
            disturbance_time=100.0
        )
        print(f"✓ Generated synthetic data ({len(flight_data)} points)\n")
    except Exception as e:
        print(f"⚠️  Synthetic data generation failed: {e}")
        SYNTH_DATA_AVAILABLE = False
else:
    print("ℹ️  Synthetic data module not available\n")

if not SYNTH_DATA_AVAILABLE:
    print("Creating simple simulation data...")
    # Fallback data
    n_samples = int(300 * 8)
    time = np.linspace(0, 300, n_samples)
    
    # Simple simulation data
    flight_data = {
        'time': time,
        'P': 2.0 + 0.5 * np.sin(time/10),
        'B': -3.0 + 1.0 * np.cos(time/15),
        'W': np.where(time < 100, 0.8, 0.3)
    }
    print(f"✓ Created fallback data ({n_samples} points)\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Process Flight Data
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("Processing flight data through OSEF...")
print("-" * 70)

results = []
alerts_displayed = []

# معالجة أنواع مختلفة من البيانات
if PANDAS_AVAILABLE and hasattr(flight_data, 'iterrows'):
    # pandas DataFrame
    for idx, row in flight_data.iterrows():
        result = osef.process_sample(
            t=row['time'],
            P=row['P'],
            B=row['B'],
            W=row['W']
        )
        results.append(result)
        
        # Display alerts
        if result['alert']:
            alert = result['alert']
            alert_msg = f"[t={row['time']:6.1f}s] {alert['level']:8s}: {alert['message']}"
            print(alert_msg)
            alerts_displayed.append(alert_msg)
else:
    # dict أو numpy arrays
    time_data = flight_data['time']
    if hasattr(time_data, '__len__'):
        n_samples = len(time_data)
    else:
        n_samples = 2400  # افتراضي
    
    for i in range(n_samples):
        try:
            result = osef.process_sample(
                t=flight_data['time'][i],
                P=flight_data['P'][i],
                B=flight_data['B'][i],
                W=flight_data['W'][i]
            )
            results.append(result)
            
            # Display alerts
            if result['alert']:
                alert = result['alert']
                alert_msg = f"[t={flight_data['time'][i]:6.1f}s] {alert['level']:8s}: {alert['message']}"
                print(alert_msg)
                alerts_displayed.append(alert_msg)
        except (IndexError, KeyError):
            break  # انتهاء البيانات

print("-" * 70)
print(f"✓ Processing complete. {len(alerts_displayed)} alerts generated\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Summary Report
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("="*70)
print("FLIGHT SUMMARY REPORT")
print("="*70)

report = osef.get_summary_report()

print("\n📊 Overall Statistics:")
print(f"  Total flight time: {report['summary']['total_time_monitored']:.1f} seconds")
print(f"  Samples processed: {report['summary']['total_samples_processed']}")
print(f"  Final state: {report['summary']['current_state']}")

print("\n🎯 Creative Chaos Zone (CCZ) Analysis:")
print(f"  CCZ entries: {report['ccz_statistics']['total_entries']}")
print(f"  Total CCZ time: {report['ccz_statistics']['total_time_sec']:.1f} seconds")
print(f"  Average CCZ duration: {report['ccz_statistics']['average_duration_sec']:.1f} seconds")
print(f"  Successful LC recoveries: {report['ccz_statistics']['successful_recoveries']}")
print(f"  Average recovery time: {report['ccz_statistics']['average_recovery_time_sec']:.1f} seconds")

print("\n📈 Stability Metrics:")
print(f"  Max λ observed: {report['stability_metrics']['max_lambda_observed']:.3f}")
print(f"  Max deviation observed: {report['stability_metrics']['max_deviation_observed']:.2f}")
print(f"  Chaos entries: {report['stability_metrics']['chaos_entries']}")
print(f"  Current λ: {report['stability_metrics']['current_lambda']:.3f}")
print(f"  Current d_LC: {report['stability_metrics']['current_d_LC']:.2f}")

print("\n⚡ Performance:")
print(f"  Average latency: {report['performance']['average_latency_ms']:.2f} ms")
print(f"  Max latency: {report['performance']['max_latency_ms']:.2f} ms")
print(f"  P99 latency: {report['performance']['p99_latency_ms']:.2f} ms")
print(f"  Real-time capable: {'✓ YES' if report['performance']['realtime_capable'] else '✗ NO'}")

print("\n🚨 Alerts:")
print(f"  Total alerts: {report['alerts']['total_generated']}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Visualization
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n" + "="*70)

if MATPLOTLIB_AVAILABLE and plt is not None:
    print("Generating visualization...")
    
    fig, axes = plt.subplots(4, 1, figsize=(12, 10))
    fig.suptitle('OSEF Flight Analysis', fontsize=16, fontweight='bold')

    time = [r['timestamp'] for r in results if r['timestamp'] is not None]
    lambda_vals = [r['lambda'] for r in results if r['lambda'] is not None]
    d_LC_vals = [r['d_LC'] for r in results if r['d_LC'] is not None]
    
    # الحصول على بيانات الرسم
    if PANDAS_AVAILABLE and hasattr(flight_data, 'iterrows'):
        flight_time = flight_data['time'].values
        flight_P = flight_data['P'].values
        flight_B = flight_data['B'].values
        flight_W = flight_data['W'].values
    else:
        flight_time = flight_data['time']
        flight_P = flight_data['P']
        flight_B = flight_data['B']
        flight_W = flight_data['W']

    # Plot 1: Pitch and Bank
    axes[0].plot(flight_time, flight_P, label='Pitch (P)', color='blue', linewidth=1)
    axes[0].plot(flight_time, flight_B, label='Bank (B)', color='green', linewidth=1)
    axes[0].axvline(x=100, color='red', linestyle='--', alpha=0.5, label='Disturbance')
    axes[0].set_ylabel('Angle (degrees)')
    axes[0].legend(loc='upper right')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_title('Aircraft Attitude')

    # Plot 2: Power
    axes[1].plot(flight_time, flight_W, label='Power (W)', color='orange', linewidth=1)
    axes[1].axvline(x=100, color='red', linestyle='--', alpha=0.5)
    axes[1].set_ylabel('Power (normalized)')
    axes[1].legend(loc='upper right')
    axes[1].grid(True, alpha=0.3)
    axes[1].set_title('Power/Memory State')

    # Plot 3: Lyapunov Exponent
    axes[2].plot(time, lambda_vals, label='λ (Lyapunov)', color='purple', linewidth=1.5)
    axes[2].axhline(y=0.01, color='green', linestyle=':', alpha=0.5, label='Stable LC threshold')
    axes[2].axhline(y=0.5, color='red', linestyle=':', alpha=0.5, label='Chaos threshold')
    axes[2].axhspan(0.01, 0.5, alpha=0.1, color='yellow', label='CCZ range')
    axes[2].set_ylabel('λ')
    axes[2].legend(loc='upper right')
    axes[2].grid(True, alpha=0.3)
    axes[2].set_title('Lyapunov Exponent (Stability Indicator)')

    # Plot 4: Distance to LC
    axes[3].plot(time, d_LC_vals, label='d_LC (Distance to LC)', color='brown', linewidth=1.5)
    axes[3].axhline(y=0.2, color='green', linestyle=':', alpha=0.5)
    axes[3].axhline(y=0.8, color='red', linestyle=':', alpha=0.5)
    axes[3].axhspan(0.2, 0.8, alpha=0.1, color='yellow')
    axes[3].set_xlabel('Time (seconds)')
    axes[3].set_ylabel('d_LC')
    axes[3].legend(loc='upper right')
    axes[3].grid(True, alpha=0.3)
    axes[3].set_title('Deviation from Limit Cycle')

    plt.tight_layout()
    plt.savefig('flight_simulation_results.png', dpi=150)
    print("✓ Visualization saved: flight_simulation_results.png")

    plt.show()
else:
    print("📊 Skipping visualization (matplotlib not available)")
    print("   Data available for analysis in summary report above.")

print("\n✅ Example completed successfully!\n")
