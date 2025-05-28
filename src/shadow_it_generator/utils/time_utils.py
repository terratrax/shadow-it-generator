"""
Time-related utilities for log generation.

Handles working hours, weekends, holidays, and time-based activity patterns.
"""

from datetime import datetime, time, timedelta
from typing import List, Tuple, Optional
import random
import numpy as np
from zoneinfo import ZoneInfo


def is_working_hours(
    timestamp: datetime,
    work_start: time = time(8, 0),
    work_end: time = time(18, 0),
    timezone: str = "America/New_York"
) -> bool:
    """
    Check if a timestamp falls within working hours.
    
    Args:
        timestamp: The timestamp to check
        work_start: Start of working hours
        work_end: End of working hours
        timezone: Timezone for the check
        
    Returns:
        True if within working hours
    """
    # Convert to local timezone
    local_time = timestamp.astimezone(ZoneInfo(timezone))
    current_time = local_time.time()
    
    return work_start <= current_time <= work_end


def is_weekend(timestamp: datetime) -> bool:
    """
    Check if a timestamp falls on a weekend.
    
    Args:
        timestamp: The timestamp to check
        
    Returns:
        True if Saturday or Sunday
    """
    return timestamp.weekday() >= 5  # 5 = Saturday, 6 = Sunday


def get_activity_multiplier(
    timestamp: datetime,
    work_start: time = time(8, 0),
    work_end: time = time(18, 0),
    lunch_hour: int = 12,
    timezone: str = "America/New_York"
) -> float:
    """
    Get activity multiplier based on time of day.
    
    Returns a value between 0 and 1 indicating expected activity level.
    
    Args:
        timestamp: Current timestamp
        work_start: Start of working hours
        work_end: End of working hours
        lunch_hour: Hour of lunch break (24-hour format)
        timezone: Timezone for calculations
        
    Returns:
        Activity multiplier between 0 and 1
    """
    # Convert to local timezone
    local_time = timestamp.astimezone(ZoneInfo(timezone))
    
    # Weekend activity is much lower
    if is_weekend(local_time):
        return 0.1
    
    hour = local_time.hour
    minute = local_time.minute
    decimal_hour = hour + minute / 60.0
    
    # Convert work hours to decimal
    work_start_decimal = work_start.hour + work_start.minute / 60.0
    work_end_decimal = work_end.hour + work_end.minute / 60.0
    
    # Outside working hours
    if decimal_hour < work_start_decimal or decimal_hour > work_end_decimal:
        # Some activity before/after work
        if work_start_decimal - 1 < decimal_hour < work_start_decimal:
            # Early morning ramp-up
            return 0.3 * (1 - (work_start_decimal - decimal_hour))
        elif work_end_decimal < decimal_hour < work_end_decimal + 2:
            # Evening wind-down
            return 0.3 * (1 - (decimal_hour - work_end_decimal) / 2)
        else:
            # Late night/early morning
            return 0.05
    
    # Lunch break reduction
    if abs(decimal_hour - lunch_hour) < 0.5:
        return 0.3
    elif abs(decimal_hour - lunch_hour) < 1:
        return 0.6
    
    # Normal working hours - use a bell curve
    # Peak activity around 10 AM and 3 PM
    morning_peak = 10
    afternoon_peak = 15
    
    # Calculate distance from peaks
    morning_distance = abs(decimal_hour - morning_peak)
    afternoon_distance = abs(decimal_hour - afternoon_peak)
    
    # Use the closer peak
    min_distance = min(morning_distance, afternoon_distance)
    
    # Convert to activity level (gaussian-like)
    activity = np.exp(-(min_distance ** 2) / 8)
    
    return min(1.0, activity)


def generate_session_times(
    start_date: datetime,
    end_date: datetime,
    sessions_per_day: int,
    work_start: time = time(8, 0),
    work_end: time = time(18, 0),
    timezone: str = "America/New_York"
) -> List[datetime]:
    """
    Generate session start times across a date range.
    
    Args:
        start_date: Start of period
        end_date: End of period
        sessions_per_day: Average number of sessions per day
        work_start: Start of working hours
        work_end: End of working hours
        timezone: Timezone for generation
        
    Returns:
        List of session start times
    """
    session_times = []
    
    current_date = start_date.date()
    end_date_only = end_date.date()
    
    while current_date <= end_date_only:
        # Skip weekends if desired
        if current_date.weekday() < 5:  # Monday-Friday
            # Vary sessions per day
            daily_sessions = max(1, int(np.random.normal(sessions_per_day, sessions_per_day * 0.3)))
            
            # Generate times throughout the workday
            for _ in range(daily_sessions):
                # Weight towards working hours
                if random.random() < 0.85:  # 85% during work hours
                    hour = random.randint(work_start.hour, work_end.hour - 1)
                    minute = random.randint(0, 59)
                else:  # 15% outside work hours
                    if random.random() < 0.5:
                        # Early morning
                        hour = random.randint(6, work_start.hour - 1)
                    else:
                        # Evening
                        hour = random.randint(work_end.hour, 21)
                    minute = random.randint(0, 59)
                
                session_time = datetime.combine(
                    current_date,
                    time(hour, minute),
                    tzinfo=ZoneInfo(timezone)
                )
                session_times.append(session_time)
        
        current_date += timedelta(days=1)
    
    return sorted(session_times)


def distribute_events_naturally(
    start_time: datetime,
    end_time: datetime,
    num_events: int,
    burst_probability: float = 0.2
) -> List[datetime]:
    """
    Distribute events naturally over a time period.
    
    Uses a combination of uniform and burst patterns to simulate
    realistic event timing.
    
    Args:
        start_time: Start of period
        end_time: End of period  
        num_events: Number of events to generate
        burst_probability: Probability of burst behavior
        
    Returns:
        List of event timestamps
    """
    if num_events == 0:
        return []
    
    events = []
    duration = (end_time - start_time).total_seconds()
    
    if num_events == 1:
        # Single event at random time
        offset = random.uniform(0, duration)
        events.append(start_time + timedelta(seconds=offset))
        return events
    
    # Decide if this is a burst pattern
    if random.random() < burst_probability:
        # Burst pattern - events clustered together
        num_bursts = random.randint(1, min(3, num_events // 3))
        
        for i in range(num_bursts):
            # Random position for burst center
            burst_center = random.uniform(0.1, 0.9) * duration
            burst_size = num_events // num_bursts
            
            # Events around burst center with normal distribution
            for j in range(burst_size):
                offset = np.random.normal(0, duration * 0.05)  # 5% std dev
                event_time = start_time + timedelta(seconds=burst_center + offset)
                
                # Ensure within bounds
                event_time = max(start_time, min(end_time, event_time))
                events.append(event_time)
    else:
        # Regular pattern - roughly uniform with some variance
        base_interval = duration / num_events
        
        current_time = start_time
        for i in range(num_events):
            # Add some randomness to interval
            interval = np.random.exponential(base_interval)
            current_time += timedelta(seconds=interval)
            
            if current_time > end_time:
                current_time = end_time - timedelta(seconds=random.uniform(0, 60))
            
            events.append(current_time)
    
    return sorted(events)


def get_timezone_offset(timezone: str, timestamp: datetime) -> str:
    """
    Get timezone offset string for a timestamp.
    
    Args:
        timezone: Timezone name
        timestamp: Timestamp to check
        
    Returns:
        Offset string like "-0500" or "+0000"
    """
    tz = ZoneInfo(timezone)
    localized = timestamp.astimezone(tz)
    offset = localized.strftime('%z')
    
    # Ensure format is ±HHMM
    if not offset:
        return "+0000"
    
    return offset