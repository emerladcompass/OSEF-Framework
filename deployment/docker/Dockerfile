```dockerfile
# CCZ Monitoring System Dockerfile
# Multi-stage build for optimized production deployment

# Stage 1: Builder Stage
FROM python:3.9-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install requirements
RUN pip install --upgrade pip wheel setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime Stage
FROM python:3.9-slim as runtime

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libgomp1 \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r cczuser && useradd -r -g cczuser -m -d /app cczuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=cczuser:cczuser . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/results && \
    chown -R cczuser:cczuser /app

# Switch to non-root user
USER cczuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose ports
EXPOSE 8080  # Web interface
EXPOSE 9090  # Metrics endpoint

# Set environment variables for production
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    CCZ_ENV=production \
    CCZ_LOG_LEVEL=INFO \
    CCZ_DATA_PATH=/app/data \
    CCZ_RESULTS_PATH=/app/results

# Create entrypoint script
COPY --chown=cczuser:cczuser docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]

# Default command
CMD ["python", "main.py", "--mode", "production"]

# Labels
LABEL maintainer="ccz-monitoring-team@example.com" \
      version="1.0.0" \
      description="CCZ (Chaos-to-Zero) Monitoring System" \
      org.opencontainers.image.title="CCZ Monitoring System" \
      org.opencontainers.image.description="Real-time detection of chaotic flight regimes" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.authors="Aviation Safety Team" \
      org.opencontainers.image.licenses="MIT"
```

```bash
# docker-entrypoint.sh
#!/bin/bash
set -e

# Function to wait for database/other services
wait_for_services() {
    echo "Waiting for required services..."
    # Add service wait logic here if needed
    sleep 2
}

# Function to check environment variables
check_env() {
    echo "Checking environment configuration..."
    
    # Required environment variables
    REQUIRED_VARS=("CCZ_ENV")
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            echo "Error: Required environment variable $var is not set"
            exit 1
        fi
    done
    
    echo "Environment check passed"
}

# Function to initialize application
init_app() {
    echo "Initializing CCZ Monitoring System..."
    
    # Create directories if they don't exist
    mkdir -p /app/data /app/logs /app/results /app/models
    
    # Set permissions
    chown -R cczuser:cczuser /app
    
    # Initialize database if needed
    if [ ! -f /app/data/ccz.db ]; then
        echo "Initializing database..."
        python -c "from app.database import init_db; init_db()"
    fi
    
    # Load default models if needed
    if [ ! -f /app/models/default.model ]; then
        echo "Loading default models..."
        python -c "from app.models import load_default_models; load_default_models()"
    fi
}

# Function to run database migrations
run_migrations() {
    if [ -f /app/migrations/versions ]; then
        echo "Running database migrations..."
        alembic upgrade head
    fi
}

# Function to start the application
start_app() {
    echo "Starting CCZ Monitoring System in ${CCZ_ENV} mode..."
    
    if [ "$CCZ_ENV" = "development" ]; then
        # Development mode with hot reload
        echo "Starting in development mode..."
        exec python main.py --mode development --host 0.0.0.0 --port 8080
    elif [ "$CCZ_ENV" = "testing" ]; then
        # Testing mode
        echo "Starting in testing mode..."
        exec python -m pytest tests/ -v
    else
        # Production mode
        echo "Starting in production mode..."
        exec gunicorn \
            --bind 0.0.0.0:8080 \
            --workers 4 \
            --worker-class uvicorn.workers.UvicornWorker \
            --access-logfile /app/logs/access.log \
            --error-logfile /app/logs/error.log \
            --log-level info \
            --timeout 120 \
            --keep-alive 5 \
            app.main:app
    fi
}

# Function to start worker processes
start_workers() {
    if [ "$CCZ_ENV" = "production" ]; then
        echo "Starting background workers..."
        # Start Celery worker if needed
        # celery -A app.tasks worker --loglevel=info &
        
        # Start monitoring daemon
        python -m app.monitoring.daemon &
    fi
}

# Main execution
main() {
    echo "========================================"
    echo "CCZ Monitoring System Docker Entrypoint"
    echo "========================================"
    
    # Check environment
    check_env
    
    # Wait for dependencies
    wait_for_services
    
    # Initialize application
    init_app
    
    # Run migrations
    run_migrations
    
    # Start worker processes
    start_workers
    
    # Start main application
    start_app
}

# Run main function
main "$@"
```

