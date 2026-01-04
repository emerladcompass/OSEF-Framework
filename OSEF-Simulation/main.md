from simulation.aircraft_model import Aircraft
from simulation.pilot_input import PilotInput
from simulation.environment import Environment, LimitCycleDetector
from visualization.animator import AircraftAnimator
from visualization.dashboard import CCDashboard

aircraft = Aircraft()
pilot = PilotInput()
env = Environment()
detector = LimitCycleDetector()
dashboard = CCDashboard()
animator = AircraftAnimator(aircraft)

for t in range(300):
    pilot.set_input(elevator=0.1, aileron=0, rudder=0, throttle=0.05)
    gust = env.wind_gust()
    aircraft.update_state(
        elevator=pilot.elevator + gust,
        aileron=pilot.aileron,
        rudder=pilot.rudder,
        throttle=pilot.throttle
    )

    detector.add_data(aircraft.pitch)
    if detector.check_limit_cycle():
        print(f"⚠️ Limit Cycle Detected at t={t*aircraft.dt:.2f}s")

    dashboard.update(aircraft.pitch)

animator.animate()