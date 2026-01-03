Installation Guide - OSEF Framework

🚀 Quick Installation

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

📦 System Requirements

Minimum Requirements

· Python 3.9 or higher
· 2GB RAM
· 500MB disk space
· Linux, macOS, or Windows 10+

Recommended Requirements

· Python 3.10+
· 4GB RAM
· 1GB disk space
· Multi-core processor

🔧 Detailed Installation Methods

1. Using pip

Basic Installation

```bash
pip install osef-framework
```

With Optional Dependencies

```bash
# With development tools
pip install osef-framework[dev]

# With visualization
pip install osef-framework[viz]

# With machine learning extensions
pip install osef-framework[ml]

# Full installation
pip install osef-framework[all]
```

2. Using conda

Create New Environment

```bash
conda create -n osef python=3.10
conda activate osef
pip install osef-framework
```

Using environment.yml

```bash
conda env create -f environment.yml
conda activate osef
```

3. Using Docker

Pull from Docker Hub

```bash
docker pull emerladcompass/osef:latest
```

Pull from GitHub Container Registry

```bash
docker pull ghcr.io/emerladcompass/osef:latest
```

Run Container

```bash
docker run -p 8080:8080 ghcr.io/emerladcompass/osef:latest
```

4. Building from Source

Clone and Install

```bash
git clone https://github.com/emerladcompass/OSEF-Framework.git
cd OSEF-Framework

# Install in development mode
pip install -e .

# Or install with all dependencies
pip install -e .[dev,test,viz]
```

Build Wheels

```bash
# Build distribution packages
python setup.py sdist bdist_wheel

# Install from built wheel
pip install dist/osef_framework-*.whl
```

⚙️ Platform-Specific Instructions

Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-dev python3-pip

# Install OSEF
pip3 install osef-framework
```

Linux (Fedora/RHEL)

```bash
sudo dnf install python3-devel python3-pip
pip3 install osef-framework
```

macOS

```bash
# Using Homebrew
brew install python
pip install osef-framework

# Or using pyenv
pyenv install 3.10.0
pyenv global 3.10.0
pip install osef-framework
```

Windows

```bash
# Using Python from python.org
python -m pip install osef-framework

# Or using Windows Terminal/PowerShell
pip install osef-framework
```

Termux (Android)

```bash
pkg update
pkg install python
pip install osef-framework
```

Raspberry Pi

```bash
sudo apt-get update
sudo apt-get install python3-pip
pip3 install osef-framework
```

🔐 Virtual Environments

Using venv

```bash
python -m venv osef-env

# Activate on Linux/macOS
source osef-env/bin/activate

# Activate on Windows
osef-env\Scripts\activate

# Install OSEF
pip install osef-framework
```

Using virtualenv

```bash
pip install virtualenv
virtualenv osef-env
source osef-env/bin/activate
pip install osef-framework
```

Using pipenv

```bash
pip install pipenv
pipenv install osef-framework
pipenv shell
```

🐳 Container Installation

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
```

Kubernetes

```bash
kubectl apply -f https://raw.githubusercontent.com/emerladcompass/OSEF-Framework/main/deployment/kubernetes/osef-deployment.yaml
```

Podman

```bash
podman run -d -p 8080:8080 ghcr.io/emerladcompass/osef:latest
```

📚 Verification

Check Installation

```bash
# Check version
python -c "import osef; print(osef.__version__)"

# Verify import
python -c "from osef.core import LimitCycleModel; print('Import successful')"

# Run basic test
python -c "
from osef import StabilityMonitor
monitor = StabilityMonitor()
print('OSEF initialized successfully')
"
```

Test Examples

```bash
# Run example scripts
python examples/01_basic_usage.py
python examples/02_flight_simulation.py
```

🔄 Upgrading

Upgrade from PyPI

```bash
pip install --upgrade osef-framework
```

Upgrade from Source

```bash
cd OSEF-Framework
git pull origin main
pip install --upgrade -e .
```

Check Current Version

```bash
pip show osef-framework
```

🛠️ Troubleshooting

Common Issues

Import Errors

