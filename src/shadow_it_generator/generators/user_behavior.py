"""
User behavior simulation for realistic activity patterns.

This module simulates different user behaviors including work patterns,
break times, and service usage habits.
"""

from datetime import datetime, time, timedelta
from typing import List, Dict, Any, Tuple, Optional
import random
import numpy as np
from dataclasses import dataclass


@dataclass
class UserBehaviorProfile:
    """Defines behavior characteristics for a user type."""
    name: str
    work_start_mean: float  # Hour in 24h format (e.g., 8.5 = 8:30 AM)
    work_start_std: float   # Standard deviation in hours
    work_duration_mean: float  # Hours
    work_duration_std: float
    break_frequency: int    # Breaks per day
    break_duration: float   # Minutes
    focus_periods: List[Tuple[float, float]]  # High activity periods (start, end)
    multitasking_factor: float  # 0-1, likelihood of using multiple services


class UserBehaviorSimulator:
    """
    Simulates realistic user behavior patterns.
    
    Handles work schedules, break times, and activity variations.
    """
    
    def __init__(self):
        """Initialize behavior profiles."""
        self.profiles = {
            'normal': UserBehaviorProfile(
                name='normal',
                work_start_mean=8.5,
                work_start_std=0.5,
                work_duration_mean=8.0,
                work_duration_std=0.5,
                break_frequency=3,
                break_duration=15,
                focus_periods=[(9.0, 11.0), (14.0, 16.0)],
                multitasking_factor=0.3
            ),
            'power_user': UserBehaviorProfile(
                name='power_user',
                work_start_mean=7.5,
                work_start_std=0.75,
                work_duration_mean=10.0,
                work_duration_std=1.0,
                break_frequency=2,
                break_duration=10,
                focus_periods=[(8.0, 12.0), (13.0, 17.0)],
                multitasking_factor=0.6
            ),
            'risky': UserBehaviorProfile(
                name='risky',
                work_start_mean=9.0,
                work_start_std=1.5,
                work_duration_mean=7.0,
                work_duration_std=2.0,
                break_frequency=5,
                break_duration=20,
                focus_periods=[(10.0, 11.0), (15.0, 16.0)],
                multitasking_factor=0.7
            )
        }
    
    def generate_work_schedule(self, profile_name: str, date: datetime) -> Dict[str, Any]:
        """
        Generate a work schedule for a user on a specific date.
        
        Args:
            profile_name: User profile type
            date: Date to generate schedule for
            
        Returns:
            Dictionary with work schedule details
        """
        profile = self.profiles.get(profile_name, self.profiles['normal'])
        
        # Skip weekends with some probability
        if date.weekday() >= 5:  # Saturday or Sunday
            if random.random() > 0.1:  # 10% chance of weekend work
                return {
                    'is_working': False,
                    'work_start': None,
                    'work_end': None,
                    'breaks': []
                }
        
        # Generate work start time
        start_hour = np.random.normal(profile.work_start_mean, profile.work_start_std)
        start_hour = max(5.0, min(12.0, start_hour))  # Clamp between 5 AM and noon
        
        # Generate work duration
        duration = np.random.normal(profile.work_duration_mean, profile.work_duration_std)
        duration = max(4.0, min(14.0, duration))  # Clamp between 4 and 14 hours
        
        # Convert to times
        start_time = time(int(start_hour), int((start_hour % 1) * 60))
        end_hour = start_hour + duration
        end_time = time(int(end_hour), int((end_hour % 1) * 60))
        
        # Generate breaks
        breaks = self._generate_breaks(start_hour, end_hour, profile)
        
        return {
            'is_working': True,
            'work_start': start_time,
            'work_end': end_time,
            'breaks': breaks,
            'focus_periods': profile.focus_periods
        }
    
    def _generate_breaks(
        self, 
        start_hour: float, 
        end_hour: float, 
        profile: UserBehaviorProfile
    ) -> List[Tuple[float, float]]:
        """Generate break times during work hours."""
        breaks = []
        work_duration = end_hour - start_hour
        
        # Always include lunch break around noon
        if start_hour < 12 and end_hour > 13:
            lunch_start = 12 + random.uniform(-0.5, 0.5)
            lunch_duration = random.uniform(30, 60) / 60  # 30-60 minutes
            breaks.append((lunch_start, lunch_start + lunch_duration))
        
        # Add other breaks
        remaining_breaks = profile.break_frequency - 1
        if remaining_breaks > 0 and work_duration > 4:
            # Distribute breaks throughout the day
            break_interval = work_duration / (remaining_breaks + 1)
            for i in range(remaining_breaks):
                break_time = start_hour + (i + 1) * break_interval + random.uniform(-0.5, 0.5)
                if break_time < end_hour - 1:
                    duration = profile.break_duration / 60  # Convert to hours
                    breaks.append((break_time, break_time + duration))
        
        return sorted(breaks)
    
    def get_activity_level(
        self, 
        current_time: datetime, 
        schedule: Dict[str, Any],
        profile_name: str
    ) -> float:
        """
        Get activity level for a specific time.
        
        Args:
            current_time: Time to check
            schedule: User's work schedule
            profile_name: User profile type
            
        Returns:
            Activity level between 0 and 1
        """
        if not schedule['is_working']:
            return 0.0
        
        hour = current_time.hour + current_time.minute / 60
        
        # Check if outside work hours
        work_start = schedule['work_start'].hour + schedule['work_start'].minute / 60
        work_end = schedule['work_end'].hour + schedule['work_end'].minute / 60
        
        if hour < work_start or hour > work_end:
            return 0.0
        
        # Check if on break
        for break_start, break_end in schedule['breaks']:
            if break_start <= hour <= break_end:
                return 0.2  # Reduced activity during breaks
        
        # Base activity level
        activity = 0.7
        
        # Boost during focus periods
        profile = self.profiles[profile_name]
        for focus_start, focus_end in profile.focus_periods:
            if focus_start <= hour <= focus_end:
                activity = 1.0
                break
        
        # Add some randomness
        activity += random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, activity))
    
    def should_multitask(self, profile_name: str) -> bool:
        """Determine if user should use multiple services simultaneously."""
        profile = self.profiles.get(profile_name, self.profiles['normal'])
        return random.random() < profile.multitasking_factor
    
    def get_session_intensity(self, profile_name: str, service_category: str) -> float:
        """
        Get intensity factor for a session.
        
        Returns a multiplier for request frequency.
        """
        base_intensity = 1.0
        
        # Profile adjustments
        if profile_name == 'power_user':
            base_intensity *= 1.5
        elif profile_name == 'risky':
            base_intensity *= random.uniform(0.5, 2.0)  # More variable
        
        # Category adjustments
        intensity_map = {
            'collaboration': 1.2,
            'development': 1.3,
            'productivity': 1.1,
            'social_media': 0.8,
            'entertainment': 0.7
        }
        
        category_multiplier = intensity_map.get(service_category, 1.0)
        
        return base_intensity * category_multiplier