"""
Validators for configuration files.

This module provides validation functions to ensure configuration
files have the required structure and valid values.
"""

from typing import Dict, Any, List
import ipaddress
import re


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


def validate_enterprise_config(config: Dict[str, Any]) -> None:
    """
    Validate enterprise configuration structure.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ConfigValidationError: If validation fails
    """
    required_sections = ["enterprise", "network", "users", "user_profiles"]
    
    # Check required sections
    for section in required_sections:
        if section not in config:
            raise ConfigValidationError(f"Missing required section: {section}")
    
    # Validate enterprise section
    enterprise = config["enterprise"]
    if "name" not in enterprise:
        raise ConfigValidationError("Enterprise name is required")
    if "domain" not in enterprise:
        raise ConfigValidationError("Enterprise domain is required")
    
    # Validate network section
    network = config["network"]
    if "internal_subnets" not in network:
        raise ConfigValidationError("internal_subnets is required in network section")
    if "egress_ips" not in network:
        raise ConfigValidationError("egress_ips is required in network section")
    
    # Validate IP addresses and subnets
    for subnet in network["internal_subnets"]:
        try:
            ipaddress.ip_network(subnet)
        except ValueError:
            raise ConfigValidationError(f"Invalid subnet: {subnet}")
    
    for ip in network["egress_ips"]:
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            raise ConfigValidationError(f"Invalid IP address: {ip}")
    
    # Validate users section
    users = config["users"]
    if "total_count" not in users:
        raise ConfigValidationError("total_count is required in users section")
    if not isinstance(users["total_count"], int) or users["total_count"] <= 0:
        raise ConfigValidationError("total_count must be a positive integer")
    
    # Validate user profiles
    profiles = config["user_profiles"]
    if not profiles:
        raise ConfigValidationError("At least one user profile is required")
    
    total_percentage = 0
    for profile in profiles:
        if "name" not in profile:
            raise ConfigValidationError("Profile name is required")
        if "percentage" not in profile:
            raise ConfigValidationError(f"Percentage is required for profile {profile.get('name', 'unknown')}")
        total_percentage += profile["percentage"]
    
    if abs(total_percentage - 1.0) > 0.01:
        raise ConfigValidationError(f"User profile percentages must sum to 1.0, got {total_percentage}")


def validate_service_config(config: Dict[str, Any]) -> None:
    """
    Validate cloud service configuration structure.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ConfigValidationError: If validation fails
    """
    required_sections = ["service", "network"]
    
    # Check required sections
    for section in required_sections:
        if section not in config:
            raise ConfigValidationError(f"Missing required section: {section}")
    
    # Validate service section
    service = config["service"]
    required_service_fields = ["name", "category", "status"]
    for field in required_service_fields:
        if field not in service:
            raise ConfigValidationError(f"Missing required field in service: {field}")
    
    # Validate status
    valid_statuses = ["sanctioned", "unsanctioned", "blocked"]
    if service["status"] not in valid_statuses:
        raise ConfigValidationError(f"Invalid service status: {service['status']}. Must be one of {valid_statuses}")
    
    # Validate network section
    network = config["network"]
    if "domains" not in network:
        raise ConfigValidationError("domains is required in network section")
    if not network["domains"]:
        raise ConfigValidationError("At least one domain is required")
    
    # Validate domains
    for domain in network["domains"]:
        if not is_valid_domain_pattern(domain):
            raise ConfigValidationError(f"Invalid domain pattern: {domain}")
    
    # Validate IP ranges if present
    if "ip_ranges" in network:
        for ip_range in network["ip_ranges"]:
            try:
                ipaddress.ip_network(ip_range)
            except ValueError:
                raise ConfigValidationError(f"Invalid IP range: {ip_range}")
    
    # Validate activity section if present
    if "activity" in config:
        activity = config["activity"]
        if "user_adoption_rate" in activity:
            rate = activity["user_adoption_rate"]
            if not isinstance(rate, (int, float)) or rate < 0 or rate > 1:
                raise ConfigValidationError("user_adoption_rate must be between 0 and 1")
    
    # Validate security events if present
    if "security_events" in config:
        security = config["security_events"]
        if "block_rate" in security:
            rate = security["block_rate"]
            if not isinstance(rate, (int, float)) or rate < 0 or rate > 1:
                raise ConfigValidationError("block_rate must be between 0 and 1")


def is_valid_domain_pattern(domain: str) -> bool:
    """
    Check if a domain pattern is valid.
    
    Supports wildcards like *.example.com
    
    Args:
        domain: Domain pattern to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Remove wildcard for validation
    domain_to_check = domain.replace("*.", "")
    
    # Basic domain validation regex
    domain_regex = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    )
    
    return bool(domain_regex.match(domain_to_check))