```bash
# If you get module not found errors
pip install --force-reinstall osef-framework
```

Permission Errors

```bash
# Use --user flag
pip install --user osef-framework

# Or use virtual environment
python -m venv env
source env/bin/activate
pip install osef-framework
```

Version Conflicts

```bash
# Create fresh environment
python -m venv fresh-env
source fresh-env/bin/activate
pip install osef-framework
```

Missing Dependencies

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install python3-dev build-essential

# Install system dependencies (macOS)
brew install python-tk
```

Debug Logging

```bash
# Enable verbose output
pip install -v osef-framework

# Check installation logs
pip install osef-framework --log install.log
```

📊 Performance Tuning

Optimized Installation

```bash
# Install with performance flags
pip install osef-framework --no-binary :all:

# Or use optimized wheels
pip install osef-framework --only-binary :all:
```

GPU Acceleration (Optional)

```bash
# Install with CUDA support (if available)
pip install osef-framework[gpu]

# Or manually install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

🔗 Integration with Other Tools

Jupyter Notebook

```bash
pip install osef-framework
pip install jupyter
jupyter notebook
```

VS Code Development

```bash
# Install in development mode
pip install -e .[dev]

# Install VS Code extensions
code --install-extension ms-python.python
```

PyCharm Setup

1. Create new project
2. Set Python interpreter to your virtual environment
3. Install package via PyCharm package manager

📝 Post-Installation Steps

Configuration Setup

```bash
# Create config directory
mkdir -p ~/.osef

# Generate default config
python -c "from osef.utils import Config; Config().save_default('~/.osef/config.yaml')"
```

Test Installation

```bash
# Run test suite
pytest tests/

# Or run specific tests
pytest tests/test_limit_cycle.py
```

Verify Functionality

```python
# Quick verification script
import osef
import numpy as np

# Test basic functionality
model = osef.core.LimitCycleModel()
cycle = model.compute_limit_cycle()
print(f"Limit cycle computed: {cycle['converged']}")

# Test monitoring
monitor = osef.core.StabilityMonitor()
result = monitor.process_sample(
    timestamp=0.0,
    pitch=2.5,
    bank=-1.2,
    power=0.85
)
print(f"Sample processed: {result['state']}")
```

🚨 Security Considerations

Isolated Installation

```bash
# Use container for isolation
docker run --rm -it ghcr.io/emerladcompass/osef:latest

# Or use virtual machine
```

Network Security

```bash
# Install from trusted sources only
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org osef-framework
```

📈 Monitoring Installation

Check System Impact

```bash
# Monitor resource usage
pip install psutil
python -c "
import psutil, osef
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'CPU: {psutil.cpu_percent()}%')
"
```

Log Installation

```bash
# Log installation details
python -c "
import sys, platform, osef
print(f'Python: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'OSEF: {osef.__version__}')
" > installation.log
```

🔄 Uninstallation

Remove Package

```bash
# Uninstall OSEF
pip uninstall osef-framework

# Remove dependencies (optional)
pip freeze | grep osef-framework | xargs pip uninstall -y
```

Clean Virtual Environment

```bash
# Deactivate and remove
deactivate
rm -rf osef-env
```

Remove Docker Images

```bash
docker rmi ghcr.io/emerladcompass/osef:latest
docker system prune -a
```

🎯 Quick Reference Commands

One-Liners

```bash
# Install and test in one command
pip install osef-framework && python -c "import osef; print('Success')"

# Development setup
git clone https://github.com/emerladcompass/OSEF-Framework.git && cd OSEF-Framework && pip install -e .[dev]

# Docker quickstart
docker run -p 8080:8080 ghcr.io/emerladcompass/osef:latest
```

Platform-Specific Quick Installs

```bash
# Linux
curl -sSL https://raw.githubusercontent.com/emerladcompass/OSEF-Framework/main/install.sh | bash

# macOS
brew install emerladcompass/tap/osef-framework

# Windows (PowerShell)
iwr -useb https://raw.githubusercontent.com/emerladcompass/OSEF-Framework/main/install.ps1 | iex
```