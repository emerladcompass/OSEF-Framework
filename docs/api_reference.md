API Reference - OSEF Framework

📦 Core Modules

osef.core.LimitCycleModel

Constructor

```python
LimitCycleModel(
    mu: float = 1.0,
    epsilon: float = 0.1,
    dt: float = 0.01,
    bounds: Tuple[float, float] = (-3.0, 3.0)
) -> LimitCycleModel
```

Parameters:

· mu: Nonlinearity parameter (default: 1.0)
· epsilon: Damping coefficient (default: 0.1)
· dt: Time step for integration (default: 0.01)
· bounds: Phase space boundaries (default: (-3.0, 3.0))

Methods

compute_limit_cycle()

```python
def compute_limit_cycle(
    self,
    initial_state: Optional[np.ndarray] = None,
    max_iter: int = 10000,
    tol: float = 1e-6
) -> Dict[str, Any]
```

Compute stable limit cycle.

Returns:

```python
{
    'cycle_points': np.ndarray,    # Limit cycle coordinates
    'period': float,               # Cycle period
    'amplitude': float,            # Cycle amplitude
    'converged': bool              # Convergence status
}
```

analyze_trajectory()

```python
def analyze_trajectory(
    self,
    trajectory: np.ndarray,
    window_size: int = 100
) -> Dict[str, Any]
```

Analyze flight trajectory for limit cycle behavior.

Returns:

```python
{
    'limit_cycle_similarity': float,
    'deviation_index': float,
    'phase_offset': float,
    'is_stable': bool
}
```

predict_ccz()

```python
def predict_ccz(
    self,
    current_state: np.ndarray,
    forecast_steps: int = 50
) -> Dict[str, Any]
```

Predict Creative Chaos Zone entry.

Returns:

```python
{
    'ccz_probability': float,
    'time_to_ccz': float,
    'recommended_action': str,
    'confidence': float
}
```

osef.core.StabilityMonitor

Constructor

```python
StabilityMonitor(
    sampling_rate: int = 125,      # Hz
    buffer_size: int = 1000,
    alert_threshold: float = 0.8,
    model: Optional[LimitCycleModel] = None
) -> StabilityMonitor
```

Methods

process_sample()

```python
def process_sample(
    self,
    timestamp: float,
    pitch: float,
    bank: float,
    power: float
) -> Dict[str, Any]
```

Process single flight data sample.

Returns:

```python
{
    'state': str,                  # 'STABLE', 'CCZ', 'UNSTABLE'
    'lambda': float,               # Lyapunov exponent
    'ccz_probability': float,
    'recommendation': str,
    'processing_time_ms': float
}
```

batch_process()

```python
def batch_process(
    self,
    data: np.ndarray,
    parallel: bool = True
) -> Dict[str, Any]
```

Process batch of flight data.

get_statistics()

```python
def get_statistics(self) -> Dict[str, Any]
```

Get monitoring statistics.

Returns:

```python
{
    'samples_processed': int,
    'ccz_detections': int,
    'avg_processing_time': float,
    'alert_rate': float,
    'uptime': float
}
```

reset()

```python
def reset(self, clear_history: bool = True) -> None
```

Reset monitor state.

osef.core.LyapunovAnalyzer

Methods

compute_exponent()

```python
def compute_exponent(
    self,
    trajectory: np.ndarray,
    method: str = 'wolf'
) -> float
```

Compute Lyapunov exponent.

Parameters:

· method: 'wolf', 'rosenstein', 'sano-sawada'

stability_classification()

```python
def stability_classification(
    self,
    lambda_value: float
) -> str
```

Classify stability based on Lyapunov exponent.

Returns: 'STABLE', 'MARGINAL', 'CHAOTIC', 'UNSTABLE'

osef.core.GuidanceSystem

Methods

compute_correction()

```python
def compute_correction(
    self,
    current_state: np.ndarray,
    target_cycle: np.ndarray,
    aircraft_params: Dict[str, float]
) -> Dict[str, float]
```

Compute guidance corrections.

Returns:

```python
{
    'pitch_correction': float,
    'bank_correction': float, 
    'power_correction': float,
    'priority': str           # 'IMMEDIATE', 'ADVISORY', 'MONITOR'
}
```

generate_recovery_path()

```python
def generate_recovery_path(
    self,
    start_state: np.ndarray,
    target_state: np.ndarray,
    constraints: Dict[str, Any]
) -> np.ndarray
```

Generate recovery trajectory.

📊 Data Module

osef.data.FDRReader

Methods

read_flight_data()

```python
def read_flight_data(
    self,
    filepath: str,
    format: str = 'auto'
) -> pd.DataFrame
```

