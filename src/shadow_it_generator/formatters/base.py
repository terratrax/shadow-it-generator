"""
Base classes for log formatters.

Defines the interface that all log formatters must implement and
common functionality for formatting log events.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LogEvent:
    """
    Represents a single log event to be formatted.
    
    This is a format-agnostic representation of a network traffic event
    that can be converted to various log formats.
    """
    timestamp: datetime
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    username: str
    user_domain: str
    url: str
    method: str  # GET, POST, etc.
    status_code: int
    bytes_sent: int
    bytes_received: int
    duration_ms: int
    user_agent: str
    referrer: Optional[str] = None
    action: str = "allowed"  # allowed, blocked, denied
    category: str = "cloud_services"
    risk_level: str = "low"
    service_name: Optional[str] = None
    protocol: str = "https"
    additional_fields: Optional[Dict[str, Any]] = None


class LogFormatter(ABC):
    """
    Abstract base class for log formatters.
    
    All log format implementations should inherit from this class.
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize the formatter.
        
        Args:
            output_dir: Directory to write formatted logs
        """
        self.output_dir = output_dir
        self._file_handle = None
        
    def setup(self) -> None:
        """Setup the formatter and create output directory."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    @abstractmethod
    def format_event(self, event: LogEvent) -> str:
        """
        Format a single log event.
        
        Args:
            event: The event to format
            
        Returns:
            Formatted log line as string
        """
        pass
        
    @abstractmethod
    def write_event(self, event: LogEvent) -> None:
        """
        Write a formatted event to the output file.
        
        Args:
            event: The event to write
        """
        pass
        
    def finalize(self) -> None:
        """Cleanup and close any open file handles."""
        if self._file_handle:
            self._file_handle.close()