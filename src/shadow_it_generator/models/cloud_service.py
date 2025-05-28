"""Cloud service model."""

from typing import Dict, Any, List, Optional


class CloudService:
    """Cloud service configuration."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.service = data.get("service", {})
        self.network = data.get("network", {})
        self.traffic_patterns = data.get("traffic_patterns", {})
        self.activity = data.get("activity", {})
        self.security_events = data.get("security_events", {})
    
    @property
    def name(self) -> str:
        """Get service name."""
        return self.service.get("name", "unknown")
    
    @property
    def status(self) -> str:
        """Get service status."""
        return self.service.get("status", "unsanctioned")
    
    @property
    def category(self) -> str:
        """Get service category."""
        return self.service.get("category", "other")
    
    @property
    def risk_level(self) -> str:
        """Get service risk level."""
        return self.service.get("risk_level", "low")
    
    @property
    def domains(self) -> List[str]:
        """Get service domains."""
        return self.network.get("domains", [])
    
    @property
    def user_adoption_rate(self) -> float:
        """Get user adoption rate."""
        return self.activity.get("user_adoption_rate", 0.1)
    
    @property
    def block_rate(self) -> float:
        """Get block rate."""
        return self.security_events.get("block_rate", 0.0)