"""Simplified configuration models without pydantic."""

from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml


class EnterpriseConfig:
    """Enterprise configuration."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.enterprise = data.get("enterprise", {})
        self.network = data.get("network", {})
        self.users = data.get("users", {})
        self.user_profiles = data.get("user_profiles", [])
        self.traffic = data.get("traffic", {})
        self.shadow_it = data.get("shadow_it", {})
        self.junk_traffic = data.get("junk_traffic", {})
        self.output = data.get("output", {})
    
    @classmethod
    def from_yaml(cls, path: Path) -> "EnterpriseConfig":
        """Load configuration from YAML file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnterpriseConfig":
        """Create from dictionary."""
        return cls(data)


class CloudService:
    """Cloud service configuration."""
    
    def __init__(self, **kwargs):
        self.service = kwargs.get("service", {})
        self.network = kwargs.get("network", {})
        self.traffic_patterns = kwargs.get("traffic_patterns", {})
        self.activity = kwargs.get("activity", {})
        self.security_events = kwargs.get("security_events", {})
    
    @property
    def name(self) -> str:
        return self.service.get("name", "unknown")
    
    @property
    def status(self) -> str:
        return self.service.get("status", "unsanctioned")
    
    @property
    def category(self) -> str:
        return self.service.get("category", "other")
    
    @property
    def risk_level(self) -> str:
        return self.service.get("risk_level", "low")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CloudService":
        """Create from dictionary."""
        return cls(**data)