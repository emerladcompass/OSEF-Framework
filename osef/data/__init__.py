"""
Data processing modules for OSEF Framework
"""

# Conditional imports based on pandas availability
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    DataFrame = pd.DataFrame
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None
    DataFrame = type('DataFrame', (), {})  # Dummy class

# Now import modules
from osef.data.fdr_reader import FDRReader
from osef.data.preprocessing import preprocess_fdr_data
from osef.data.synthetic_data import generate_synthetic_flight

__all__ = [
    'FDRReader',
    'preprocess_fdr_data', 
    'generate_synthetic_flight',
    'PANDAS_AVAILABLE',
    'DataFrame' if PANDAS_AVAILABLE else None
]
