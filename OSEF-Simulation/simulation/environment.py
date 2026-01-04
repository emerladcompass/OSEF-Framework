import numpy as np

class Environment:
    def __init__(self, wind_std=0.5):
        self.wind_std = wind_std

    def wind_gust(self):
        return np.random.normal(0, self.wind_std)