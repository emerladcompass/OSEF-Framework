## 🎮 **New Wiki Page: Simulation**


# 🎮 OSEF Simulation Framework

Interactive real-time aircraft simulation with Creative Chaos Zone detection and visual dashboard.

---

## 📋 Overview

The OSEF Simulation Framework provides an **interactive flight simulation environment** for:
- Training and demonstration of CCZ detection
- Real-time visualization of flight dynamics
- Testing OSEF algorithms in controlled scenarios
- Educational understanding of limit cycle dynamics

---

## ⚙️ Features

### Aircraft Simulation
- **State variables**: Velocity, pitch, roll, yaw, rotational rates
- **Flight dynamics**: Physics-based aircraft model
- **Control inputs**: Keyboard and joystick support
- **Environmental effects**: Wind, turbulence, gusts

### Real-Time Monitoring
- **CCZ detection**: Live Creative Chaos Zone alerts
- **Limit cycle tracking**: Visual stability indicators
- **Performance metrics**: Real-time latency monitoring
- **Advisory alerts**: Cockpit-style warnings

### Visualization
- **Animated plots**: Pitch, roll, velocity over time
- **Interactive dashboard**: Cockpit-style advisory panel
- **Phase space plots**: 3D trajectory visualization
- **Alert indicators**: Visual and textual warnings

---

## 🚀 Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/emerladcompass/OSEF-Framework.git
cd OSEF-Framework/OSEF-Simulation

# Install dependencies
pip install -r requirements.txt
Dependencies
numpy>=1.20.0
matplotlib>=3.4.0
pygame>=2.1.0  # For joystick support
scipy>=1.7.0
Run Simulation
python main.py
🎮 Controls
Keyboard Controls
Key
Action
↑
Increase pitch (nose up)
↓
Decrease pitch (nose down)
←
Roll left
→
Roll right
W
Increase throttle
S
Decrease throttle
A
Yaw left
D
Yaw right
Space
Reset to level flight
ESC
Exit simulation
Joystick Controls
Left stick: Pitch and roll
Right stick: Yaw
Triggers: Throttle
Button A: Reset
Button B: Pause
📊 Dashboard Elements
Main Display
┌─────────────────────────────────────┐
│  OSEF Advisory Dashboard            │
├─────────────────────────────────────┤
│  Velocity:  245 kts                 │
│  Pitch:     +5.2°                   │
│  Roll:      -12.3°                  │
│  Yaw:       180.5°                  │
├─────────────────────────────────────┤
│  Status: ⚠️ CCZ DETECTED            │
│  Confidence: 87%                    │
│  Recommended: Reduce bank angle     │
└─────────────────────────────────────┘
--+
Alert Levels
Status
Color
Description
Normal
🟢 Green
Stable flight, no issues
Monitoring
🟡 Yellow
Approaching limits
CCZ Detected
🟠 Orange
Creative Chaos Zone active
Critical
🔴 Red
Immediate action required
---

📂 Project Structure
```
```
OSEF-Simulation/
│
├── README.md
├── requirements.txt
│
├── simulation/              # Aircraft simulation modules
│   ├── __init__.py
│   ├── aircraft_model.py    # Aircraft state + dynamics
│   ├── pilot_input.py       # Pilot inputs (Keyboard/Joystick)
│   ├── environment.py       # Environmental disturbances
│   └── limit_cycle.py       # CCZ & Limit Cycle detection
│
├── visualization/           # Visualization & Dashboard
│   ├── __init__.py
│   ├── dashboard.py         # Advisory cockpit dashboard
│   └── animator.py          # Animated plots
│
├── main.py                  # Entry point
└── pictures/                # Screenshots
🖼️ Screenshots
```

Pitch & Roll Animation
Real-time visualization of aircraft attitude changes with CCZ detection overlay.
Velocity & CCZ Alerts
Speed monitoring with automatic Creative Chaos Zone detection and warnings.
Advisory Dashboard
Interactive cockpit-style panel showing all flight parameters and stability status.
Note: Screenshots available in pictures/ folder in GitHub repository.
🧪 Example Scenarios
Scenario 1: Normal Flight
# Stable cruise flight
# Expected: Green status, no alerts
Scenario 2: Aggressive Maneuvering
# Rapid pitch/roll changes
# Expected: Yellow/Orange alerts, CCZ detection
Scenario 3: Environmental Disturbance
# Heavy turbulence and wind gusts
# Expected: Stability warnings, recovery guidance
Scenario 4: Engine Failure
# Simulate single engine failure
# Expected: CCZ detection, recovery recommendations
🔧 Configuration
Simulation Parameters
Edit config.py to adjust:
# Aircraft characteristics
AIRCRAFT_MASS = 75000  # kg
WING_AREA = 122.6      # m²
MAX_THRUST = 120000    # N

# Simulation settings
TIME_STEP = 0.01       # seconds
UPDATE_RATE = 100      # Hz

# CCZ detection
CCZ_THRESHOLD = 0.75
DETECTION_WINDOW = 10  # seconds
Visual Settings
# Display
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Plot colors
COLOR_NORMAL = 'green'
COLOR_CCZ = 'orange'
COLOR_CRITICAL = 'red'
📈 Performance
Metric
Value
Update Rate
100 Hz
CCZ Detection
<8ms latency
Frame Rate
60 FPS
Memory Usage
~200 MB
🎓 Educational Use
Training Applications
Pilot training: CCZ awareness and recovery
Instructor tools: Demonstrate stability concepts
Academic: Teach nonlinear dynamics
Research: Algorithm development and testing
Learning Objectives
Understand limit cycle behavior in flight
Recognize Creative Chaos Zone indicators
Practice recovery techniques
Evaluate OSEF detection accuracy
🐛 Troubleshooting
Issue: Low frame rate
Solution: Reduce UPDATE_RATE or disable some visualizations
Issue: Joystick not detected
Solution: Check pygame joystick configuration, ensure drivers installed
Issue: CCZ not detecting
Solution: Verify CCZ_THRESHOLD and DETECTION_WINDOW parameters
🤝 Contributing
Simulation improvements welcome:
New aircraft models
Additional environmental effects
Enhanced visualizations
VR/AR integration
Multiplayer scenarios
📚 Related Documentation
Installation Guide
Quick Start
API Reference
Research Paper
📜 License
MIT License - See LICENSE
Last Updated: January 4, 2026
Version: 0.1.2
Platform: Cross-platform (Windows, macOS, Linux)
← Home | Quick Start →
---