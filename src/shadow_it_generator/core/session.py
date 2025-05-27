"""Session generation and management.

This module handles the creation of user sessions, including timing,
duration, and request patterns within sessions.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import random
import numpy as np
import logging

from .user import User, UserType
from ..config.models import CloudService, EnterpriseConfig


logger = logging.getLogger(__name__)


@dataclass
class Session:
    """Represents a user session with a cloud service.
    
    Attributes:
        session_id: Unique session identifier
        user: User associated with the session
        service: Cloud service being accessed
        start_time: Session start timestamp
        end_time: Session end timestamp
        request_count: Number of requests in the session
        total_bytes_in: Total bytes sent
        total_bytes_out: Total bytes received
    """
    session_id: str
    user: User
    service: CloudService
    start_time: datetime
    end_time: datetime
    request_count: int
    total_bytes_in: int
    total_bytes_out: int


@dataclass
class Request:
    """Represents a single HTTP request within a session.
    
    Attributes:
        timestamp: Request timestamp
        method: HTTP method
        url: Full URL
        path: URL path
        status_code: HTTP response code
        bytes_in: Request size
        bytes_out: Response size
        response_time: Response time in milliseconds
    """
    timestamp: datetime
    method: str
    url: str
    path: str
    status_code: int
    bytes_in: int
    bytes_out: int
    response_time: int


class SessionGenerator:
    """Generates realistic user sessions with cloud services.
    
    This class creates sessions with appropriate timing, duration,
    and request patterns based on user profiles and service characteristics.
    """
    
    def __init__(self, enterprise_config: EnterpriseConfig):
        """Initialize the session generator.
        
        Args:
            enterprise_config: Enterprise-wide configuration
        """
        self.config = enterprise_config
        self._session_counter = 0
    
    def generate_user_sessions(self,
                             user: User,
                             services: List[CloudService],
                             hour_start: datetime) -> List[Session]:
        """Generate sessions for a user within a specific hour.
        
        Args:
            user: User to generate sessions for
            services: Available cloud services
            hour_start: Start of the hour
            
        Returns:
            List of generated sessions
        """
        sessions = []
        
        # Determine number of services to access based on user type
        service_count = self._get_service_count(user)
        
        # Select services based on user preferences and type
        selected_services = self._select_services(user, services, service_count)
        
        # Generate sessions for each selected service
        for service in selected_services:
            session = self._create_session(user, service, hour_start)
            if session:
                sessions.append(session)
        
        return sessions
    
    def generate_session_requests(self, session: Session) -> List[Request]:
        """Generate individual requests within a session.
        
        Args:
            session: Session to generate requests for
            
        Returns:
            List of generated requests
        """
        requests = []
        service = session.service
        
        # Generate requests based on service traffic patterns
        request_times = self._generate_request_times(
            session.start_time,
            session.end_time,
            session.request_count
        )
        
        for timestamp in request_times:
            # Select endpoint based on weights
            endpoint = self._select_endpoint(service.endpoints)
            
            # Generate request details
            request = self._create_request(
                timestamp=timestamp,
                endpoint=endpoint,
                service=service,
                user=session.user
            )
            
            requests.append(request)
        
        return requests
    
    def _get_service_count(self, user: User) -> int:
        """Determine number of services a user will access.
        
        Args:
            user: User to evaluate
            
        Returns:
            Number of services to access
        """
        profile = self._get_user_profile(user.user_type)
        mean = profile.avg_services_per_day / 24  # Services per hour
        std = profile.service_variance / 24
        
        # Use normal distribution with bounds
        count = int(np.random.normal(mean, std))
        return max(0, count)
    
    def _get_user_profile(self, user_type: UserType):
        """Get user profile configuration for a user type.
        
        Args:
            user_type: Type of user
            
        Returns:
            User profile configuration
        """
        profiles = self.config.user_profiles
        
        if user_type == UserType.NORMAL:
            return profiles.normal_users
        elif user_type == UserType.POWER:
            return profiles.power_users
        else:
            return profiles.risky_users
    
    def _select_services(self,
                        user: User,
                        services: List[CloudService],
                        count: int) -> List[CloudService]:
        """Select services for a user to access.
        
        Args:
            user: User selecting services
            services: Available services
            count: Number of services to select
            
        Returns:
            List of selected services
        """
        # TODO: Implement intelligent service selection
        # Consider user preferences, department, and risk profile
        return random.sample(services, min(count, len(services)))
    
    def _create_session(self,
                       user: User,
                       service: CloudService,
                       hour_start: datetime) -> Optional[Session]:
        """Create a single session.
        
        Args:
            user: User for the session
            service: Service being accessed
            hour_start: Start of the hour
            
        Returns:
            Created session or None if skipped
        """
        # Check if service is blocked for this user
        if not service.access.allowed and user.user_type != UserType.RISKY:
            return None  # Normal users don't access blocked services
        
        # Generate session timing
        start_offset = random.randint(0, 3000)  # Within first 50 minutes
        duration = self._generate_session_duration()
        
        start_time = hour_start + timedelta(seconds=start_offset)
        end_time = start_time + timedelta(seconds=duration)
        
        # Generate request count
        mean_requests = service.traffic.avg_requests_per_session
        std_requests = service.traffic.requests_std_deviation
        request_count = max(1, int(np.random.normal(mean_requests, std_requests)))
        
        # Generate traffic volume
        mean_bytes = service.traffic.avg_bytes_per_session
        std_bytes = service.traffic.bytes_std_deviation
        total_bytes = max(100, int(np.random.normal(mean_bytes, std_bytes)))
        
        # Split bytes between in and out (more out for downloads)
        bytes_in = int(total_bytes * 0.2)
        bytes_out = int(total_bytes * 0.8)
        
        self._session_counter += 1
        
        return Session(
            session_id=f"SES{self._session_counter:010d}",
            user=user,
            service=service,
            start_time=start_time,
            end_time=end_time,
            request_count=request_count,
            total_bytes_in=bytes_in,
            total_bytes_out=bytes_out
        )
    
    def _generate_session_duration(self) -> int:
        """Generate realistic session duration in seconds.
        
        Returns:
            Duration in seconds
        """
        # Normal distribution: mean 30 min, std 10 min
        duration = np.random.normal(1800, 600)
        return max(60, int(duration))  # At least 1 minute
    
    def _generate_request_times(self,
                               start: datetime,
                               end: datetime,
                               count: int) -> List[datetime]:
        """Generate request timestamps within a session.
        
        Args:
            start: Session start time
            end: Session end time
            count: Number of requests
            
        Returns:
            List of request timestamps
        """
        duration = (end - start).total_seconds()
        
        # Generate exponentially distributed intervals
        intervals = np.random.exponential(duration / count, count)
        
        # Normalize to fit within duration
        intervals = intervals * (duration / intervals.sum())
        
        # Convert to timestamps
        timestamps = []
        current = 0
        
        for interval in intervals:
            current += interval
            if current < duration:
                timestamps.append(start + timedelta(seconds=current))
        
        return timestamps
    
    def _select_endpoint(self, endpoints: List[Any]) -> Any:
        """Select an endpoint based on configured weights.
        
        Args:
            endpoints: List of available endpoints
            
        Returns:
            Selected endpoint
        """
        weights = [e.weight for e in endpoints]
        return random.choices(endpoints, weights=weights)[0]
    
    def _create_request(self,
                       timestamp: datetime,
                       endpoint: Any,
                       service: CloudService,
                       user: User) -> Request:
        """Create a single request.
        
        Args:
            timestamp: Request timestamp
            endpoint: Endpoint being accessed
            service: Service being accessed
            user: User making the request
            
        Returns:
            Created request
        """
        # Build URL
        protocol = "https" if service.name != "Legacy HTTP Service" else "http"
        url = f"{protocol}://{service.hostname}{endpoint.path}"
        
        # Determine status code
        if service.access.allowed:
            status_code = 200 if random.random() > 0.05 else 404
        else:
            status_code = 403  # Blocked
        
        # Generate request/response sizes
        if endpoint.method in ['POST', 'PUT']:
            bytes_in = random.randint(1000, 50000)
            bytes_out = random.randint(100, 1000)
        else:
            bytes_in = random.randint(100, 1000)
            bytes_out = random.randint(1000, 100000)
        
        # Response time (milliseconds)
        response_time = random.randint(50, 500)
        
        return Request(
            timestamp=timestamp,
            method=endpoint.method,
            url=url,
            path=endpoint.path,
            status_code=status_code,
            bytes_in=bytes_in,
            bytes_out=bytes_out,
            response_time=response_time
        )