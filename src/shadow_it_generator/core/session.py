"""
User session management for cloud services.

This module handles session creation, duration, and request patterns
within sessions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import random
import numpy as np

from ..config.models import CloudService
from ..formatters.base import LogEvent
from .user import User


@dataclass
class Session:
    """
    Represents a user session with a cloud service.
    
    A session is a period of continuous interaction with a service,
    containing multiple requests.
    """
    id: str
    user: User
    service: CloudService
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # Session characteristics
    is_mobile: bool = False
    user_agent: str = ""
    source_ip: str = ""
    
    # Request tracking
    request_count: int = 0
    total_bytes_sent: int = 0
    total_bytes_received: int = 0
    
    # Session state
    is_authenticated: bool = False
    is_active: bool = True
    was_blocked: bool = False
    
    def __post_init__(self):
        """Initialize session duration based on service and user profile."""
        if self.end_time is None:
            # Generate session duration
            duration = self._generate_duration()
            self.end_time = self.start_time + duration
    
    def _generate_duration(self) -> timedelta:
        """
        Generate realistic session duration based on service type and user profile.
        
        Returns:
            Session duration as timedelta
        """
        # Base duration depends on service category
        category_durations = {
            'collaboration': (20, 60),  # 20-60 minutes
            'cloud_storage': (5, 30),   # 5-30 minutes
            'productivity': (15, 90),   # 15-90 minutes
            'development': (30, 120),   # 30-120 minutes
            'email': (10, 45),          # 10-45 minutes
            'crm': (20, 60),           # 20-60 minutes
            'analytics': (15, 60),      # 15-60 minutes
            'ai_ml': (10, 45),         # 10-45 minutes
            'default': (10, 40)         # Default duration
        }
        
        min_duration, max_duration = category_durations.get(
            self.service.category,
            category_durations['default']
        )
        
        # Adjust based on user profile
        if self.user.profile.name == "power_user":
            # Power users have longer sessions
            max_duration *= 1.5
        elif self.user.profile.name == "risky":
            # Risky users might have shorter, more frequent sessions
            max_duration *= 0.8
        
        # If service is blocked, session is very short
        if self.service.status == "blocked":
            min_duration = 0.5
            max_duration = 2
        
        # Generate duration with some randomness
        duration_minutes = np.random.gamma(2, (max_duration - min_duration) / 4) + min_duration
        duration_minutes = max(min_duration, min(max_duration, duration_minutes))
        
        return timedelta(minutes=duration_minutes)
    
    def generate_requests(self) -> List[Dict[str, Any]]:
        """
        Generate all requests for this session.
        
        Returns:
            List of request dictionaries with timing and details
        """
        requests = []
        current_time = self.start_time
        
        # If blocked service, generate one or a few blocked attempts
        if self.service.status == "blocked":
            num_attempts = random.randint(1, 3)
            for i in range(num_attempts):
                requests.append(self._generate_blocked_request(current_time))
                current_time += timedelta(seconds=random.randint(1, 10))
            self.was_blocked = True
            return requests
        
        # Normal session flow
        # Start with authentication if needed
        if random.random() < 0.8:  # 80% of sessions start with auth
            requests.append(self._generate_auth_request(current_time))
            current_time += timedelta(seconds=random.randint(1, 5))
            self.is_authenticated = True
        
        # Generate activity requests based on service patterns
        session_duration = (self.end_time - self.start_time).total_seconds()
        
        # Determine request rate based on service activity
        if hasattr(self.service, 'activity') and self.service.activity.actions:
            # Calculate total request rate from actions
            total_rate = sum(
                action.avg_per_hour 
                for action in self.service.activity.actions.values() 
                if hasattr(action, 'avg_per_hour') and action.avg_per_hour
            )
            if total_rate == 0:
                total_rate = 30  # Default 30 requests per hour
        else:
            total_rate = 30
        
        # Convert to requests per minute
        requests_per_minute = total_rate / 60
        
        # Generate requests with exponential inter-arrival times
        while current_time < self.end_time:
            # Exponential distribution for realistic spacing
            interval = np.random.exponential(1 / requests_per_minute)
            current_time += timedelta(minutes=interval)
            
            if current_time >= self.end_time:
                break
            
            # Generate request based on service actions
            request = self._generate_activity_request(current_time)
            requests.append(request)
            self.request_count += 1
        
        return requests
    
    def _generate_auth_request(self, timestamp: datetime) -> Dict[str, Any]:
        """Generate an authentication request."""
        return {
            'timestamp': timestamp,
            'type': 'auth',
            'path': random.choice(['/login', '/api/auth', '/oauth/authorize', '/saml/sso']),
            'method': 'POST',
            'status_code': 200 if not self.was_blocked else 403,
            'bytes_sent': random.randint(200, 500),
            'bytes_received': random.randint(1000, 5000),
            'duration_ms': random.randint(100, 500)
        }
    
    def _generate_blocked_request(self, timestamp: datetime) -> Dict[str, Any]:
        """Generate a blocked request."""
        paths = ['/'] + (self.service.traffic_patterns.web_paths or ['/'])
        
        return {
            'timestamp': timestamp,
            'type': 'blocked',
            'path': random.choice(paths),
            'method': 'GET',
            'status_code': 403,
            'bytes_sent': random.randint(100, 300),
            'bytes_received': random.randint(500, 1500),  # Block page
            'duration_ms': random.randint(10, 50),
            'block_reason': self._get_block_reason()
        }
    
    def _generate_activity_request(self, timestamp: datetime) -> Dict[str, Any]:
        """Generate a normal activity request."""
        # Select action type based on weights
        if self.service.activity.actions:
            actions = list(self.service.activity.actions.items())
            action_weights = [action[1].weight for action in actions]
            selected_action = random.choices(actions, weights=action_weights)[0]
            action_name, action_config = selected_action
        else:
            action_name = 'page_view'
            action_config = None
        
        # Determine request characteristics based on action
        request_details = self._get_request_details(action_name, action_config)
        
        # Add common fields
        request_details.update({
            'timestamp': timestamp,
            'type': action_name,
            'status_code': self._get_status_code(),
            'duration_ms': self._get_duration_ms(action_name)
        })
        
        # Track bytes
        self.total_bytes_sent += request_details.get('bytes_sent', 0)
        self.total_bytes_received += request_details.get('bytes_received', 0)
        
        return request_details
    
    def _get_request_details(self, action_name: str, action_config: Any) -> Dict[str, Any]:
        """Get request details based on action type."""
        details = {}
        
        if action_name in ['file_upload', 'file_download']:
            # File operations
            if action_config and hasattr(action_config, 'avg_size_mb'):
                avg_size = action_config.avg_size_mb * 1024 * 1024
                std_dev = getattr(action_config, 'size_std_dev', 5) * 1024 * 1024
                size = int(max(1024, np.random.normal(avg_size, std_dev)))
            else:
                size = random.randint(1024, 10 * 1024 * 1024)
            
            if action_name == 'file_upload':
                details['method'] = 'POST'
                details['path'] = random.choice(['/api/upload', '/files/upload', '/api/v2/files'])
                details['bytes_sent'] = size
                details['bytes_received'] = random.randint(200, 1000)
            else:
                details['method'] = 'GET'
                details['path'] = f'/files/{random.randint(1000, 9999)}/download'
                details['bytes_sent'] = random.randint(200, 500)
                details['bytes_received'] = size
                
        elif action_name in ['message_send', 'email_send']:
            # Communication actions
            details['method'] = 'POST'
            details['path'] = random.choice(['/api/messages', '/api/send', '/api/v2/messages'])
            size = getattr(action_config, 'size_bytes', 1000) if action_config else 1000
            details['bytes_sent'] = size + random.randint(-200, 200)
            details['bytes_received'] = random.randint(200, 500)
            
        elif action_name == 'api_call':
            # API calls
            details['method'] = random.choice(['GET', 'POST', 'PUT', 'DELETE'])
            api_paths = self.service.traffic_patterns.api_endpoints or ['/api/v1/data']
            details['path'] = random.choice(api_paths)
            details['bytes_sent'] = random.randint(100, 2000)
            details['bytes_received'] = random.randint(500, 50000)
            
        else:
            # Default page view
            details['method'] = 'GET'
            paths = self.service.traffic_patterns.web_paths or ['/']
            details['path'] = random.choice(paths)
            details['bytes_sent'] = random.randint(200, 800)
            details['bytes_received'] = random.randint(5000, 100000)
        
        return details
    
    def _get_status_code(self) -> int:
        """Get HTTP status code for request."""
        # Most requests succeed
        if random.random() < 0.95:
            return random.choice([200, 304])  # OK or Not Modified
        else:
            # Occasional errors
            return random.choice([400, 401, 404, 500, 503])
    
    def _get_duration_ms(self, action_name: str) -> int:
        """Get request duration in milliseconds."""
        # Different actions have different typical durations
        if action_name in ['file_upload', 'file_download']:
            return random.randint(500, 5000)
        elif action_name == 'api_call':
            return random.randint(50, 500)
        else:
            return random.randint(100, 1000)
    
    def _get_block_reason(self) -> str:
        """Get reason for blocking based on service."""
        if self.service.risk_level == "high":
            reasons = [
                "High Risk Application",
                "Security Policy Violation",
                "Unauthorized Application",
                "Malware Risk"
            ]
        elif self.service.category in ["social_media", "entertainment"]:
            reasons = [
                "Social Media Blocked",
                "Entertainment Site Blocked",
                "Productivity Policy",
                "Non-Business Use"
            ]
        else:
            reasons = [
                "Unsanctioned Application",
                "Policy Violation",
                "Access Denied",
                "IT Policy Block"
            ]
        
        return random.choice(reasons)