```text
# requirements.txt
# Core dependencies
numpy==1.24.3
pandas==2.0.3
scipy==1.10.1
scikit-learn==1.3.0

# Data processing
numexpr==2.8.4
tables==3.8.0
h5py==3.9.0

# Machine Learning
torch==2.0.1
torchvision==0.15.2
tensorflow==2.13.0
keras==2.13.1

# Visualization
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.15.0
bokeh==3.2.1

# Web framework
fastapi==0.100.0
uvicorn[standard]==0.23.2
gunicorn==21.2.0
jinja2==3.1.2

# Database
sqlalchemy==2.0.19
alembic==1.12.0
redis==5.0.1
psycopg2-binary==2.9.7

# Monitoring & Logging
prometheus-client==0.17.1
grafana-sdk==0.7.2
structlog==23.1.0
loguru==0.7.2

# Utilities
pydantic==2.3.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Testing
pytest==7.4.2
pytest-asyncio==0.21.1
pytest-cov==4.1.0
hypothesis==6.82.2

# Development tools
black==23.7.0
flake8==6.1.0
mypy==1.5.1
pre-commit==3.3.3

# Documentation
sphinx==7.1.2
sphinx-rtd-theme==1.3.0

# Additional scientific computing
numba==0.57.1
statsmodels==0.14.0
pymc==5.7.2

# Time series analysis
arch==6.2.0
pyts==0.13.0

# Signal processing
pywavelets==1.4.1
librosa==0.10.1

# Optimization
optuna==3.3.0
hyperopt==0.2.7

# Serialization
msgpack==1.0.5
orjson==3.9.5
pyarrow==13.0.0

# Networking
aiohttp==3.8.5
websockets==12.0
httpx==0.25.1

# Security
cryptography==41.0.3
bcrypt==4.0.1

# System monitoring
psutil==5.9.6
gpustat==1.0.0

# Email and notifications
python-dotenv==1.0.0
celery==5.3.1

# File formats
openpyxl==3.1.2
xlrd==2.0.1
pyyaml==6.0.1
toml==0.10.2

# Version specific (lock versions for reproducibility)
# No version constraints for the following (use latest compatible)
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  ccz-monitoring:
    build: .
    image: ccz-monitoring:latest
    container_name: ccz-monitoring
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "9090:9090"
    environment:
      - CCZ_ENV=production
      - CCZ_LOG_LEVEL=INFO
      - CCZ_DATABASE_URL=postgresql://postgres:password@postgres/ccz_db
      - CCZ_REDIS_URL=redis://redis:6379/0
      - CCZ_MODEL_PATH=/app/models
      - CCZ_DATA_PATH=/app/data
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
      - ./results:/app/results
      - ./config:/app/config
    networks:
      - ccz-network
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  postgres:
    image: postgres:15-alpine
    container_name: ccz-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=ccz_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - ccz-network
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ccz-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - ccz-network
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  grafana:
    image: grafana/grafana:10.0.0
    container_name: ccz-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3000:3000"
    networks:
      - ccz-network
    depends_on:
      - ccz-monitoring

  prometheus:
    image: prom/prometheus:latest
    container_name: ccz-prometheus
    restart: unless-stopped
    volumes:
      - prometheus-data:/prometheus
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/alert.rules:/etc/prometheus/alert.rules
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    ports:
      - "9091:9090"
    networks:
      - ccz-network

  nginx:
    image: nginx:alpine
    container_name: ccz-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./ssl:/etc/nginx/ssl
    networks:
      - ccz-network
    depends_on:
      - ccz-monitoring

  # Optional services
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    container_name: ccz-mlflow
    restart: unless-stopped
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    ports:
      - "5000:5000"
    volumes:
      - mlflow-data:/mlflow
    networks:
      - ccz-network

  minio:
    image: minio/minio:latest
    container_name: ccz-minio
    restart: unless-stopped
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio-data:/data
    networks:
      - ccz-network

networks:
  ccz-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  postgres-data:
  redis-data:
  grafana-data:
  prometheus-data:
  mlflow-data:
  minio-data:
```

```text
# .dockerignore
# Git
.git
.gitignore
.gitattributes

# IDE
.vscode
.idea
*.swp
*.swo

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Testing
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Jupyter
.ipynb_checkpoints

# Documentation
docs/_build/

# Logs
*.log
logs/

# Data files
data/*.csv
data/*.h5
data/*.pkl
models/*.pkl

# Configs
config/local*
*.local.yaml

# Docker
docker-compose.override.yml

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp

# Large files
*.zip
*.tar.gz
*.rar

# Sensitive files
*.pem
*.key
*.crt
secrets/
credentials/
config/secret*
```

This Docker setup provides:

Key Features:

1. Multi-stage Build: Small final image (runtime stage only)
2. Security: Non-root user, minimal runtime dependencies
3. Health Checks: Automatic container health monitoring
4. Resource Limits: CPU and memory constraints
5. Persistent Storage: Volumes for data, models, logs
6. Full Stack: Includes PostgreSQL, Redis, Grafana, Prometheus
7. Production Ready: Gunicorn with Uvicorn workers

Usage:

```bash
# Build the image
docker build -t ccz-monitoring .

# Run single container
docker run -p 8080:8080 -p 9090:9090 ccz-monitoring

# Use docker-compose
docker-compose up -d

# View logs
docker-compose logs -f ccz-monitoring

# Scale services
docker-compose up -d --scale ccz-monitoring=3

# Run tests
docker-compose run ccz-monitoring python -m pytest

# Backup data
docker-compose exec postgres pg_dump -U postgres ccz_db > backup.sql
```

Environment Variables:

Variable Default Description
CCZ_ENV production Runtime environment
CCZ_LOG_LEVEL INFO Logging level
CCZ_DATABASE_URL - PostgreSQL connection
CCZ_REDIS_URL - Redis connection
CCZ_MODEL_PATH /app/models Path to ML models
CCZ_DATA_PATH /app/data Path to data files
CCZ_RESULTS_PATH /app/results Path to results

The setup is production-ready with monitoring, logging, and scalability in mind.