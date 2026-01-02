# Contributing to OSEF Framework

Thank you for your interest in contributing to OSEF! 🎉

## 🤝 How to Contribute

### Reporting Bugs 🐛

1. Check if the bug has already been reported in [Issues](https://github.com/emeraldcompass/OSEF-Framework/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs. actual behavior
   - System information (OS, Python version)
   - Relevant code snippets or error messages

### Suggesting Features ✨

1. Check [existing issues](https://github.com/emeraldcompass/OSEF-Framework/issues) for similar suggestions
2. Create a new issue with:
   - Clear description of the feature
   - Use case and motivation
   - Proposed implementation (optional)

### Pull Requests 🔀

1. **Fork** the repository
2. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/amazing-feature
Make your changes:
Follow code style (see below)
Add tests for new functionality
Update documentation as needed
Test your changes:
pytest tests/
Commit with clear messages:
git commit -m "Add amazing feature"
Push to your fork:
git push origin feature/amazing-feature
Open a Pull Request with:
Description of changes
Related issue number (if applicable)
Screenshots (if UI changes)
📝 Code Style
We use Black for code formatting:
black osef/ tests/ examples/
And flake8 for linting:
flake8 osef/ tests/ examples/
Python Style Guidelines
Follow PEP 8
Use type hints where appropriate
Write docstrings for all public functions (Google style)
Keep functions focused and small
Use meaningful variable names
Example:
def compute_lyapunov(trajectory: np.ndarray, 
                     embedding_dim: int = 3) -> float:
    """
    Compute the largest Lyapunov exponent for a trajectory.
    
    Args:
        trajectory: Time series data (N x D array)
        embedding_dim: Embedding dimension for phase space reconstruction
        
    Returns:
        Largest Lyapunov exponent (λ)
        
    Raises:
        ValueError: If trajectory has insufficient data points
    """
    # Implementation here
    pass
🧪 Testing
All new code must have tests
Aim for >80% code coverage
Run tests before submitting PR:
pytest tests/ --cov=osef --cov-report=html
📚 Documentation
Update docstrings for modified functions
Update README.md if adding major features
Add examples for new functionality
Update API reference in docs/api_reference.md
🌿 Branch Naming
feature/ - New features
bugfix/ - Bug fixes
docs/ - Documentation updates
refactor/ - Code refactoring
test/ - Test additions/improvements
📬 Communication
Join discussions in GitHub Discussions
Tag maintainers for urgent issues: @emeraldcompass
Be respectful and professional
📜 Code of Conduct
We follow the Contributor Covenant Code of Conduct.
🙏 Recognition
Contributors will be acknowledged in:
README.md Contributors section
Release notes
Project documentation
Thank you for making OSEF better! 🚀

