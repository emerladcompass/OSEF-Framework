# 🏗️ OSEF Architecture

Complete system architecture and design philosophy.

---

## Overview

OSEF (Operational Stability Envelope Framework) is a real-time implementation layer for limit cycle–based flight dynamics models.

┌─────────────────────────────────────────────────────────┐
│                    OSEF Architecture                    │
└─────────────────────────────────────────────────────────┘
┌──────────────┐
│  Flight Data │ (FDR @ 8 Hz)
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Data Acquisition                              │
│  • FDR Reader & Buffer Management                       │
│  • Preprocessing (non-linear filtering, gap filling)   │
│  • State extraction: [P, B, W]                          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 2: Limit Cycle Model                              │
│  • Van der Pol dynamics (coupled 3D space)              │
│  • Pre-calibrated parameters (Baladi et al., 2026)      │
│  • Reference LC trajectory & KD-Tree indexing           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 3: Real-Time Stability Assessment (OSEF Core)    │
│  • Lyapunov exponent (λ) – fast estimation              │
│  • Distance to LC (d_LC)                                │
│  • State classification via FSM                         │
│  • Creative Chaos Zone (CCZ) detection                  │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 4: Guidance System                                │
│  • Trajectory corrections & gain scheduling             │
│  • Context-aware alert generation                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 5: Output & Logging                               │
│  • Real-time telemetry & metric tracking                │
│  • Structured logging (JSON / CSV)                      │
│  • Post-flight reports                                  │
└─────────────────────────────────────────────────────────┘

---

## Core Components

### 1. Limit Cycle Model

**File:** `osef/core/limit_cycle_model.py`

**Purpose:** Implements Van der Pol oscillator dynamics to define the operational normal envelope in a coupled 3D state space.

**Key Features:**
- Pre-calibrated parameters from Baladi et al. (2026)
- Offline reference limit cycle computation
- Efficient closest-point search using KD-Tree indexing

**Equations:**

d²P/dt² = μ(1 − P²)·dP/dt − ω₀²·P + k_B·B  
d²B/dt² = μ(1 − B²)·dB/dt − ω₀²·B + k_P·P  
dW/dt   = −λ·W + η(P, B)

---

### 2. OSEF Stability Monitor

**File:** `osef/core/stability_monitor.py`

**Purpose:** Real-time supervision and stability state classification.

**Processing Pipeline:**
1. Sliding buffer management (100 samples @ 8 Hz)
2. Fast Lyapunov exponent estimation
3. Distance-to-limit-cycle computation
4. Finite State Machine (FSM) classification
5. Context-aware alert generation

**State Logic:**

| State        | Metric Thresholds                         | Risk Level |
|-------------|-------------------------------------------|------------|
| Stable_LC   | λ < 0.01 and d_LC < 0.2                   | 🟢 Low     |
| Converging  | λ < 0.01 and d_LC ≥ 0.2                   | 🟡 Medium  |
| CCZ         | 0.01 ≤ λ < 0.5                            | 🟠 High    |
| Chaos       | λ ≥ 0.5                                  | 🔴 Critical|

---

### 3. Lyapunov Analysis

**File:** `osef/core/lyapunov.py`

**Purpose:** Quantitative stability assessment via exponential divergence analysis.

**Methods:**
- `compute_lyapunov_exponent()` — full Rosenstein algorithm
- `estimate_lyapunov_fast()` — real-time approximation

**Performance:**
- Full computation: ~100 ms (post-flight)
- Fast estimation: ~2 ms (real-time)

---

### 4. Guidance System

**File:** `osef/core/guidance.py`

**Purpose:** Generate corrective guidance toward stable limit cycle trajectories.

**Guidance Gains:**

| State       | Gain | Urgency  |
|------------|------|----------|
| Stable_LC  | 0.0  | None     |
| Converging | 0.7  | Medium   |
| CCZ        | 0.5  | Moderate |
| Chaos      | 1.0  | High     |

---

## Data Flow & Results

### Execution Loop

```python
# Real-time processing (125 ms cadence)

t = current_time()
P, B, W = read_fdr_data()

result = osef.process_sample(t, P, B, W)

# Result structure
{
    "state": "CCZ",
    "lyapunov": 0.021,
    "distance_to_lc": 0.34,
    "guidance": {
        "gain": 0.5,
        "vector": [0.1, -0.2, 0.0]
    },
    "alert_level": "MODERATE"
}


---

Design Philosophy

Physics-Informed: Stability emerges from non-linear dynamical systems theory.

Robustness: High-frequency noise is filtered to prevent false CCZ triggering.

Explainability: Every alert is traceable to measurable quantities.

Ethically Aligned: OSEF does not override the pilot; it stabilizes the decision environment.

Computational Efficiency: Core loops execute in under 8 ms, ensuring deterministic performance.



---

Project Structure

osef/
├── core/         # Limit cycle, Lyapunov, stability engine
├── data/         # FDR processing & synthetic generation
├── guidance/     # Recovery and gain algorithms
└── utils/        # Logging and performance metrics


---

Reliability & Compliance

Fail-Safe: System reverts to Initializing if data gaps exceed 500 ms.

Compliance-Oriented: Architecture designed for deterministic execution aligned with DO-178C principles.



---

🧭 “Stability is not the absence of movement, but the mastery of oscillation.” 🧭
