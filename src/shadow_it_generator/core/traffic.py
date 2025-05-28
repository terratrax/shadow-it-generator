"""Traffic pattern generation.

This module handles the generation of realistic traffic patterns based on
time of day, user activity levels, and enterprise behavior patterns.
"""

from datetime import datetime, time
from typing import List, Dict, Tuple
import math
import random
import logging

from .user import User, UserType
from ..config.models import EnterpriseConfig


logger = logging.getLogger(__name__)


class TrafficGenerator:
    """Generates realistic traffic patterns for the enterprise.
    
    This class manages temporal traffic distribution, user activity levels,
    and handles special patterns like lunch dips and weekend activity.
    """
    
    def __init__(self, enterprise_config: EnterpriseConfig):
        """Initialize the traffic generator.
        
        Args:
            enterprise_config: Enterprise-wide configuration
        """
        self.config = enterprise_config
        self.working_hours = self._parse_working_hours()
        # Get peak hours from traffic config
        self.peak_hours = enterprise_config.traffic.get('peak_hours', [9, 10, 11, 14, 15, 16])
    
    def get_active_users(self,
                        hour: datetime,
                        users: List[User]) -> List[User]:
        """Determine which users are active during a specific hour.
        
        Args:
            hour: The hour to evaluate
            users: Complete user population
            
        Returns:
            List of active users for this hour
        """
        # Calculate activity factor for this hour
        activity_factor = self._calculate_activity_factor(hour)
        
        # Determine number of active users
        base_active_count = int(len(users) * activity_factor)
        
        # Add some randomness
        variance = int(base_active_count * 0.1)
        active_count = base_active_count + random.randint(-variance, variance)
        active_count = max(1, min(active_count, len(users)))
        
        # Select users based on their type and activity patterns
        active_users = self._select_active_users(users, active_count, hour)
        
        logger.debug(f"Hour {hour}: {len(active_users)} active users "
                    f"(activity factor: {activity_factor:.2f})")
        
        return active_users
    
    def _calculate_activity_factor(self, hour: datetime) -> float:
        """Calculate activity level factor for a specific hour.
        
        Args:
            hour: Hour to evaluate
            
        Returns:
            Activity factor between 0.0 and 1.0
        """
        hour_of_day = hour.hour
        day_of_week = hour.weekday()
        
        # Weekend activity reduction
        if day_of_week >= 5:  # Saturday or Sunday
            base_factor = self.config.traffic.get('weekend_activity', 0.1)
        else:
            base_factor = 1.0
        
        # Time of day adjustment
        if self._is_working_hours(hour_of_day):
            # Working hours activity
            if hour_of_day in self.peak_hours:
                time_factor = 1.0
            elif hour_of_day == 12 and self.config.traffic.get('lunch_dip', True):
                time_factor = 0.7  # 30% reduction during lunch
            else:
                time_factor = 0.8
        else:
            # After hours activity
            time_factor = 0.1
        
        return base_factor * time_factor
    
    def _is_working_hours(self, hour: int) -> bool:
        """Check if an hour is within working hours.
        
        Args:
            hour: Hour of day (0-23)
            
        Returns:
            True if within working hours
        """
        start, end = self.working_hours
        return start <= hour < end
    
    def _parse_working_hours(self) -> Tuple[int, int]:
        """Parse working hours from configuration.
        
        Returns:
            Tuple of (start_hour, end_hour)
        """
        # Get working hours from config
        working_hours = self.config.traffic.get('working_hours', {'start': '08:00', 'end': '18:00'})
        start = datetime.strptime(working_hours.get('start', '08:00'), "%H:%M").hour
        end = datetime.strptime(working_hours.get('end', '18:00'), "%H:%M").hour
        return start, end
    
    def _select_active_users(self,
                           users: List[User],
                           count: int,
                           hour: datetime) -> List[User]:
        """Select which users should be active.
        
        Args:
            users: Complete user population
            count: Number of users to select
            hour: Current hour
            
        Returns:
            List of selected active users
        """
        # Weight users by their likelihood to be active
        weights = []
        
        for user in users:
            weight = self._get_user_activity_weight(user, hour)
            weights.append(weight)
        
        # Select users based on weights
        selected = random.choices(users, weights=weights, k=count)
        
        # Remove duplicates while preserving count
        unique_users = list(set(selected))
        while len(unique_users) < count and len(unique_users) < len(users):
            additional = random.choices(users, weights=weights, 
                                      k=count - len(unique_users))
            unique_users.extend(additional)
            unique_users = list(set(unique_users))
        
        return unique_users[:count]
    
    def _get_user_activity_weight(self, user: User, hour: datetime) -> float:
        """Calculate activity weight for a user at a specific time.
        
        Args:
            user: User to evaluate
            hour: Current hour
            
        Returns:
            Weight factor for selection probability
        """
        hour_of_day = hour.hour
        
        # Base weight by user type
        if user.user_type == UserType.POWER:
            base_weight = 1.5  # Power users more likely to be active
        elif user.user_type == UserType.RISKY:
            # Risky users have irregular patterns
            if self._is_working_hours(hour_of_day):
                base_weight = 1.2
            else:
                base_weight = 2.0  # More likely after hours
        else:
            base_weight = 1.0
        
        # Department-based adjustments
        if user.department == 'IT' and not self._is_working_hours(hour_of_day):
            base_weight *= 1.5  # IT more likely to work off-hours
        elif user.department == 'Sales' and hour_of_day in self.peak_hours:
            base_weight *= 1.2  # Sales more active during peak
        
        return base_weight
    
    def calculate_request_distribution(self,
                                     hour: datetime,
                                     total_requests: int) -> List[Tuple[datetime, int]]:
        """Distribute requests throughout an hour.
        
        Args:
            hour: Start of the hour
            total_requests: Total requests to distribute
            
        Returns:
            List of (timestamp, request_count) tuples
        """
        # Divide hour into 5-minute intervals
        intervals = []
        
        for minute in range(0, 60, 5):
            interval_start = hour.replace(minute=minute)
            
            # Calculate weight for this interval
            weight = self._get_interval_weight(interval_start)
            intervals.append((interval_start, weight))
        
        # Distribute requests based on weights
        total_weight = sum(w for _, w in intervals)
        distribution = []
        
        for timestamp, weight in intervals:
            count = int(total_requests * weight / total_weight)
            if count > 0:
                distribution.append((timestamp, count))
        
        return distribution
    
    def _get_interval_weight(self, timestamp: datetime) -> float:
        """Calculate weight for a 5-minute interval.
        
        Args:
            timestamp: Start of the interval
            
        Returns:
            Weight for request distribution
        """
        # Add some randomness to avoid perfectly uniform distribution
        base_weight = 1.0
        
        # Slight preference for round numbers (00, 15, 30, 45)
        if timestamp.minute % 15 == 0:
            base_weight *= 1.1
        
        # Add random variation
        variation = random.uniform(0.8, 1.2)
        
        return base_weight * variation