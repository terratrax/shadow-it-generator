"""Session model."""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import random


class Session:
    """Represents a user session with a service."""
    
    def __init__(self, user: Any, service: Any, start_time: datetime):
        self.user = user
        self.service = service
        self.start_time = start_time
        self.session_id = f"{user.id}-{service.name}-{int(start_time.timestamp())}"
        self.duration = self._calculate_duration()
        self.end_time = start_time + timedelta(seconds=self.duration)
        self.requests: List[Dict[str, Any]] = []
    
    def _calculate_duration(self) -> int:
        """Calculate session duration in seconds."""
        # Simple duration logic based on service category
        if self.service.category in ["communication", "collaboration"]:
            return random.randint(300, 7200)  # 5 min to 2 hours
        elif self.service.category in ["storage", "productivity"]:
            return random.randint(180, 3600)  # 3 min to 1 hour
        else:
            return random.randint(60, 1800)  # 1 min to 30 min
    
    def generate_requests(self) -> List[Dict[str, Any]]:
        """Generate requests for the session."""
        num_requests = random.randint(5, 50)
        current_time = self.start_time
        
        for _ in range(num_requests):
            # Random time between requests
            current_time += timedelta(seconds=random.randint(1, 30))
            if current_time > self.end_time:
                break
            
            request = {
                "timestamp": current_time,
                "user": self.user,
                "service": self.service,
                "session_id": self.session_id,
                "action": random.choice(["browse", "download", "upload", "api_call"]),
                "bytes": random.randint(1000, 1000000)
            }
            self.requests.append(request)
        
        return self.requests