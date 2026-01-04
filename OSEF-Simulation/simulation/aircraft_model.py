import numpy as np

class Aircraft:
    def __init__(self, dt=0.01):
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        self.velocity = 100.0
        self.altitude = 1000.0
        self.dt = dt

    def update_state(self, elevator=0, aileron=0, rudder=0, throttle=0):
        self.pitch += elevator * self.dt
        self.roll += aileron * self.dt
        self.yaw += rudder * self.dt
        self.velocity += throttle * self.dt
        self.altitude += self.velocity * np.sin(np.radians(self.pitch)) * self.dt