Read Flight Data Recorder data.

Supported formats: 'csv', 'json', 'hdf5', 'arinc'

extract_phase_variables()

```python
def extract_phase_variables(
    self,
    df: pd.DataFrame
) -> np.ndarray
```

Extract phase space variables (Pitch, Bank, Power).

validate_data()

```python
def validate_data(
    self,
    data: np.ndarray,
    checks: List[str] = None
) -> Dict[str, bool]
```

Validate flight data quality.

osef.data.SyntheticDataGenerator

Methods

generate_limit_cycle()

```python
def generate_limit_cycle(
    self,
    duration: float = 600.0,
    noise_level: float = 0.05,
    anomalies: bool = False
) -> np.ndarray
```

Generate synthetic limit cycle data.

inject_anomalies()

```python
def inject_anomalies(
    self,
    data: np.ndarray,
    anomaly_type: str = 'ccz',
    severity: float = 0.5
) -> np.ndarray
```

Inject anomalies into flight data.

📈 Visualization Module

osef.visualization.PhaseSpacePlot

Methods

plot_3d_trajectory()

```python
def plot_3d_trajectory(
    self,
    trajectory: np.ndarray,
    limit_cycle: Optional[np.ndarray] = None,
    show: bool = True
) -> go.Figure
```

Create 3D phase space plot.

plot_stability_map()

```python
def plot_stability_map(
    self,
    monitor: StabilityMonitor,
    resolution: int = 50
) -> go.Figure
```

Create stability region visualization.

osef.visualization.RealTimeDisplay

Methods

update_display()

```python
def update_display(
    self,
    data: Dict[str, Any],
    refresh_rate: float = 10.0
) -> None
```

Update real-time display.

create_dashboard()

```python
def create_dashboard(
    self,
    layout: str = 'standard'
) -> dash.Dash
```

Create web dashboard.

⚙️ Configuration

osef.utils.Config

Methods

load_config()

```python
@classmethod
def load_config(
    cls,
    config_path: str = None,
    env_prefix: str = 'OSEF_'
) -> Config
```

Load configuration from file and environment.

get()

```python
def get(
    self,
    key: str,
    default: Any = None
) -> Any
```

Get configuration value.

Configuration Structure

```yaml
core:
  sampling_rate: 125
  buffer_size: 1000
  alert_threshold: 0.8
  
model:
  mu: 1.0
  epsilon: 0.1
  dt: 0.01
  
visualization:
  enabled: true
  port: 8050
  update_rate: 10.0
  
logging:
  level: INFO
  file: osef.log
  
performance:
  max_workers: 4
  cache_size: 10000
```

🔌 Plugin System

Creating Custom Models

```python
from osef.core import BaseModel

class CustomModel(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def analyze(self, data: np.ndarray) -> Dict[str, Any]:
        # Custom analysis logic
        return {
            'stability': self._compute_stability(data),
            'features': self._extract_features(data)
        }
    
    def _compute_stability(self, data: np.ndarray) -> float:
        # Implementation
        pass
```

Plugin Registration

```python
from osef.plugins import register_model

@register_model(name='custom_model', version='1.0.0')
class CustomModel(BaseModel):
    # Implementation
    pass
```

📡 Web API

REST Endpoints

GET /api/health

```json
{
  "status": "healthy",
  "version": "0.2.2",
  "uptime": 3600.5
}
```

POST /api/analyze

```json
{
  "timestamp": 1672531200.0,
  "pitch": 2.5,
  "bank": -1.2,
  "power": 0.85
}
```

Response:

```json
{
  "state": "STABLE",
  "lambda": -0.15,
  "ccz_probability": 0.12,
  "recommendation": "Continue current trajectory",
  "processing_time_ms": 0.8
}
```

POST /api/batch_analyze

```json
{
  "data": [
    [1672531200.0, 2.5, -1.2, 0.85],
    [1672531201.0, 2.6, -1.1, 0.86]
  ]
}
```

GET /api/statistics

```json
{
  "samples_processed": 12500,
  "ccz_detections": 24,
  "avg_processing_time_ms": 0.75,
  "system_load": 0.42
}
```

WebSocket API

```python
import websockets
import json

async def connect_to_osef():
    async with websockets.connect('ws://localhost:8080/ws') as websocket:
        # Send flight data
        await websocket.send(json.dumps({
            'pitch': 2.5,
            'bank': -1.2,
            'power': 0.85
        }))
        
        # Receive real-time analysis
        response = await websocket.recv()
        analysis = json.loads(response)
```

🧪 Testing Interface

osef.testing.Benchmark

