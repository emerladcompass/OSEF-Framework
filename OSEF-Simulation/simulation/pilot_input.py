class PilotInput:
    def __init__(self):
        self.elevator = 0.0
        self.aileron = 0.0
        self.rudder = 0.0
        self.throttle = 0.0

    def set_input(self, elevator=0, aileron=0, rudder=0, throttle=0):
        self.elevator = elevator
        self.aileron = aileron
        self.rudder = rudder
        self.throttle = throttle