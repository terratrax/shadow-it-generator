"""Configuration models for Shadow IT Generator."""

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
    
    def get_user_count(self) -> int:
        """Get total number of users."""
        return self.users.get("total_count", 1000)
    
    def get_domain(self) -> str:
        """Get enterprise domain."""
        return self.enterprise.get("domain", "example.com")
    
    def get_output_format(self) -> str:
        """Get output format."""
        return self.output.get("format", {}).get("type", "leef")