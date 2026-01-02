"""
OSEF: Operational Stability Envelope Framework
Setup script for installation
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

setup(
    name='osef',
    version='0.1.0',
    author='Samir Baladi',
    author_email='emeraldcompass@gmail.com',
    description='Operational Stability Envelope Framework for Aviation Safety',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/emeraldcompass/OSEF-Framework',
    project_urls={
        'Documentation': 'https://emeraldcompass.github.io/Aviation/',
        'Source': 'https://github.com/emeraldcompass/OSEF-Framework',
        'Research Paper': 'https://doi.org/10.17605/OSF.IO/RJBDK',
        'Bug Reports': 'https://github.com/emeraldcompass/OSEF-Framework/issues',
    },
    packages=find_packages(exclude=['tests', 'docs', 'examples']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.2.5',
            'pytest-cov>=3.0.0',
            'black>=21.9b0',
            'flake8>=4.0.1',
            'mypy>=0.910',
        ],
        'docs': [
            'sphinx>=4.2.0',
            'sphinx-rtd-theme>=1.0.0',
            'nbsphinx>=0.8.7',
        ],
        'ml': [
            'tensorflow>=2.8.0',
            'torch>=1.10.0',
        ],
    },
    include_package_data=True,
    package_data={
        'osef': [
            'data/parameters/*.json',
            'data/parameters/*.yaml',
        ],
    },
    entry_points={
        'console_scripts': [
            'osef-simulate=osef.cli:simulate',
            'osef-analyze=osef.cli:analyze',
        ],
    },
    keywords=[
        'aviation',
        'safety',
        'limit-cycle',
        'nonlinear-dynamics',
        'lyapunov',
        'flight-dynamics',
        'real-time-monitoring',
        'van-der-pol',
    ],
    zip_safe=False,
)
