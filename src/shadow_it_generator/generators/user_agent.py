"""User agent string generation.

This module handles generation and management of user agent strings
for simulating different browsers and devices.
"""

import random
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class UserAgentConfig:
    """Configuration for a user agent."""
    user_agent: str
    weight: float
    browser: str
    os: str
    device_type: str


class UserAgentGenerator:
    """Generates realistic user agent strings.
    
    This class manages a pool of user agent strings and assigns them
    to users based on configured weights and patterns.
    """
    
    def __init__(self, browser_configs: List[Dict[str, any]]):
        """Initialize the user agent generator.
        
        Args:
            browser_configs: List of browser configurations with weights
        """
        self.configs = []
        self.total_weight = 0
        
        # Parse configurations
        for config in browser_configs:
            ua_config = self._parse_user_agent(config)
            self.configs.append(ua_config)
            self.total_weight += ua_config.weight
        
        # Normalize weights
        for config in self.configs:
            config.weight = config.weight / self.total_weight
        
        # User assignments for consistency
        self.user_assignments = {}
    
    def _parse_user_agent(self, config: Dict[str, any]) -> UserAgentConfig:
        """Parse user agent string to extract browser and OS info.
        
        Args:
            config: Browser configuration
            
        Returns:
            UserAgentConfig object
        """
        ua_string = config['user_agent']
        weight = config['weight']
        
        # Simple parsing - in production would use a proper UA parser
        browser = "Unknown"
        os = "Unknown"
        device_type = "Desktop"
        
        if "Chrome" in ua_string:
            browser = "Chrome"
        elif "Firefox" in ua_string:
            browser = "Firefox"
        elif "Safari" in ua_string and "Chrome" not in ua_string:
            browser = "Safari"
        elif "Edge" in ua_string:
            browser = "Edge"
        
        if "Windows" in ua_string:
            os = "Windows"
        elif "Mac OS" in ua_string or "Macintosh" in ua_string:
            os = "macOS"
        elif "Linux" in ua_string:
            os = "Linux"
        elif "Android" in ua_string:
            os = "Android"
            device_type = "Mobile"
        elif "iPhone" in ua_string or "iPad" in ua_string:
            os = "iOS"
            device_type = "Mobile" if "iPhone" in ua_string else "Tablet"
        
        return UserAgentConfig(
            user_agent=ua_string,
            weight=weight,
            browser=browser,
            os=os,
            device_type=device_type
        )
    
    def get_user_agent(self, user_id: str = None) -> str:
        """Get a user agent string for a user.
        
        Args:
            user_id: Optional user ID for consistent assignment
            
        Returns:
            User agent string
        """
        # Check if user already has an assignment
        if user_id and user_id in self.user_assignments:
            return self.user_assignments[user_id]
        
        # Select based on weights
        weights = [config.weight for config in self.configs]
        selected = random.choices(self.configs, weights=weights)[0]
        
        # Store assignment if user_id provided
        if user_id:
            self.user_assignments[user_id] = selected.user_agent
        
        return selected.user_agent
    
    def get_mobile_user_agents(self) -> List[str]:
        """Get all mobile user agents.
        
        Returns:
            List of mobile user agent strings
        """
        return [
            config.user_agent 
            for config in self.configs 
            if config.device_type in ['Mobile', 'Tablet']
        ]
    
    def generate_variations(self, base_ua: str, count: int = 5) -> List[str]:
        """Generate variations of a user agent string.
        
        This simulates version updates and minor differences.
        
        Args:
            base_ua: Base user agent string
            count: Number of variations to generate
            
        Returns:
            List of user agent variations
        """
        variations = [base_ua]
        
        # Simple version number variations
        for i in range(1, count):
            # Find version numbers and increment them
            import re
            
            # Match version patterns like "91.0.4472.124"
            pattern = r'(\d+)\.(\d+)\.(\d+)\.(\d+)'
            
            def increment_version(match):
                parts = [int(x) for x in match.groups()]
                # Increment minor version
                parts[2] += i
                return '.'.join(str(x) for x in parts)
            
            varied_ua = re.sub(pattern, increment_version, base_ua, count=1)
            if varied_ua != base_ua:
                variations.append(varied_ua)
        
        return variations