"""Cloud service management.

This module provides utilities for managing and categorizing cloud services,
including loading predefined services and selecting services based on
various criteria.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import random
import logging

from ..config.models import CloudService
from .categories import ServiceCategory


logger = logging.getLogger(__name__)


class ServiceManager:
    """Manages cloud service definitions and selection.
    
    This class provides methods for loading, categorizing, and selecting
    cloud services based on various criteria like user type and risk level.
    """
    
    def __init__(self, services: List[CloudService]):
        """Initialize the service manager.
        
        Args:
            services: List of available cloud services
        """
        self.services = services
        self._categorize_services()
    
    def _categorize_services(self):
        """Organize services by various attributes for efficient selection."""
        # Group by category
        self.by_category: Dict[str, List[CloudService]] = {}
        for service in self.services:
            category = service.category
            if category not in self.by_category:
                self.by_category[category] = []
            self.by_category[category].append(service)
        
        # Group by access status
        # Group by status (sanctioned vs unsanctioned)
        self.sanctioned = [s for s in self.services if s.status == 'sanctioned']
        self.blocked = [s for s in self.services if s.status != 'sanctioned']
        
        # Create risk categories
        self.low_risk = []
        self.medium_risk = []
        self.high_risk = []
        
        for service in self.services:
            risk_level = self._calculate_risk_level(service)
            if risk_level == 'low':
                self.low_risk.append(service)
            elif risk_level == 'medium':
                self.medium_risk.append(service)
            else:
                self.high_risk.append(service)
    
    def _calculate_risk_level(self, service: CloudService) -> str:
        """Calculate risk level for a service.
        
        Args:
            service: Service to evaluate
            
        Returns:
            Risk level: 'low', 'medium', or 'high'
        """
        # Unsanctioned services are automatically high risk
        if service.status != 'sanctioned':
            return 'high'
        
        # Categorize based on service category
        category = service.category.lower()
        
        high_risk_categories = [
            'file sharing', 'personal storage', 'social media',
            'personal email', 'vpn', 'proxy', 'torrent'
        ]
        
        medium_risk_categories = [
            'collaboration', 'messaging', 'video conferencing',
            'development tools', 'cloud storage'
        ]
        
        if any(cat in category for cat in high_risk_categories):
            return 'high'
        elif any(cat in category for cat in medium_risk_categories):
            return 'medium'
        else:
            return 'low'
    
    def select_services_for_user(self,
                                user_type: str,
                                count: int,
                                prefer_risky: bool = False) -> List[CloudService]:
        """Select appropriate services for a user type.
        
        Args:
            user_type: Type of user ('normal', 'power', 'risky')
            count: Number of services to select
            prefer_risky: Whether to prefer risky services
            
        Returns:
            List of selected cloud services
        """
        if user_type == 'risky' or prefer_risky:
            # Risky users access more blocked/high-risk services
            pool = self.services  # All services
            weights = [3 if s in self.high_risk else 1 for s in pool]
        elif user_type == 'power':
            # Power users access mix of services
            pool = self.sanctioned + random.sample(
                self.high_risk, 
                min(len(self.high_risk), count // 4)
            )
            weights = None
        else:
            # Normal users mostly access sanctioned services
            pool = self.sanctioned + random.sample(
                self.medium_risk,
                min(len(self.medium_risk), count // 10)
            )
            weights = None
        
        # Ensure we don't select more than available
        count = min(count, len(pool))
        
        if weights:
            selected = random.choices(pool, weights=weights, k=count)
            # Remove duplicates while preserving general distribution
            selected = list(dict.fromkeys(selected))
            
            # If we need more due to duplicates, add more
            while len(selected) < count and len(selected) < len(pool):
                additional = random.choices(pool, weights=weights, k=count-len(selected))
                for service in additional:
                    if service not in selected:
                        selected.append(service)
        else:
            selected = random.sample(pool, count)
        
        return selected
    
    def get_services_by_category(self, category: str) -> List[CloudService]:
        """Get all services in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of services in that category
        """
        return self.by_category.get(category, [])
    
    def get_popular_services(self, count: int = 10) -> List[CloudService]:
        """Get the most popular/common services.
        
        Args:
            count: Number of services to return
            
        Returns:
            List of popular services
        """
        # Define popular services by name
        popular_names = [
            'Microsoft Office 365', 'Google Workspace', 'Salesforce',
            'Slack', 'Zoom', 'Dropbox', 'Box', 'GitHub', 'AWS',
            'Microsoft Azure', 'ServiceNow', 'Workday', 'DocuSign'
        ]
        
        popular = []
        for name in popular_names:
            for service in self.services:
                if service.name == name:
                    popular.append(service)
                    break
        
        return popular[:count]
    
    @staticmethod
    def create_default_services() -> List[Dict[str, Any]]:
        """Create a set of default cloud service definitions.
        
        Returns:
            List of service configuration dictionaries
        """
        # This would typically load from YAML files
        # For now, return a few examples
        return [
            {
                'service': {
                    'name': 'Microsoft Office 365',
                    'hostname': 'outlook.office365.com',
                    'category': 'Business'
                },
                'traffic': {
                    'avg_bytes_per_session': 1048576,
                    'bytes_std_deviation': 524288,
                    'avg_requests_per_session': 50,
                    'requests_std_deviation': 20
                },
                'access': {
                    'allowed': True,
                    'block_reason': ''
                },
                'endpoints': [
                    {
                        'path': '/api/v2/messages',
                        'method': 'GET',
                        'weight': 0.4,
                        'is_api': True
                    },
                    {
                        'path': '/owa/',
                        'method': 'GET',
                        'weight': 0.3,
                        'is_api': False
                    },
                    {
                        'path': '/api/v2/attachments',
                        'method': 'POST',
                        'weight': 0.2,
                        'is_api': True
                    },
                    {
                        'path': '/api/v2/calendar',
                        'method': 'GET',
                        'weight': 0.1,
                        'is_api': True
                    }
                ]
            },
            # Add more default services here
        ]