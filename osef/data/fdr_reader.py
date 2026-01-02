"""
Flight Data Recorder (FDR) Reader
Handles reading and parsing FDR data from various formats
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, List, Tuple
import warnings
import os


class FDRReader:
    """
    Reader for Flight Data Recorder files.
    
    Supports:
    - CSV format
    - HDF5 format
    - Custom binary formats (future)
    
    Extracts P (Pitch), B (Bank), W (Power) from FDR parameters.
    """
    
    # Standard FDR parameter names (varies by aircraft/airline)
    PITCH_PARAMS = ['PITCH_ANGLE', 'PITCH', 'P', 'PITCH_ATT']
    BANK_PARAMS = ['ROLL_ANGLE', 'BANK_ANGLE', 'ROLL', 'B', 'BANK']
    POWER_PARAMS = ['N1_AVG', 'N1', 'EPR', 'THRUST', 'POWER']
    
    def __init__(self, sampling_rate: float = 8.0):
        """
        Initialize FDR Reader.
        
        Args:
            sampling_rate: Target sampling rate in Hz (default 8 Hz)
        """
        self.sampling_rate = sampling_rate
        self.dt = 1.0 / sampling_rate
        
    def read_csv(self, 
                 filepath: str,
                 time_col: str = 'time',
                 pitch_col: Optional[str] = None,
                 bank_col: Optional[str] = None,
                 power_col: Optional[str] = None) -> pd.DataFrame:
        """
        Read FDR data from CSV file.
        
        Args:
            filepath: Path to CSV file
            time_col: Name of time column
            pitch_col: Name of pitch column (auto-detect if None)
            bank_col: Name of bank column (auto-detect if None)
            power_col: Name of power column (auto-detect if None)
            
        Returns:
            DataFrame with columns: time, P, B, W
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Read CSV
        df = pd.read_csv(filepath)
        
        # Auto-detect columns if not specified
        if pitch_col is None:
            pitch_col = self._find_column(df.columns, self.PITCH_PARAMS)
        if bank_col is None:
            bank_col = self._find_column(df.columns, self.BANK_PARAMS)
        if power_col is None:
            power_col = self._find_column(df.columns, self.POWER_PARAMS)
        
        # Check required columns exist
        required = {
            'time': time_col,
            'P': pitch_col,
            'B': bank_col,
            'W': power_col
        }
        
        for name, col in required.items():
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found for {name}")
        
        # Extract and rename
        result = pd.DataFrame({
            'time': df[time_col],
            'P': df[pitch_col],
            'B': df[bank_col],
            'W': df[power_col]
        })
        
        # Resample to target rate if needed
        result = self._resample_data(result)
        
        return result
    
    def read_hdf5(self, filepath: str) -> pd.DataFrame:
        """
        Read FDR data from HDF5 file.
        
        Args:
            filepath: Path to HDF5 file
            
        Returns:
            DataFrame with columns: time, P, B, W
        """
        try:
            import h5py
        except ImportError:
            raise ImportError("h5py required for HDF5 support. Install: pip install h5py")
        
        with h5py.File(filepath, 'r') as f:
            # Assume standard structure
            time = f['time'][:]
            P = f['pitch'][:]
            B = f['bank'][:]
            
            # Power might be computed from multiple engines
            if 'power' in f:
                W = f['power'][:]
            elif 'N1_left' in f and 'N1_right' in f:
                W = (f['N1_left'][:] + f['N1_right'][:]) / 2.0
            else:
                raise ValueError("No power/thrust data found in HDF5")
        
        result = pd.DataFrame({
            'time': time,
            'P': P,
            'B': B,
            'W': W
        })
        
        return self._resample_data(result)
    
    def _find_column(self, columns: List[str], candidates: List[str]) -> str:
        """
        Find matching column name from candidates.
        
        Args:
            columns: Available column names
            candidates: Candidate names to search for
            
        Returns:
            Matched column name
        """
        # Case-insensitive search
        columns_lower = [c.lower() for c in columns]
        
        for candidate in candidates:
            candidate_lower = candidate.lower()
            if candidate_lower in columns_lower:
                idx = columns_lower.index(candidate_lower)
                return columns[idx]
        
        raise ValueError(f"Could not find column matching any of: {candidates}")
    
    def _resample_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Resample data to target sampling rate.
        
        Args:
            df: DataFrame with 'time' column
            
        Returns:
            Resampled DataFrame
        """
        # Check current sampling rate
        time_diffs = np.diff(df['time'])
        current_dt = np.median(time_diffs)
        current_rate = 1.0 / current_dt if current_dt > 0 else 0
        
        if abs(current_rate - self.sampling_rate) < 0.1:
            # Already at target rate
            return df
        
        # Create uniform time grid
        t_start = df['time'].iloc[0]
        t_end = df['time'].iloc[-1]
        n_points = int((t_end - t_start) * self.sampling_rate) + 1
        time_uniform = np.linspace(t_start, t_end, n_points)
        
        # Interpolate each column
        result = pd.DataFrame({'time': time_uniform})
        
        for col in ['P', 'B', 'W']:
            result[col] = np.interp(time_uniform, df['time'], df[col])
        
        return result
    
    def extract_pbw(self, 
                    df: pd.DataFrame,
                    normalize_power: bool = True) -> Dict[str, np.ndarray]:
        """
        Extract P, B, W as numpy arrays.
        
        Args:
            df: DataFrame with time, P, B, W columns
            normalize_power: Normalize W to 0-1 range
            
        Returns:
            Dictionary with 'time', 'P', 'B', 'W' arrays
        """
        result = {
            'time': df['time'].values,
            'P': df['P'].values,
            'B': df['B'].values,
            'W': df['W'].values
        }
        
        # Normalize power to 0-1 if needed
        if normalize_power and result['W'].max() > 1.5:
            # Assume power is in percent (0-100)
            result['W'] = result['W'] / 100.0
        
        return result


def load_sample_fdr() -> pd.DataFrame:
    """
    Load sample FDR data for testing.
    
    Returns:
        Sample DataFrame
    """
    # Path to sample data
    sample_path = os.path.join(
        os.path.dirname(__file__),
        '../data/sample_fdr.csv'
    )
    
    if os.path.exists(sample_path):
        reader = FDRReader()
        return reader.read_csv(sample_path)
    else:
        warnings.warn("Sample FDR file not found. Generating synthetic data.")
        from osef.data.synthetic_data import generate_synthetic_flight
        return generate_synthetic_flight(duration=300)
