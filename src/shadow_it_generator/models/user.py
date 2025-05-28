"""User model."""

from typing import List, Set, Dict, Any
import random


class User:
    """Represents an enterprise user."""
    
    def __init__(self, user_id: int, domain: str, profile: Dict[str, Any]):
        self.id = user_id
        self.domain = domain
        self.profile = profile
        self.username = f"user{user_id}"
        self.email = f"{self.username}@{domain}"
        self.assigned_services: Set[str] = set()
        self.ip_address = self._generate_ip()
    
    def _generate_ip(self) -> str:
        """Generate a random internal IP address."""
        return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    
    def assign_services(self, services: List[Any]) -> None:
        """Assign services to user based on profile."""
        for service in services:
            # Simple adoption logic
            adoption_rate = service.user_adoption_rate
            if service.status == "sanctioned":
                adoption_rate *= 1.2
            elif service.status == "blocked":
                adoption_rate *= 0.1
            
            if random.random() < adoption_rate:
                self.assigned_services.add(service.name)
    
    def uses_service(self, service_name: str) -> bool:
        """Check if user uses a service."""
        return service_name in self.assigned_services