```python
benchmark = Benchmark(
    iterations: int = 1000,
    warmup: int = 100
)

results = benchmark.run(
    model=LimitCycleModel(),
    test_data=synthetic_data
)
```

Performance Metrics

```python
{
  'throughput_samples_per_second': 1250.5,
  'latency_p99_ms': 1.2,
  'memory_usage_mb': 142.3,
  'accuracy_ccz_detection': 0.912
}
```

🔐 Security API

Authentication

```python
from osef.auth import authenticate

token = authenticate(
    api_key: str,
    permissions: List[str] = ['read', 'write']
)

# Use in requests
headers = {'Authorization': f'Bearer {token}'}
```

Rate Limiting

```python
from osef.auth import RateLimiter

limiter = RateLimiter(
    requests_per_minute: int = 100,
    burst_capacity: int = 20
)

if limiter.check_limit(client_id):
    # Process request
    pass
```

📝 Error Handling

Custom Exceptions

```python
from osef.exceptions import (
    OSEFError,
    ConfigurationError,
    DataValidationError,
    ModelConvergenceError,
    CCZDetectionError
)

try:
    result = monitor.process_sample(data)
except CCZDetectionError as e:
    logger.error(f"CCZ detection failed: {e}")
    # Fallback logic
except ModelConvergenceError as e:
    logger.warning(f"Model didn't converge: {e}")
    # Retry with different parameters
```

Error Response Format

```json
{
  "error": {
    "code": "CCZ_DETECTION_FAILED",
    "message": "Failed to detect Creative Chaos Zone",
    "details": {
      "input_data": {...},
      "model_state": {...},
      "suggestion": "Try increasing sample rate"
    },
    "timestamp": "2026-01-03T12:00:00Z"
  }
}
```

🔄 Serialization

Model Persistence

```python
# Save model
model.save('model_state.pkl')

# Load model
loaded_model = LimitCycleModel.load('model_state.pkl')

# Export to ONNX
model.export_onnx('model.onnx')

# Export to TensorFlow
model.export_tensorflow('model_saved')
```

Result Serialization

```python
# To JSON
json_result = result.to_json(indent=2)

# To DataFrame
df = result.to_dataframe()

# To binary
binary_data = result.to_protobuf()
```

📊 Monitoring Hooks

Custom Callbacks

```python
def custom_alert_callback(result: Dict[str, Any]):
    if result['ccz_detected']:
        send_alert(
            severity='HIGH',
            message=f"CCZ detected at lambda={result['lambda']:.3f}"
        )

monitor.add_callback(custom_alert_callback)
```

Metrics Export

```python
# To Prometheus
monitor.export_metrics_prometheus(port=9090)

# To Datadog
monitor.export_metrics_datadog(api_key='your_key')

# To file
monitor.export_metrics_csv('metrics.csv')
```

🎯 Quick Reference

Common Patterns

Basic Usage

```python
from osef import LimitCycleModel, StabilityMonitor

# Initialize
model = LimitCycleModel()
monitor = StabilityMonitor(model=model)

# Analyze single sample
result = monitor.process_sample(
    timestamp=time.time(),
    pitch=2.3,
    bank=-1.5,
    power=0.78
)

# Batch processing
results = monitor.batch_process(flight_data)
```

Real-time Monitoring

```python
async def monitor_flight(data_stream):
    monitor = StabilityMonitor()
    
    async for sample in data_stream:
        result = monitor.process_sample(**sample)
        
        if result['state'] == 'CCZ':
            await trigger_alert(result)
        
        yield result
```

Integration with Flight Systems

```python
class FlightSystemIntegration:
    def __init__(self):
        self.osef = StabilityMonitor()
        self.guidance = GuidanceSystem()
    
    def on_flight_data(self, data):
        analysis = self.osef.process_sample(data)
        
        if analysis['needs_correction']:
            correction = self.guidance.compute_correction(
                data, 
                analysis['target_state']
            )
            self.apply_correction(correction)
```

Performance Tips

```python
# Use vectorized operations for batch processing
monitor.batch_process(data, parallel=True)

# Adjust sampling for performance
monitor = StabilityMonitor(
    sampling_rate=62.5,  # Half rate for better performance
    buffer_size=500      # Smaller buffer
)

# Enable caching for repeated analyses
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_analysis(pitch, bank, power):
    return monitor.process_sample(pitch, bank, power)
```

Debugging Helpers

```python
# Enable debug logging
import logging
logging.getLogger('osef').setLevel(logging.DEBUG)

# Get detailed diagnostics
diagnostics = monitor.get_diagnostics()

# Export for analysis
monitor.export_debug_info('debug_info.json')
```