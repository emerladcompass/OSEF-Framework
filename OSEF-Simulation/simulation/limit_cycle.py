class LimitCycleDetector:
    def __init__(self, threshold=5.0, window=50):
        self.threshold = threshold
        self.window = window
        self.history = []

    def add_data(self, value):
        self.history.append(value)
        if len(self.history) > self.window:
            self.history.pop(0)

    def check_limit_cycle(self):
        if len(self.history) < self.window:
            return False
        return max(self.history) - min(self.history) > self.threshold