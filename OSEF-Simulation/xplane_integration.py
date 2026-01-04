from XPlaneConnect import xp
import numpy as np

# Example: connect to X-Plane
client = xp.XPlaneConnect()
state = client.getDREFs([
    "sim/flightmodel/position/indicated_airspeed",
    "sim/flightmodel/position/phi",
    "sim/flightmodel/position/theta"
])
print("Aircraft state from X-Plane:", state)