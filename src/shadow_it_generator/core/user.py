"""User generation and management.

This module handles the creation and management of synthetic users with
different behavior profiles (normal, power, risky).
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum
import random
import logging

from faker import Faker
from ..config.models import EnterpriseConfig, UserProfile


logger = logging.getLogger(__name__)


class UserType(Enum):
    """User behavior profile types."""
    NORMAL = 'normal'
    POWER = 'power'
    RISKY = 'risky'


@dataclass
class User:
    """Represents a synthetic enterprise user.
    
    Attributes:
        user_id: Unique identifier
        username: Email-format username
        full_name: User's full name
        department: Department name
        user_type: Behavior profile type
        source_ip: Assigned source IP address
        preferred_services: List of preferred cloud services
        risk_score: Risk level (0-100)
    """
    user_id: str
    username: str
    full_name: str
    department: str
    user_type: UserType
    source_ip: str
    preferred_services: List[str]
    risk_score: int


class UserManager:
    """Manages the generation and behavior of synthetic users.
    
    This class creates a realistic population of enterprise users with
    varying behavior profiles and manages their characteristics.
    """
    
    def __init__(self, enterprise_config: EnterpriseConfig):
        """Initialize the user manager.
        
        Args:
            enterprise_config: Enterprise-wide configuration
        """
        self.config = enterprise_config
        self.faker = Faker()
        self.departments = [
            'Sales', 'Marketing', 'Engineering', 'HR', 'Finance',
            'IT', 'Legal', 'Operations', 'Customer Service', 'R&D'
        ]
    
    def generate_users(self) -> List[User]:
        """Generate the complete user population.
        
        Returns:
            List of User objects representing the enterprise population
        """
        users = []
        total_users = self.config.total_users
        
        # Calculate user counts by type
        user_counts = self._calculate_user_distribution(total_users)
        
        # Generate users for each type
        for user_type, count in user_counts.items():
            users.extend(self._generate_user_batch(user_type, count))
        
        logger.info(f"Generated users - Normal: {user_counts[UserType.NORMAL]}, "
                   f"Power: {user_counts[UserType.POWER]}, "
                   f"Risky: {user_counts[UserType.RISKY]}")
        
        return users
    
    def _calculate_user_distribution(self, total: int) -> Dict[UserType, int]:
        """Calculate number of users for each profile type.
        
        Args:
            total: Total number of users
            
        Returns:
            Dictionary mapping user type to count
        """
        profiles = self.config.user_profiles
        
        return {
            UserType.NORMAL: int(total * profiles.normal_users.percentage / 100),
            UserType.POWER: int(total * profiles.power_users.percentage / 100),
            UserType.RISKY: int(total * profiles.risky_users.percentage / 100)
        }
    
    def _generate_user_batch(self, user_type: UserType, count: int) -> List[User]:
        """Generate a batch of users of a specific type.
        
        Args:
            user_type: Type of users to generate
            count: Number of users to generate
            
        Returns:
            List of generated User objects
        """
        users = []
        
        for i in range(count):
            user = self._create_user(user_type, i)
            users.append(user)
        
        return users
    
    def _create_user(self, user_type: UserType, index: int) -> User:
        """Create a single user with appropriate characteristics.
        
        Args:
            user_type: Type of user to create
            index: User index for ID generation
            
        Returns:
            Generated User object
        """
        # Generate basic user info
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        username = f"{first_name.lower()}.{last_name.lower()}@{self.config.domain}"
        
        # Assign characteristics based on user type
        if user_type == UserType.RISKY:
            risk_score = random.randint(70, 100)
        elif user_type == UserType.POWER:
            risk_score = random.randint(30, 70)
        else:
            risk_score = random.randint(0, 30)
        
        return User(
            user_id=f"USR{user_type.value.upper()}{index:05d}",
            username=username,
            full_name=f"{first_name} {last_name}",
            department=random.choice(self.departments),
            user_type=user_type,
            source_ip=self._generate_source_ip(),
            preferred_services=[],  # Will be populated later
            risk_score=risk_score
        )
    
    def _generate_source_ip(self) -> str:
        """Generate a source IP address from configured ranges.
        
        Returns:
            Generated IP address string
        """
        # TODO: Implement IP generation from CIDR ranges
        # For now, return a placeholder
        return "10.10.1.100"
    
    def assign_service_preferences(self, users: List[User], services: List[Any]):
        """Assign preferred cloud services to users based on their profile.
        
        Args:
            users: List of users to assign preferences to
            services: Available cloud services
        """
        # TODO: Implement service preference assignment
        # Consider user type, department, and service categories
        pass