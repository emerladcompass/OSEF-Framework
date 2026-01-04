from simulation.aircraft_model import Aircraft
from simulation.pilot_input import PilotInput
from simulation.environment import Environment, LimitCycleDetector
from visualization.animator import AircraftAnimator
from visualization.dashboard import CCDashboard
import time

# تهيئة
aircraft = Aircraft()
pilot = PilotInput()
env = Environment()
detector = LimitCycleDetector()
dashboard = CCDashboard()
animator = AircraftAnimator(aircraft)

# محاكاة بسيطة
for t in range(300):
    # مدخلات الطيار (تجريبية)
    pilot.set_input(elevator=0.1, aileron=0, rudder=0, throttle=0.05)

    # تحديث حالة الطائرة
    gust = env.wind_gust()
    aircraft.update_state(
        elevator=pilot.elevator + gust,
        aileron=pilot.aileron,
        rudder=pilot.rudder,
        throttle=pilot.throttle
    )

    # كشف Limit Cycle
    detector.add_data(aircraft.pitch)
    if detector.check_limit_cycle():
        print(f"⚠️ Limit Cycle Detected at t={t*aircraft.dt:.2f}s")

    # تحديث لوحة CCZ
    dashboard.update(aircraft.pitch)

# تشغيل الرسوم المتحركة
animator.animate()