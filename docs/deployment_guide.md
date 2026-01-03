🚀 OSEF Framework - Deployment Guide

📦 Python Package Installation

From PyPI (Recommended)

```bash
pip install osef-framework
```

From GitHub Packages

```bash
pip install osef-framework --extra-index-url https://pypi.pkg.github.com/emerladcompass
```

From Source

```bash
git clone https://github.com/emerladcompass/OSEF-Framework.git
cd OSEF-Framework
pip install -e .
```

🐳 Docker Deployment

Pull from GitHub Container Registry

```bash
docker pull ghcr.io/emerladcompass/osef:latest
```

Run Container

```bash
docker run -p 8080:8080 \
  -v /path/to/data:/app/data \
  ghcr.io/emerladcompass/osef:latest
```

Docker Compose

```yaml
version: '3.8'
services:
  osef:
    image: ghcr.io/emerladcompass/osef:latest
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
    environment:
      - OSEF_LOG_LEVEL=INFO
      - OSEF_CACHE_DIR=/app/cache
```

☸️ Kubernetes Deployment

Deployment Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: osef-framework
spec:
  replicas: 2
  selector:
    matchLabels:
      app: osef
  template:
    metadata:
      labels:
        app: osef
    spec:
      containers:
      - name: osef
        image: ghcr.io/emerladcompass/osef:latest
        ports:
        - containerPort: 8080
        env:
        - name: OSEF_LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

Service Configuration

```yaml
apiVersion: v1
kind: Service
metadata:
  name: osef-service
spec:
  selector:
    app: osef
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

🚀 Standalone Server

Basic Server

```python
from osef.core import StabilityMonitor
from osef.visualization import RealTimeDisplay
import asyncio

async def main():
    monitor = StabilityMonitor()
    display = RealTimeDisplay()
    
    # Start monitoring
    await monitor.start()
    await display.start()
    
    # Keep running
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
```

With Web Interface

```python
from osef.web import OSEFWebServer

server = OSEFWebServer(
    host="0.0.0.0",
    port=8080,
    debug=False
)
server.run()
```

🔧 Environment Configuration

Environment Variables

```bash
export OSEF_LOG_LEVEL=INFO
export OSEF_DATA_PATH=/path/to/data
export OSEF_CACHE_SIZE=1000
export OSEF_UPDATE_INTERVAL=100  # ms
export OSEF_MAX_SAMPLES=10000
```

Configuration File (config.yaml)

```yaml
logging:
  level: INFO
  file: /var/log/osef.log
  
performance:
  update_interval_ms: 100
  max_samples: 10000
  cache_size: 1000
  
data:
  input_path: /data/input
  output_path: /data/output
  cache_path: /data/cache
  
visualization:
  enabled: true
  update_rate: 10  # Hz
  port: 8080
```

📡 Real-time Integration

Flight Simulator Integration

```python
import socket
from osef.core import OSEF

# Connect to flight simulator
def connect_to_simulator(host='127.0.0.1', port=49000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    return sock

# Process real-time data
def process_realtime_data():
    osef = OSEF()
    sock = connect_to_simulator()
    
    while True:
        data, addr = sock.recvfrom(1024)
        result = osef.process_sample(data)
        
        if result['ccz_detected']:
            trigger_alert(result)
```

ROS Integration

```python
#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float32MultiArray
from osef.core import LimitCycleModel

class OSEFROSNode:
    def __init__(self):
        rospy.init_node('osef_node')
        self.model = LimitCycleModel()
        
        self.sub = rospy.Subscriber(
            '/flight_data',
            Float32MultiArray,
            self.callback
        )
        
        self.pub = rospy.Publisher(
            '/stability_status',
            Float32MultiArray,
            queue_size=10
        )
    
    def callback(self, msg):
        data = list(msg.data)
        stability = self.model.analyze(data)
        
        result_msg = Float32MultiArray()
        result_msg.data = stability
        self.pub.publish(result_msg)
```

🔐 Security Configuration

HTTPS Setup

```python
from osef.web import OSEFWebServer

server = OSEFWebServer(
    ssl_cert='cert.pem',
    ssl_key='key.pem',
    port=443
)
```

Authentication

```python
from osef.auth import APIAuth

auth = APIAuth(
    api_keys=['key1', 'key2'],
    require_auth=True,
    rate_limit=100  # requests per minute
)
```

📊 Monitoring & Metrics

Prometheus Metrics

```python
from prometheus_client import start_http_server, Counter, Gauge

# Define metrics
ccz_detections = Counter('osef_ccz_detections_total', 'Total CCZ detections')
processing_time = Gauge('osef_processing_time_ms', 'Processing time in ms')

class MonitoredOSEF(OSEF):
    def process_sample(self, data):
        start_time = time.time()
        result = super().process_sample(data)
        
        if result['ccz_detected']:
            ccz_detections.inc()
        
        processing_time.set((time.time() - start_time) * 1000)
        return result
```

Health Check Endpoint

```python
from flask import Flask, jsonify
import psutil

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'memory_usage': psutil.virtual_memory().percent,
        'cpu_usage': psutil.cpu_percent(),
        'uptime': time.time() - start_time
    })
```

🔄 CI/CD Pipeline

GitHub Actions

```yaml
name: Deploy OSEF

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t ghcr.io/emerladcompass/osef:${{ github.sha }} .
        
    - name: Push to GitHub Container Registry
      run: |
        echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
        docker push ghcr.io/emerladcompass/osef:${{ github.sha }}
        
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/osef osef=ghcr.io/emerladcompass/osef:${{ github.sha }}
```

📈 Scaling Configuration

Horizontal Scaling

```python
from osef.cluster import OSEFCluster

cluster = OSEFCluster(
    nodes=3,
    load_balancer='round-robin',
    failover=True
)

# Add nodes dynamically
cluster.add_node('node1:8080')
cluster.add_node('node2:8080')
```

Database Configuration

```python
from osef.storage import TimescaleDBStorage

storage = TimescaleDBStorage(
    host='localhost',
    port=5432,
    database='osef',
    user='osef_user',
    password='secure_password'
)
```

🛠️ Troubleshooting

Common Issues

1. High Memory Usage

```bash
export OSEF_CACHE_SIZE=500  # Reduce cache size
export OSEF_MAX_SAMPLES=5000  # Reduce sample history
```

1. Slow Processing

```python
# Enable performance mode
osef = OSEF(performance_mode=True, sampling_rate=10)  # Hz
```

1. Connection Issues

```bash
# Check network connectivity
curl -v https://upload.pkg.github.com/
```

Logging Setup

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('osef.log'),
        logging.StreamHandler()
    ]
)
```

🎯 Quick Deployment Commands

Single Command Deployment

```bash
# Deploy everything
./deploy.sh --env production --scale 3 --with-monitoring
```

Development Setup

```bash
# Local development
docker-compose up -d
pip install -e .[dev]
python examples/02_flight_simulation.py
```

Production Deployment

```bash
# Kubernetes
kubectl apply -f deployment/kubernetes/

# Docker Swarm
docker stack deploy -c docker-compose.prod.yml osef
```