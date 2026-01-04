import matplotlib.pyplot as plt

class CCDashboard:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("CCZ / Limit Cycle Dashboard")
        self.ax.set_ylim(0, 10)
        self.data = []

    def update(self, value):
        self.data.append(value)
        if len(self.data) > 50:
            self.data.pop(0)
        self.ax.clear()
        self.ax.plot(self.data, color='red')
        self.ax.set_title("CCZ / Limit Cycle Dashboard")
        plt.pause(0.01)