"""
Traffic pattern generation for cloud services.

This module defines patterns for generating realistic network traffic
based on service characteristics and user behavior.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import random
import numpy as np


@dataclass
class TrafficPattern:
    """
    Defines traffic patterns for a specific type of activity.
    
    Used to generate realistic request patterns, sizes, and timing.
    """
    name: str
    request_rate_per_hour: float
    avg_request_size: int
    avg_response_size: int
    size_std_dev_percent: float = 0.3
    burst_probability: float = 0.2
    
    def generate_request_size(self) -> int:
        """Generate a request size based on the pattern."""
        std_dev = self.avg_request_size * self.size_std_dev_percent
        size = int(np.random.normal(self.avg_request_size, std_dev))
        return max(100, size)  # Minimum 100 bytes
    
    def generate_response_size(self) -> int:
        """Generate a response size based on the pattern."""
        std_dev = self.avg_response_size * self.size_std_dev_percent
        size = int(np.random.normal(self.avg_response_size, std_dev))
        return max(100, size)  # Minimum 100 bytes
    
    def should_burst(self) -> bool:
        """Determine if this should be a burst of activity."""
        return random.random() < self.burst_probability
    
    def get_burst_multiplier(self) -> float:
        """Get multiplier for burst activity."""
        return random.uniform(2.0, 5.0)


class TrafficPatternLibrary:
    """
    Library of common traffic patterns for different activities.
    """
    
    @staticmethod
    def get_patterns() -> Dict[str, TrafficPattern]:
        """Get predefined traffic patterns."""
        return {
            'web_browsing': TrafficPattern(
                name='web_browsing',
                request_rate_per_hour=30,
                avg_request_size=500,
                avg_response_size=50000,
                burst_probability=0.3
            ),
            'api_heavy': TrafficPattern(
                name='api_heavy',
                request_rate_per_hour=120,
                avg_request_size=2000,
                avg_response_size=5000,
                burst_probability=0.4
            ),
            'file_transfer': TrafficPattern(
                name='file_transfer',
                request_rate_per_hour=10,
                avg_request_size=1000,
                avg_response_size=10485760,  # 10MB average
                size_std_dev_percent=0.8,  # High variance
                burst_probability=0.1
            ),
            'streaming': TrafficPattern(
                name='streaming',
                request_rate_per_hour=300,
                avg_request_size=200,
                avg_response_size=65536,  # 64KB chunks
                burst_probability=0.1
            ),
            'chat': TrafficPattern(
                name='chat',
                request_rate_per_hour=60,
                avg_request_size=300,
                avg_response_size=500,
                burst_probability=0.5
            ),
            'authentication': TrafficPattern(
                name='authentication',
                request_rate_per_hour=2,
                avg_request_size=1000,
                avg_response_size=2000,
                burst_probability=0.0
            )
        }
    
    @staticmethod
    def get_pattern_for_category(category: str) -> TrafficPattern:
        """Get appropriate pattern for a service category."""
        category_patterns = {
            'cloud_storage': 'file_transfer',
            'collaboration': 'chat',
            'productivity': 'api_heavy',
            'development': 'api_heavy',
            'social_media': 'web_browsing',
            'email': 'chat',
            'streaming': 'streaming',
            'file_transfer': 'file_transfer',
            'communication': 'chat',
            'analytics': 'api_heavy',
            'ai_ml': 'api_heavy'
        }
        
        pattern_name = category_patterns.get(category, 'web_browsing')
        patterns = TrafficPatternLibrary.get_patterns()
        return patterns.get(pattern_name, patterns['web_browsing'])