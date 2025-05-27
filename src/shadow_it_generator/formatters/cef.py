"""
CEF (Common Event Format) formatter implementation.

Formats log events according to the ArcSight CEF specification.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import re

from .base import LogFormatter, LogEvent


class CEFFormatter(LogFormatter):
    """
    Formats log events in CEF format.
    
    CEF format structure:
    CEF:Version|Device Vendor|Device Product|Device Version|Device Event Class ID|Name|Severity|Extension
    """
    
    def __init__(self, output_dir: Path):
        """Initialize CEF formatter."""
        super().__init__(output_dir)
        self.vendor = "McAfee"
        self.product = "Web Gateway"
        self.product_version = "8.2.9"
        self.cef_version = "0"  # CEF version is always 0
        self.current_file = None
        self.current_date = None
    
    def _escape_header(self, value: str) -> str:
        """
        Escape special characters in CEF header fields.
        
        Header fields need to escape pipe (|) and backslash (\).
        """
        if not isinstance(value, str):
            value = str(value)
        value = value.replace('\\', '\\\\')
        value = value.replace('|', '\\|')
        return value
    
    def _escape_extension(self, value: str) -> str:
        """
        Escape special characters in CEF extension fields.
        
        Extension fields need to escape equals (=) and backslash (\).
        """
        if not isinstance(value, str):
            value = str(value)
        value = value.replace('\\', '\\\\')
        value = value.replace('=', '\\=')
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        return value
    
    def _get_severity(self, event: LogEvent) -> int:
        """
        Determine the severity level (0-10) based on the event.
        
        Severity mapping:
        - 0-3: Low (allowed traffic, normal activity)
        - 4-6: Medium (unsanctioned services, policy violations)
        - 7-8: High (blocked traffic, security risks)
        - 9-10: Critical (malware, data breach attempts)
        """
        if event.action == "allowed":
            if event.risk_level == "low":
                return 1
            elif event.risk_level == "medium":
                return 3
            else:
                return 4
        elif event.action in ["blocked", "denied"]:
            if event.risk_level == "high":
                return 8
            elif event.risk_level == "medium":
                return 6
            else:
                return 5
        else:
            return 3
    
    def _get_event_class_id(self, event: LogEvent) -> str:
        """
        Determine the event class ID based on the event type.
        
        Event class IDs:
        - 100: Web request allowed
        - 101: Web request blocked
        - 102: Authentication event
        - 103: Malware detected
        - 104: DLP violation
        - 105: Shadow IT detected
        """
        if event.action == "blocked":
            return "101"
        elif event.action == "denied":
            return "101"
        elif hasattr(event, 'event_type'):
            if event.event_type == 'auth':
                return "102"
            elif event.event_type == 'malware':
                return "103"
            elif event.event_type == 'dlp':
                return "104"
        elif event.category == "shadow_it":
            return "105"
        else:
            return "100"  # Allowed web request
    
    def _get_event_name(self, event: LogEvent) -> str:
        """Generate a descriptive name for the event."""
        if event.action == "blocked":
            return f"Blocked access to {event.service_name or 'web service'}"
        elif event.action == "denied":
            return f"Denied access to {event.service_name or 'web service'}"
        else:
            return f"Web request to {event.service_name or 'service'}"
    
    def format_event(self, event: LogEvent) -> str:
        """
        Format a log event in CEF format.
        
        Args:
            event: The event to format
            
        Returns:
            CEF formatted string
        """
        # Build CEF header
        header_parts = [
            f"CEF:{self.cef_version}",
            self._escape_header(self.vendor),
            self._escape_header(self.product),
            self._escape_header(self.product_version),
            self._get_event_class_id(event),
            self._escape_header(self._get_event_name(event)),
            str(self._get_severity(event))
        ]
        header = "|".join(header_parts)
        
        # Build extension fields (key=value pairs)
        extensions = []
        
        # Timestamp
        extensions.append(f"rt={int(event.timestamp.timestamp() * 1000)}")
        
        # Source and destination
        extensions.append(f"src={event.source_ip}")
        extensions.append(f"dst={event.destination_ip}")
        extensions.append(f"spt={event.source_port}")
        extensions.append(f"dpt={event.destination_port}")
        
        # User information
        extensions.append(f"suser={self._escape_extension(event.username)}")
        extensions.append(f"sntdom={self._escape_extension(event.user_domain)}")
        
        # Request information
        extensions.append(f"request={self._escape_extension(event.url)}")
        extensions.append(f"requestMethod={event.method}")
        extensions.append(f"app={event.protocol.upper()}")
        
        # Response
        extensions.append(f"flexNumber1={event.status_code}")
        extensions.append(f"flexNumber1Label=HTTPStatus")
        
        # Traffic metrics
        extensions.append(f"in={event.bytes_received}")
        extensions.append(f"out={event.bytes_sent}")
        extensions.append(f"cn1={event.duration_ms}")
        extensions.append(f"cn1Label=ResponseTime")
        
        # User agent
        extensions.append(f"requestClientApplication={self._escape_extension(event.user_agent)}")
        
        # Category and action
        extensions.append(f"cat={self._escape_extension(event.category)}")
        extensions.append(f"act={event.action}")
        
        # Risk level
        extensions.append(f"flexString1={event.risk_level}")
        extensions.append(f"flexString1Label=RiskLevel")
        
        # Service name
        if event.service_name:
            extensions.append(f"destinationServiceName={self._escape_extension(event.service_name)}")
        
        # Referrer
        if event.referrer:
            extensions.append(f"requestContext={self._escape_extension(event.referrer)}")
        
        # Additional fields
        if event.additional_fields:
            # Map additional fields to CEF custom fields
            flex_string_index = 2
            custom_index = 1
            
            for key, value in event.additional_fields.items():
                if flex_string_index <= 4:  # CEF supports flexString1-4
                    extensions.append(f"flexString{flex_string_index}={self._escape_extension(str(value))}")
                    extensions.append(f"flexString{flex_string_index}Label={key}")
                    flex_string_index += 1
                elif custom_index <= 3:  # Use custom fields cs1-cs6
                    extensions.append(f"cs{custom_index}={self._escape_extension(str(value))}")
                    extensions.append(f"cs{custom_index}Label={key}")
                    custom_index += 1
        
        # Combine header and extensions
        cef_line = header + "|" + " ".join(extensions)
        
        return cef_line
    
    def write_event(self, event: LogEvent) -> None:
        """
        Write a formatted event to the appropriate log file.
        
        Log files are organized by date: cef_YYYYMMDD.log
        """
        # Determine file name based on event date
        event_date = event.timestamp.date()
        
        # Check if we need to open a new file
        if self.current_date != event_date or self._file_handle is None:
            # Close previous file if open
            if self._file_handle:
                self._file_handle.close()
            
            # Open new file
            filename = f"cef_{event_date.strftime('%Y%m%d')}.log"
            filepath = self.output_dir / filename
            self._file_handle = open(filepath, 'a', encoding='utf-8')
            self.current_date = event_date
            self.current_file = filepath
        
        # Format and write the event
        cef_line = self.format_event(event)
        self._file_handle.write(cef_line + '\n')
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
            filename = f"cef_{date.strftime('%Y%m%d')}.log"
            filepath = self.output_dir / filename
            
            with open(filepath, 'a', encoding='utf-8') as f:
                for event in date_events:
                    cef_line = self.format_event(event)
                    f.write(cef_line + '\n')