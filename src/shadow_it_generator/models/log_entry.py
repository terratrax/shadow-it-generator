"""Log entry model."""

from datetime import datetime
from typing import Dict, Any, Optional


class LogEntry:
    """Represents a single log entry."""
    
    def __init__(self, timestamp: datetime, user: Any, service: Any, 
                 action: str, result: str, bytes_transferred: int = 0,
                 session_id: Optional[str] = None):
        self.timestamp = timestamp
        self.user = user
        self.service = service
        self.action = action
        self.result = result
        self.bytes_transferred = bytes_transferred
        self.session_id = session_id
        self.source_ip = user.ip_address
        self.destination = service.domains[0] if service.domains else "unknown.com"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "user": self.user.email,
            "source_ip": self.source_ip,
            "destination": self.destination,
            "service": self.service.name,
            "category": self.service.category,
            "action": self.action,
            "result": self.result,
            "bytes": self.bytes_transferred,
            "session_id": self.session_id
        }