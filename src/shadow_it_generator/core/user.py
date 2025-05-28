"""
User representation and behavior modeling.

This module defines user entities with their behavior profiles,
service assignments, and activity patterns.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, time
import random
import numpy as np

from ..config.models import UserProfile, CloudService


@dataclass
class User:
    """
    Represents a single user in the enterprise.
    
    Tracks user identity, behavior profile, assigned services,
    and activity patterns.
    """
    id: str
    email: str
    username: str
    full_name: str
    profile: UserProfile
    source_ip: str
    department: Optional[str] = None
    locale: str = "US"
    
    # Services this user has access to
    assigned_services: Set[str] = field(default_factory=set)
    service_adoption_weights: Dict[str, float] = field(default_factory=dict)
    
    # Activity tracking
    last_activity: Optional[datetime] = None
    daily_request_count: int = 0
    sessions_today: int = 0
    
    # User-specific patterns
    work_start_time: time = field(default_factory=lambda: time(8, random.randint(0, 59)))
    work_end_time: time = field(default_factory=lambda: time(17, random.randint(0, 59)))
    lunch_time: time = field(default_factory=lambda: time(12, random.randint(0, 59)))
    
    # Device preferences
    preferred_user_agent: Optional[str] = None
    mobile_probability: float = 0.2  # 20% chance of mobile usage
    
    def __post_init__(self):
        """Initialize user-specific patterns based on profile."""
        # Adjust work hours based on profile
        if self.profile.name == "power_user":
            # Power users often work longer hours
            self.work_start_time = time(7, random.randint(30, 59))
            self.work_end_time = time(18, random.randint(0, 59))
            self.mobile_probability = 0.3
        elif self.profile.name == "risky":
            # Risky users have irregular hours
            self.work_start_time = time(random.randint(6, 10), random.randint(0, 59))
            self.work_end_time = time(random.randint(16, 20), random.randint(0, 59))
            self.mobile_probability = 0.4
    
    def assign_services(self, available_services: List[CloudService]) -> None:
        """
        Assign cloud services to this user based on their profile.
        
        Args:
            available_services: List of all available cloud services
        """
        for service in available_services:
            # Determine if user should have access to this service
            adoption_chance = self._calculate_service_adoption(service)
            
            if random.random() < adoption_chance:
                self.assigned_services.add(service.name)
                # Store individual weight for this user-service combination
                self.service_adoption_weights[service.name] = adoption_chance
    
    def _calculate_service_adoption(self, service: CloudService) -> float:
        """
        Calculate the probability this user will adopt a service.
        
        Args:
            service: The cloud service to evaluate
            
        Returns:
            Probability between 0 and 1
        """
        base_rate = service.activity.user_adoption_rate
        
        # Adjust based on user profile
        if self.profile.name == "normal":
            # Normal users mostly use sanctioned services
            if service.status == "sanctioned":
                multiplier = 1.2
            elif service.status == "unsanctioned":
                multiplier = 0.5
            else:  # blocked
                multiplier = 0.1
        elif self.profile.name == "power_user":
            # Power users use more services overall
            if service.status == "sanctioned":
                multiplier = 1.5
            elif service.status == "unsanctioned":
                multiplier = 0.8
            else:  # blocked
                multiplier = 0.2
        else:  # risky
            # Risky users are more likely to use unsanctioned/blocked services
            if service.status == "sanctioned":
                multiplier = 0.8
            elif service.status == "unsanctioned":
                multiplier = 1.5
            else:  # blocked
                multiplier = 0.8
        
        # Apply shadow IT likelihood from profile
        if service.status != "sanctioned":
            multiplier *= self.profile.shadow_it_likelihood
        
        return min(1.0, base_rate * multiplier)
    
    def get_activity_level(self, current_time: datetime) -> float:
        """
        Get the user's activity level at a given time.
        
        Args:
            current_time: The current timestamp
            
        Returns:
            Activity level between 0 and 1
        """
        hour = current_time.hour
        minute = current_time.minute
        
        # Convert to decimal hour
        decimal_hour = hour + minute / 60.0
        
        # Check if within work hours
        work_start = self.work_start_time.hour + self.work_start_time.minute / 60.0
        work_end = self.work_end_time.hour + self.work_end_time.minute / 60.0
        lunch = self.lunch_time.hour + self.lunch_time.minute / 60.0
        
        if decimal_hour < work_start or decimal_hour > work_end:
            # Outside work hours
            return self.profile.work_hours_adherence * 0.1  # Very low activity
        elif abs(decimal_hour - lunch) < 0.5:
            # Lunch hour
            return 0.3  # Reduced activity
        else:
            # Normal work hours
            # Add some variance throughout the day
            base_activity = 1.0
            
            # Morning ramp-up
            if decimal_hour < work_start + 1:
                base_activity = 0.6 + 0.4 * (decimal_hour - work_start)
            # End of day wind-down
            elif decimal_hour > work_end - 1:
                base_activity = 0.6 + 0.4 * (work_end - decimal_hour)
            
            # Add profile-based variance
            if self.profile.name == "power_user":
                base_activity *= 1.2
            elif self.profile.name == "risky":
                # More erratic patterns
                base_activity *= random.uniform(0.5, 1.5)
            
            return min(1.0, base_activity)
    
    def should_use_mobile(self) -> bool:
        """Determine if user should use mobile device for this session."""
        return random.random() < self.mobile_probability
    
    def get_services_for_hour(self, current_time: datetime) -> List[str]:
        """
        Get the services this user is likely to use in the current hour.
        
        Args:
            current_time: Current timestamp
            
        Returns:
            List of service names to use
        """
        activity_level = self.get_activity_level(current_time)
        
        if activity_level < 0.1:
            return []  # No activity
        
        # Determine number of services to use this hour
        if self.profile.name == "normal":
            mean_services = 2
            std_dev = 1
        elif self.profile.name == "power_user":
            mean_services = 5
            std_dev = 2
        else:  # risky
            mean_services = 4
            std_dev = 3
        
        # Scale by activity level
        num_services = int(max(0, np.random.normal(
            mean_services * activity_level,
            std_dev
        )))
        
        if num_services == 0:
            return []
        
        # Select services based on weights
        services = list(self.assigned_services)
        if not services:
            return []
        
        # Weight selection by adoption weights
        weights = [self.service_adoption_weights.get(s, 0.5) for s in services]
        
        # Don't select more services than available
        num_services = min(num_services, len(services))
        
        selected = np.random.choice(
            services,
            size=num_services,
            replace=False,
            p=np.array(weights) / sum(weights)
        )
        
        return list(selected)