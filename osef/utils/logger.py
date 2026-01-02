"""
Logging utilities for OSEF
"""

import logging
from typing import Optional
from datetime import datetime


class OSEFLogger:
    """
    Custom logger for OSEF with structured output.
    """
    
    def __init__(self, name: str = "OSEF", level: int = logging.INFO):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create console handler
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(level)
            
            # Format
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            
            self.logger.addHandler(handler)
    
    def log_state_transition(self, old_state: str, new_state: str, t: float):
        """Log state transition."""
        self.logger.info(f"[{t:8.1f}s] State transition: {old_state} → {new_state}")
    
    def log_alert(self, alert: dict):
        """Log alert message."""
        level_map = {
            'INFO': logging.INFO,
            'CAUTION': logging.WARNING,
            'WARNING': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        level = level_map.get(alert.get('level', 'INFO'), logging.INFO)
        self.logger.log(level, f"ALERT: {alert.get('message', 'Unknown')}")
    
    def log_metrics(self, metrics: dict):
        """Log metrics summary."""
        self.logger.info(f"Metrics: {metrics}")
    
    def log_performance(self, task_name: str, duration_ms: float):
        """
        Log execution performance for real-time monitoring.
        
        Args:
            task_name: Name of the processed task (e.g., 'Lyapunov_Calc')
            duration_ms: Execution time in milliseconds
        """
        # Threshold: 125ms = 8Hz limit (as defined in OSEF initialization)
        status = "OK" if duration_ms < 125 else "DELAY"
        self.logger.debug(f"PERF: {task_name} took {duration_ms:.2f}ms [{status}]")

    def log_critical_event(self, event_type: str, details: str):
        """Log safety-critical events with microsecond precision."""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        self.logger.critical(f"CRITICAL [{timestamp}] - {event_type}: {details}")

    def error(self, message: str):
        """Log generic error."""
        self.logger.error(message)

    def warning(self, message: str):
        """Log generic warning."""
        self.logger.warning(message)

    def info(self, message: str):
        """Log generic info."""
        self.logger.info(message)

    def debug(self, message: str):
        """Log generic debug."""
        self.logger.debug(message)


def get_logger(name: str = "OSEF", level: int = logging.INFO) -> OSEFLogger:
    """Utility function to get or create an OSEFLogger instance."""
    return OSEFLogger(name, level)
