"""Service access patterns and behaviors."""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, time
import random
from dataclasses import dataclass

from ..models.cloud_service import CloudService


@dataclass
class AccessPattern:
    """Defines access pattern for a service."""
    peak_hours: List[int]  # Hours with peak usage (0-23)
    min_requests_per_session: int
    max_requests_per_session: int
    session_duration_minutes: Tuple[int, int]  # Min, max duration
    burst_probability: float  # Probability of burst activity
    burst_multiplier: float  # Request multiplier during bursts


class ServicePattern:
    """Manages service-specific access patterns."""
    
    # Default patterns by category
    CATEGORY_PATTERNS: Dict[str, AccessPattern] = {
        "collaboration": AccessPattern(
            peak_hours=[9, 10, 11, 14, 15, 16],
            min_requests_per_session=5,
            max_requests_per_session=50,
            session_duration_minutes=(10, 120),
            burst_probability=0.15,
            burst_multiplier=2.5
        ),
        "storage": AccessPattern(
            peak_hours=[9, 10, 14, 15],
            min_requests_per_session=3,
            max_requests_per_session=30,
            session_duration_minutes=(5, 60),
            burst_probability=0.20,
            burst_multiplier=3.0
        ),
        "productivity": AccessPattern(
            peak_hours=[9, 10, 11, 13, 14, 15, 16],
            min_requests_per_session=10,
            max_requests_per_session=100,
            session_duration_minutes=(15, 180),
            burst_probability=0.10,
            burst_multiplier=2.0
        ),
        "communication": AccessPattern(
            peak_hours=[8, 9, 10, 11, 13, 14, 15, 16, 17],
            min_requests_per_session=20,
            max_requests_per_session=200,
            session_duration_minutes=(5, 240),
            burst_probability=0.25,
            burst_multiplier=3.5
        ),
        "development": AccessPattern(
            peak_hours=[10, 11, 14, 15, 16, 20, 21],
            min_requests_per_session=15,
            max_requests_per_session=150,
            session_duration_minutes=(30, 240),
            burst_probability=0.12,
            burst_multiplier=2.2
        ),
        "analytics": AccessPattern(
            peak_hours=[9, 10, 14, 15],
            min_requests_per_session=5,
            max_requests_per_session=40,
            session_duration_minutes=(10, 90),
            burst_probability=0.08,
            burst_multiplier=1.8
        ),
        "security": AccessPattern(
            peak_hours=[8, 9, 14, 15],
            min_requests_per_session=3,
            max_requests_per_session=20,
            session_duration_minutes=(5, 30),
            burst_probability=0.05,
            burst_multiplier=1.5
        ),
        "marketing": AccessPattern(
            peak_hours=[9, 10, 11, 14, 15],
            min_requests_per_session=8,
            max_requests_per_session=60,
            session_duration_minutes=(15, 120),
            burst_probability=0.18,
            burst_multiplier=2.8
        ),
        "finance": AccessPattern(
            peak_hours=[9, 10, 14, 15, 16],
            min_requests_per_session=4,
            max_requests_per_session=25,
            session_duration_minutes=(10, 60),
            burst_probability=0.06,
            burst_multiplier=1.6
        ),
        "entertainment": AccessPattern(
            peak_hours=[12, 13, 17, 18, 19, 20, 21],
            min_requests_per_session=10,
            max_requests_per_session=80,
            session_duration_minutes=(10, 90),
            burst_probability=0.30,
            burst_multiplier=4.0
        ),
        "social": AccessPattern(
            peak_hours=[8, 12, 13, 17, 18, 19, 20],
            min_requests_per_session=15,
            max_requests_per_session=100,
            session_duration_minutes=(5, 60),
            burst_probability=0.35,
            burst_multiplier=4.5
        ),
        "education": AccessPattern(
            peak_hours=[9, 10, 11, 14, 15, 19, 20],
            min_requests_per_session=8,
            max_requests_per_session=50,
            session_duration_minutes=(20, 120),
            burst_probability=0.10,
            burst_multiplier=2.0
        ),
        "hr": AccessPattern(
            peak_hours=[9, 10, 14, 15],
            min_requests_per_session=3,
            max_requests_per_session=20,
            session_duration_minutes=(5, 45),
            burst_probability=0.08,
            burst_multiplier=1.8
        ),
        "legal": AccessPattern(
            peak_hours=[9, 10, 11, 14, 15, 16],
            min_requests_per_session=5,
            max_requests_per_session=30,
            session_duration_minutes=(15, 90),
            burst_probability=0.05,
            burst_multiplier=1.5
        ),
        "healthcare": AccessPattern(
            peak_hours=[8, 9, 10, 14, 15],
            min_requests_per_session=4,
            max_requests_per_session=25,
            session_duration_minutes=(10, 60),
            burst_probability=0.07,
            burst_multiplier=1.7
        )
    }
    
    # Service-specific overrides
    SERVICE_OVERRIDES: Dict[str, AccessPattern] = {
        "slack": AccessPattern(
            peak_hours=[8, 9, 10, 11, 13, 14, 15, 16, 17],
            min_requests_per_session=30,
            max_requests_per_session=300,
            session_duration_minutes=(30, 480),
            burst_probability=0.30,
            burst_multiplier=4.0
        ),
        "microsoft-teams": AccessPattern(
            peak_hours=[8, 9, 10, 11, 13, 14, 15, 16, 17],
            min_requests_per_session=25,
            max_requests_per_session=250,
            session_duration_minutes=(30, 480),
            burst_probability=0.25,
            burst_multiplier=3.5
        ),
        "zoom": AccessPattern(
            peak_hours=[9, 10, 11, 14, 15, 16],
            min_requests_per_session=5,
            max_requests_per_session=50,
            session_duration_minutes=(30, 90),
            burst_probability=0.10,
            burst_multiplier=2.0
        ),
        "youtube": AccessPattern(
            peak_hours=[12, 13, 17, 18, 19, 20, 21, 22],
            min_requests_per_session=20,
            max_requests_per_session=150,
            session_duration_minutes=(5, 120),
            burst_probability=0.40,
            burst_multiplier=5.0
        ),
        "netflix": AccessPattern(
            peak_hours=[12, 13, 18, 19, 20, 21, 22],
            min_requests_per_session=10,
            max_requests_per_session=100,
            session_duration_minutes=(30, 180),
            burst_probability=0.20,
            burst_multiplier=3.0
        )
    }
    
    @classmethod
    def get_pattern(cls, service: CloudService) -> AccessPattern:
        """Get access pattern for a service.
        
        Args:
            service: CloudService instance
            
        Returns:
            AccessPattern for the service
        """
        # Check for service-specific override first
        if service.name in cls.SERVICE_OVERRIDES:
            return cls.SERVICE_OVERRIDES[service.name]
        
        # Fall back to category pattern
        return cls.CATEGORY_PATTERNS.get(
            service.category,
            cls.CATEGORY_PATTERNS["productivity"]  # Default pattern
        )
    
    @classmethod
    def is_peak_hour(cls, service: CloudService, hour: int) -> bool:
        """Check if given hour is peak time for the service.
        
        Args:
            service: CloudService instance
            hour: Hour of day (0-23)
            
        Returns:
            True if peak hour, False otherwise
        """
        pattern = cls.get_pattern(service)
        return hour in pattern.peak_hours
    
    @classmethod
    def get_activity_multiplier(cls, service: CloudService, 
                               current_time: datetime) -> float:
        """Get activity multiplier based on time of day.
        
        Args:
            service: CloudService instance
            current_time: Current datetime
            
        Returns:
            Multiplier for activity level (0.1 to 2.0)
        """
        hour = current_time.hour
        pattern = cls.get_pattern(service)
        
        if hour in pattern.peak_hours:
            return random.uniform(1.5, 2.0)
        elif 6 <= hour <= 22:  # Business/active hours
            return random.uniform(0.8, 1.2)
        else:  # Night hours
            return random.uniform(0.1, 0.3)
    
    @classmethod
    def should_burst(cls, service: CloudService) -> bool:
        """Determine if service should experience burst activity.
        
        Args:
            service: CloudService instance
            
        Returns:
            True if burst should occur, False otherwise
        """
        pattern = cls.get_pattern(service)
        return random.random() < pattern.burst_probability
    
    @classmethod
    def get_session_duration(cls, service: CloudService) -> int:
        """Get session duration for the service.
        
        Args:
            service: CloudService instance
            
        Returns:
            Session duration in minutes
        """
        pattern = cls.get_pattern(service)
        min_duration, max_duration = pattern.session_duration_minutes
        return random.randint(min_duration, max_duration)
    
    @classmethod
    def get_request_count(cls, service: CloudService, is_burst: bool = False) -> int:
        """Get number of requests for a session.
        
        Args:
            service: CloudService instance
            is_burst: Whether this is a burst session
            
        Returns:
            Number of requests
        """
        pattern = cls.get_pattern(service)
        base_requests = random.randint(
            pattern.min_requests_per_session,
            pattern.max_requests_per_session
        )
        
        if is_burst:
            return int(base_requests * pattern.burst_multiplier)
        
        return base_requests