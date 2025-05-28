"""
Pydantic models for configuration data structures.

These models define the structure and validation for enterprise
and cloud service configurations.
"""

from datetime import time
from typing import List, Dict, Any, Optional, Literal
# Simplified models without pydantic


class TimeRange:
    """Represents a time range within a day."""
    def __init__(self, start: int, end: int, multiplier: float = 1.0, weight: float = 1.0):
        self.start = start
        self.end = end
        self.multiplier = multiplier
        self.weight = weight


class UserProfile:
    """User behavior profile configuration."""
    def __init__(self, name: str, percentage: float, work_hours_adherence: float,
                 shadow_it_likelihood: float, data_volume_multiplier: float,
                 blocked_attempt_rate: float):
        self.name = name
        self.percentage = percentage
        self.work_hours_adherence = work_hours_adherence
        self.shadow_it_likelihood = shadow_it_likelihood
        self.data_volume_multiplier = data_volume_multiplier
        self.blocked_attempt_rate = blocked_attempt_rate


class NetworkConfig(BaseModel):
    """Network configuration for the enterprise."""
    internal_subnets: List[str]
    egress_ips: List[str]
    proxy_ips: Optional[List[str]] = []
    vpn_subnets: Optional[List[str]] = []


class TrafficConfig(BaseModel):
    """Traffic generation configuration."""
    requests_per_user_per_day: Dict[str, int] = Field(
        default={"mean": 500, "std_dev": 200}
    )
    peak_hours: TimeRange = Field(
        default=TimeRange(start=9, end=17)
    )
    lunch_break: TimeRange = Field(
        default=TimeRange(start=12, end=13, multiplier=0.5)
    )
    after_hours_multiplier: float = Field(default=0.1, ge=0, le=1.0)
    weekend_multiplier: float = Field(default=0.05, ge=0, le=1.0)


class JunkTrafficConfig(BaseModel):
    """Junk traffic configuration for adding noise to logs."""
    enabled: bool = Field(default=True)
    percentage_of_total: float = Field(default=0.3, ge=0, le=0.5)
    requests_per_user_per_day: Dict[str, int] = Field(
        default={"mean": 150, "std_dev": 75}
    )
    categories: Dict[str, float] = Field(
        default={
            "news": 0.25,
            "reference": 0.20,
            "shopping": 0.15,
            "blogs": 0.15,
            "forums": 0.10,
            "misc": 0.15
        }
    )


class EnterpriseConfig(BaseModel):
    """Main enterprise configuration model."""
    enterprise: Dict[str, Any]
    network: NetworkConfig
    users: Dict[str, Any]
    user_profiles: List[UserProfile]
    traffic: TrafficConfig
    shadow_it: Dict[str, Any]
    junk_traffic: Optional[JunkTrafficConfig] = None
    output: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnterpriseConfig":
        """Create EnterpriseConfig from dictionary."""
        # Parse user profiles
        profiles = []
        for profile_data in data.get("user_profiles", []):
            profiles.append(UserProfile(**profile_data))
        
        # Parse junk traffic config if present
        junk_traffic = None
        if "junk_traffic" in data:
            junk_traffic = JunkTrafficConfig(**data["junk_traffic"])
        
        return cls(
            enterprise=data["enterprise"],
            network=NetworkConfig(**data["network"]),
            users=data["users"],
            user_profiles=profiles,
            traffic=TrafficConfig(**data.get("traffic", {})),
            shadow_it=data.get("shadow_it", {}),
            junk_traffic=junk_traffic,
            output=data.get("output", {})
        )


class ServiceNetwork(BaseModel):
    """Network identifiers for a cloud service."""
    domains: List[str]
    ip_ranges: Optional[List[str]] = []
    ports: Optional[List[int]] = []


class TrafficPattern(BaseModel):
    """Traffic patterns for a cloud service."""
    api_endpoints: Optional[List[str]] = []
    web_paths: Optional[List[str]] = []
    websocket_endpoints: Optional[List[str]] = []
    connection_attempts: Optional[List[str]] = []
    protocols: Optional[List[str]] = []
    user_agents: Optional[Dict[str, List[str]]] = {}


class ActivityAction(BaseModel):
    """Individual activity action configuration."""
    weight: float = Field(ge=0, le=1.0)
    avg_size_mb: Optional[float] = None
    size_std_dev: Optional[float] = None
    avg_per_hour: Optional[float] = None
    size_bytes: Optional[int] = None
    avg_duration_seconds: Optional[int] = None
    avg_queries_per_day: Optional[int] = None


class ServiceActivity(BaseModel):
    """Activity simulation parameters for a service."""
    user_adoption_rate: float = Field(ge=0, le=1.0)
    user_attempt_rate: Optional[float] = Field(None, ge=0, le=1.0)
    peak_hours: Optional[Dict[str, TimeRange]] = {}
    actions: Optional[Dict[str, ActivityAction]] = {}
    attempt_patterns: Optional[Dict[str, Any]] = {}
    attempt_hours: Optional[Dict[str, TimeRange]] = {}
    websocket: Optional[Dict[str, Any]] = {}


class SecurityEvents(BaseModel):
    """Security event configuration for a service."""
    block_rate: float = Field(ge=0, le=1.0)
    dlp_triggers: Optional[List[Dict[str, Any]]] = []
    detection_events: Optional[Dict[str, Any]] = {}
    block_actions: Optional[List[Dict[str, Any]]] = []
    alerts: Optional[Dict[str, Any]] = {}
    compliance: Optional[Dict[str, Any]] = {}
    anomalies: Optional[Dict[str, Any]] = {}


class CloudService(BaseModel):
    """Cloud service configuration model."""
    service: Dict[str, Any]
    network: ServiceNetwork
    traffic_patterns: TrafficPattern
    activity: ServiceActivity
    security_events: SecurityEvents
    integrations: Optional[Dict[str, Any]] = {}
    
    @property
    def name(self) -> str:
        """Get service name."""
        return self.service["name"]
    
    @property
    def status(self) -> Literal["sanctioned", "unsanctioned", "blocked"]:
        """Get service status."""
        return self.service["status"]
    
    @property
    def category(self) -> str:
        """Get service category."""
        return self.service["category"]
    
    @property
    def risk_level(self) -> str:
        """Get service risk level."""
        return self.service.get("risk_level", "low")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CloudService":
        """Create CloudService from dictionary."""
        # Parse nested structures
        network = ServiceNetwork(**data["network"])
        traffic_patterns = TrafficPattern(**data.get("traffic_patterns", {}))
        activity = ServiceActivity(**data.get("activity", {}))
        security_events = SecurityEvents(**data.get("security_events", {}))
        
        # Parse actions if present
        if "actions" in data.get("activity", {}):
            actions = {}
            for action_name, action_data in data["activity"]["actions"].items():
                actions[action_name] = ActivityAction(**action_data)
            activity.actions = actions
        
        return cls(
            service=data["service"],
            network=network,
            traffic_patterns=traffic_patterns,
            activity=activity,
            security_events=security_events,
            integrations=data.get("integrations", {})
        )