import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class AircraftAnimator:
    def __init__(self, aircraft):
        self.aircraft = aircraft
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(-50, 50)
        self.line, = self.ax.plot([], [], lw=2)

        self.data = []

    def init(self):
        self.line.set_data([], [])
        return self.line,

    def update(self, frame):
        self.data.append(self.aircraft.pitch)
        if len(self.data) > 100:
            self.data.pop(0)
        self.line.set_data(range(len(self.data)), self.data)
        return self.line,

    def animate(self):
        anim = FuncAnimation(self.fig, self.update, init_func=self.init, blit=True, interval=50)
        plt.show()