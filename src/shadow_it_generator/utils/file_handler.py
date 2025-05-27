"""File handling utilities for log output.

This module provides utilities for writing log files with rotation
and compression support.
"""

import gzip
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Union
import logging


logger = logging.getLogger(__name__)


class FileHandler:
    """Handles log file writing with rotation and compression.
    
    This class manages writing log entries to files with support for:
    - Time-based rotation (hourly, daily)
    - Automatic compression
    - Directory structure creation
    """
    
    def __init__(self,
                 output_dir: Path,
                 file_pattern: str,
                 rotation: str = 'hourly',
                 compress: bool = False):
        """Initialize the file handler.
        
        Args:
            output_dir: Base output directory
            file_pattern: File naming pattern with placeholders
            rotation: Rotation strategy ('hourly' or 'daily')
            compress: Whether to compress files
        """
        self.output_dir = Path(output_dir)
        self.file_pattern = file_pattern
        self.rotation = rotation
        self.compress = compress
        self.current_file = None
        self.current_path = None
        self.current_hour = None
        self.entries_written = 0
    
    def write_log(self, log_entry: str, timestamp: datetime):
        """Write a log entry to the appropriate file.
        
        Args:
            log_entry: Formatted log string
            timestamp: Timestamp for file organization
        """
        # Determine file path based on timestamp
        file_path = self._get_file_path(timestamp)
        
        # Check if we need to rotate
        if self._should_rotate(file_path, timestamp):
            self._rotate_file()
        
        # Open new file if needed
        if self.current_file is None:
            self._open_file(file_path)
        
        # Write log entry
        self.current_file.write(log_entry + '\n')
        self.entries_written += 1
        
        # Flush periodically
        if self.entries_written % 1000 == 0:
            self.current_file.flush()
    
    def _get_file_path(self, timestamp: datetime) -> Path:
        """Generate file path based on timestamp and pattern.
        
        Args:
            timestamp: Timestamp for file naming
            
        Returns:
            Path object for the log file
        """
        # Replace placeholders in pattern
        replacements = {
            '{year}': str(timestamp.year),
            '{month}': f"{timestamp.month:02d}",
            '{day}': f"{timestamp.day:02d}",
            '{hour}': f"{timestamp.hour:02d}",
            '{timestamp}': timestamp.strftime('%Y%m%d_%H%M%S')
        }
        
        file_name = self.file_pattern
        for placeholder, value in replacements.items():
            file_name = file_name.replace(placeholder, value)
        
        return self.output_dir / file_name
    
    def _should_rotate(self, file_path: Path, timestamp: datetime) -> bool:
        """Check if file rotation is needed.
        
        Args:
            file_path: New file path
            timestamp: Current timestamp
            
        Returns:
            True if rotation is needed
        """
        if self.current_path is None:
            return False
        
        if self.rotation == 'hourly':
            return (self.current_hour is None or 
                   timestamp.hour != self.current_hour)
        elif self.rotation == 'daily':
            return file_path.parent != self.current_path.parent
        else:
            return file_path != self.current_path
    
    def _rotate_file(self):
        """Rotate the current file."""
        if self.current_file:
            self.current_file.close()
            
            # Compress if configured
            if self.compress and self.current_path:
                self._compress_file(self.current_path)
            
            logger.info(f"Rotated log file: {self.current_path} "
                       f"({self.entries_written} entries)")
        
        self.current_file = None
        self.current_path = None
        self.current_hour = None
        self.entries_written = 0
    
    def _open_file(self, file_path: Path):
        """Open a new log file.
        
        Args:
            file_path: Path to the new file
        """
        # Create directory if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open file
        self.current_file = open(file_path, 'a', encoding='utf-8')
        self.current_path = file_path
        self.current_hour = datetime.now().hour
        
        logger.info(f"Opened log file: {file_path}")
    
    def _compress_file(self, file_path: Path):
        """Compress a log file using gzip.
        
        Args:
            file_path: Path to file to compress
        """
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        try:
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Remove original file
            os.remove(file_path)
            logger.info(f"Compressed log file: {compressed_path}")
            
        except Exception as e:
            logger.error(f"Failed to compress {file_path}: {e}")
    
    def close(self):
        """Close the file handler and perform final rotation."""
        if self.current_file:
            self._rotate_file()


class BatchFileWriter:
    """Optimized batch writer for high-volume log generation.
    
    This class buffers log entries in memory and writes them in batches
    for improved performance.
    """
    
    def __init__(self, file_handler: FileHandler, batch_size: int = 10000):
        """Initialize the batch writer.
        
        Args:
            file_handler: Underlying file handler
            batch_size: Number of entries to buffer
        """
        self.file_handler = file_handler
        self.batch_size = batch_size
        self.buffer = []
        self.buffer_timestamps = []
    
    def write_log(self, log_entry: str, timestamp: datetime):
        """Add log entry to buffer.
        
        Args:
            log_entry: Formatted log string
            timestamp: Log timestamp
        """
        self.buffer.append(log_entry)
        self.buffer_timestamps.append(timestamp)
        
        if len(self.buffer) >= self.batch_size:
            self.flush()
    
    def flush(self):
        """Write buffered entries to disk."""
        if not self.buffer:
            return
        
        # Group by file to minimize file operations
        file_groups = {}
        
        for entry, timestamp in zip(self.buffer, self.buffer_timestamps):
            file_path = self.file_handler._get_file_path(timestamp)
            if file_path not in file_groups:
                file_groups[file_path] = []
            file_groups[file_path].append((entry, timestamp))
        
        # Write each group
        for entries in file_groups.values():
            for entry, timestamp in entries:
                self.file_handler.write_log(entry, timestamp)
        
        # Clear buffer
        self.buffer.clear()
        self.buffer_timestamps.clear()
    
    def close(self):
        """Flush remaining entries and close."""
        self.flush()
        self.file_handler.close()