"""
LEEF (Log Event Extended Format) formatter implementation.

Formats log events according to the IBM LEEF specification used by
McAfee Web Gateway and other security products.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import re

from .base import LogFormatter, LogEvent


class LEEFFormatter(LogFormatter):
    """
    Formats log events in LEEF format.
    
    LEEF format structure:
    LEEF:Version|Vendor|Product|Version|EventID|key1=value1|key2=value2|...
    """
    
    def __init__(self, output_dir: Path):
        """Initialize LEEF formatter."""
        super().__init__(output_dir)
        self.vendor = "McAfee"
        self.product = "Web Gateway"
        self.product_version = "8.2.9"
        self.leef_version = "1.0"
        self.current_file = None
        self.current_date = None
    
    def _escape_value(self, value: str) -> str:
        """
        Escape special characters in LEEF values.
        
        LEEF requires escaping of pipe (|) and backslash (\) characters.
        """
        if not isinstance(value, str):
            value = str(value)
        value = value.replace('\\', '\\\\')
        value = value.replace('|', '\\|')
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        return value
    
    def _get_event_id(self, event: LogEvent) -> str:
        """
        Determine the event ID based on the event type.
        
        Event IDs for McAfee Web Gateway:
        - 0: Allowed traffic
        - 1: Blocked traffic
        - 2: Authentication
        - 3: Malware detected
        - 4: DLP violation
        """
        if event.action == "blocked":
            return "1"
        elif event.action == "denied":
            return "1"
        elif hasattr(event, 'event_type') and event.event_type == 'auth':
            return "2"
        else:
            return "0"  # Allowed traffic
    
    def format_event(self, event: LogEvent) -> str:
        """
        Format a log event in LEEF format.
        
        Args:
            event: The event to format
            
        Returns:
            LEEF formatted string
        """
        # Build LEEF header
        header = f"LEEF:{self.leef_version}|{self.vendor}|{self.product}|{self.product_version}|{self._get_event_id(event)}"
        
        # Convert timestamp to milliseconds since epoch
        dev_time = int(event.timestamp.timestamp() * 1000)
        
        # Build key-value pairs
        fields = []
        
        # Required LEEF fields
        fields.append(f"devTime={dev_time}")
        fields.append(f"src={event.source_ip}")
        fields.append(f"dst={event.destination_ip}")
        fields.append(f"srcPort={event.source_port}")
        fields.append(f"dstPort={event.destination_port}")
        
        # User information
        fields.append(f"usrName={self._escape_value(event.username)}")
        fields.append(f"domain={self._escape_value(event.user_domain)}")
        
        # Request information
        fields.append(f"url={self._escape_value(event.url)}")
        fields.append(f"method={event.method}")
        fields.append(f"proto={event.protocol}")
        fields.append(f"status={event.status_code}")
        
        # Traffic information
        fields.append(f"bytesIn={event.bytes_received}")
        fields.append(f"bytesOut={event.bytes_sent}")
        fields.append(f"responseTime={event.duration_ms}")
        
        # User agent
        fields.append(f"userAgent={self._escape_value(event.user_agent)}")
        
        # Category and risk
        fields.append(f"category={self._escape_value(event.category)}")
        fields.append(f"riskLevel={event.risk_level}")
        
        # Action taken
        fields.append(f"action={event.action}")
        
        # Service name if available
        if event.service_name:
            fields.append(f"application={self._escape_value(event.service_name)}")
        
        # Referrer if available
        if event.referrer:
            fields.append(f"referrer={self._escape_value(event.referrer)}")
        
        # Additional fields if provided
        if event.additional_fields:
            for key, value in event.additional_fields.items():
                # Convert camelCase to LEEF style (camelCase is ok in LEEF)
                fields.append(f"{key}={self._escape_value(str(value))}")
        
        # Combine header and fields
        leef_line = header + "|" + "|".join(fields)
        
        return leef_line
    
    def write_event(self, event: LogEvent) -> None:
        """
        Write a formatted event to the appropriate log file.
        
        Log files are organized by date: leef_YYYYMMDD.log
        """
        # Determine file name based on event date
        event_date = event.timestamp.date()
        
        # Check if we need to open a new file
        if self.current_date != event_date or self._file_handle is None:
            # Close previous file if open
            if self._file_handle:
                self._file_handle.close()
            
            # Open new file
            filename = f"leef_{event_date.strftime('%Y%m%d')}.log"
            filepath = self.output_dir / filename
            self._file_handle = open(filepath, 'a', encoding='utf-8')
            self.current_date = event_date
            self.current_file = filepath
        
        # Format and write the event
        leef_line = self.format_event(event)
        self._file_handle.write(leef_line + '\n')
        self._file_handle.flush()  # Ensure data is written
    
    def write_batch(self, events: list[LogEvent]) -> None:
        """
        Write a batch of events efficiently.
        
        Args:
            events: List of events to write
        """
        # Group events by date
        events_by_date = {}
        for event in events:
            event_date = event.timestamp.date()
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(event)
        
        # Write each group
        for date, date_events in sorted(events_by_date.items()):
            filename = f"leef_{date.strftime('%Y%m%d')}.log"
            filepath = self.output_dir / filename
            
            with open(filepath, 'a', encoding='utf-8') as f:
                for event in date_events:
                    leef_line = self.format_event(event)
                    f.write(leef_line + '\n')