"""Logging configuration and utilities.

This module provides logging setup and configuration for the application.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(level: str = 'INFO', log_file: str = None):
    """Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    # Create logs directory if needed
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configure handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=handlers
    )
    
    # Set specific logger levels
    logging.getLogger('faker').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


class ProgressLogger:
    """Helper class for logging progress of long-running operations."""
    
    def __init__(self, total: int, description: str = "Processing"):
        """Initialize progress logger.
        
        Args:
            total: Total number of items
            description: Description of the operation
        """
        self.total = total
        self.description = description
        self.current = 0
        self.start_time = datetime.now()
        self.logger = logging.getLogger(__name__)
        self.last_percentage = -1
    
    def update(self, count: int = 1):
        """Update progress.
        
        Args:
            count: Number of items completed
        """
        self.current += count
        percentage = int((self.current / self.total) * 100)
        
        # Only log at 10% intervals
        if percentage // 10 > self.last_percentage // 10:
            self.last_percentage = percentage
            elapsed = (datetime.now() - self.start_time).total_seconds()
            
            if self.current > 0:
                rate = self.current / elapsed
                remaining = (self.total - self.current) / rate
                
                self.logger.info(
                    f"{self.description}: {percentage}% complete "
                    f"({self.current}/{self.total}) - "
                    f"Rate: {rate:.1f}/s - "
                    f"ETA: {remaining:.0f}s"
                )
            else:
                self.logger.info(
                    f"{self.description}: {percentage}% complete "
                    f"({self.current}/{self.total})"
                )
    
    def finish(self):
        """Mark operation as finished."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        rate = self.total / elapsed if elapsed > 0 else 0
        
        self.logger.info(
            f"{self.description}: Complete! "
            f"Processed {self.total} items in {elapsed:.1f}s "
            f"(avg {rate:.1f}/s)"
        )