"""Configuration validation logic.

This module provides validation for enterprise and cloud service
configuration files to ensure they meet requirements.
"""

from typing import Dict, Any, List
import ipaddress
import re


class ConfigValidator:
    """Validates configuration data for correctness.
    
    This class provides methods to validate both enterprise and
    cloud service configurations before they are loaded.
    """
    
    def validate_enterprise_config(self, config: Dict[str, Any]):
        """Validate enterprise configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Check required top-level keys
        required_keys = ['enterprise', 'network', 'user_behavior', 
                        'browsers', 'output', 'policies']
        self._check_required_keys(config, required_keys, "enterprise config")
        
        # Validate enterprise section
        self._validate_enterprise(config['enterprise'])
        
        # Validate network section
        self._validate_network(config['network'])
        
        # Validate user behavior
        self._validate_user_behavior(config['user_behavior'])
        
        # Validate browsers
        self._validate_browsers(config['browsers'])
        
        # Validate output config
        self._validate_output(config['output'])
        
        # Validate policies
        self._validate_policies(config['policies'])
    
    def validate_service_config(self, config: Dict[str, Any]):
        """Validate cloud service configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Check required top-level keys
        required_keys = ['service', 'traffic', 'access', 'endpoints']
        self._check_required_keys(config, required_keys, "service config")
        
        # Validate service info
        self._validate_service_info(config['service'])
        
        # Validate traffic patterns
        self._validate_traffic(config['traffic'])
        
        # Validate access control
        self._validate_access(config['access'])
        
        # Validate endpoints
        self._validate_endpoints(config['endpoints'])
    
    def _check_required_keys(self, data: Dict, keys: List[str], context: str):
        """Check that all required keys are present.
        
        Args:
            data: Dictionary to check
            keys: Required keys
            context: Context for error messages
            
        Raises:
            ValueError: If required keys are missing
        """
        missing = [k for k in keys if k not in data]
        if missing:
            raise ValueError(f"Missing required keys in {context}: {missing}")
    
    def _validate_enterprise(self, enterprise: Dict[str, Any]):
        """Validate enterprise section."""
        required = ['name', 'total_users', 'domain']
        self._check_required_keys(enterprise, required, "enterprise")
        
        if not isinstance(enterprise['total_users'], int) or enterprise['total_users'] <= 0:
            raise ValueError("total_users must be a positive integer")
        
        if not self._is_valid_domain(enterprise['domain']):
            raise ValueError(f"Invalid domain: {enterprise['domain']}")
    
    def _validate_network(self, network: Dict[str, Any]):
        """Validate network configuration."""
        required = ['source_ips']
        self._check_required_keys(network, required, "network")
        
        # Validate CIDR ranges
        for cidr in network['source_ips']:
            try:
                ipaddress.ip_network(cidr)
            except ValueError:
                raise ValueError(f"Invalid CIDR range: {cidr}")
        
        # Validate proxy IP if present
        if 'proxy_ip' in network and network['proxy_ip']:
            try:
                ipaddress.ip_address(network['proxy_ip'])
            except ValueError:
                raise ValueError(f"Invalid proxy IP: {network['proxy_ip']}")
    
    def _validate_user_behavior(self, behavior: Dict[str, Any]):
        """Validate user behavior configuration."""
        required = ['working_hours', 'user_profiles', 'activity_patterns']
        self._check_required_keys(behavior, required, "user_behavior")
        
        # Validate working hours
        hours = behavior['working_hours']
        required_hours = ['start', 'end', 'timezone']
        self._check_required_keys(hours, required_hours, "working_hours")
        
        # Validate time format
        time_pattern = re.compile(r'^\d{2}:\d{2}$')
        if not time_pattern.match(hours['start']) or not time_pattern.match(hours['end']):
            raise ValueError("Working hours must be in HH:MM format")
        
        # Validate user profiles
        profiles = behavior['user_profiles']
        total_percentage = 0
        
        for profile_type in ['normal_users', 'power_users', 'risky_users']:
            if profile_type not in profiles:
                raise ValueError(f"Missing user profile: {profile_type}")
            
            profile = profiles[profile_type]
            self._validate_user_profile(profile, profile_type)
            total_percentage += profile['percentage']
        
        if total_percentage != 100:
            raise ValueError(f"User profile percentages must sum to 100, got {total_percentage}")
        
        # Validate activity patterns
        patterns = behavior['activity_patterns']
        required_patterns = ['peak_hours', 'lunch_dip', 'weekend_activity']
        self._check_required_keys(patterns, required_patterns, "activity_patterns")
        
        # Validate peak hours
        for hour in patterns['peak_hours']:
            if not isinstance(hour, int) or hour < 0 or hour > 23:
                raise ValueError(f"Invalid peak hour: {hour}")
    
    def _validate_user_profile(self, profile: Dict[str, Any], name: str):
        """Validate a user profile."""
        required = ['percentage', 'avg_services_per_day', 'service_variance']
        self._check_required_keys(profile, required, f"user profile {name}")
        
        if not 0 <= profile['percentage'] <= 100:
            raise ValueError(f"Invalid percentage for {name}: {profile['percentage']}")
        
        if profile['avg_services_per_day'] <= 0:
            raise ValueError(f"avg_services_per_day must be positive for {name}")
        
        if name == 'risky_users' and 'risky_app_preference' in profile:
            if not 0 <= profile['risky_app_preference'] <= 1:
                raise ValueError("risky_app_preference must be between 0 and 1")
    
    def _validate_browsers(self, browsers: List[Dict[str, Any]]):
        """Validate browser configurations."""
        if not browsers:
            raise ValueError("At least one browser must be configured")
        
        total_weight = 0
        
        for i, browser in enumerate(browsers):
            required = ['user_agent', 'weight']
            self._check_required_keys(browser, required, f"browser {i}")
            
            if not 0 < browser['weight'] <= 1:
                raise ValueError(f"Browser weight must be between 0 and 1: {browser['weight']}")
            
            total_weight += browser['weight']
        
        # Allow small floating point errors
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Browser weights must sum to 1.0, got {total_weight}")
    
    def _validate_output(self, output: Dict[str, Any]):
        """Validate output configuration."""
        required = ['format', 'rotation', 'compression']
        self._check_required_keys(output, required, "output")
        
        valid_rotations = ['hourly', 'daily']
        if output['rotation'] not in valid_rotations:
            raise ValueError(f"Invalid rotation: {output['rotation']}")
    
    def _validate_policies(self, policies: List[Dict[str, Any]]):
        """Validate policy configurations."""
        if not policies:
            raise ValueError("At least one policy must be configured")
        
        for i, policy in enumerate(policies):
            required = ['name', 'id']
            self._check_required_keys(policy, required, f"policy {i}")
    
    def _validate_service_info(self, service: Dict[str, Any]):
        """Validate service information."""
        required = ['name', 'hostname', 'category']
        self._check_required_keys(service, required, "service")
        
        # Validate hostname format
        if not self._is_valid_hostname(service['hostname']):
            raise ValueError(f"Invalid hostname: {service['hostname']}")
    
    def _validate_traffic(self, traffic: Dict[str, Any]):
        """Validate traffic patterns."""
        required = ['avg_bytes_per_session', 'bytes_std_deviation',
                   'avg_requests_per_session', 'requests_std_deviation']
        self._check_required_keys(traffic, required, "traffic")
        
        # All values should be positive
        for key, value in traffic.items():
            if not isinstance(value, (int, float)) or value <= 0:
                raise ValueError(f"{key} must be a positive number")
    
    def _validate_access(self, access: Dict[str, Any]):
        """Validate access control."""
        required = ['allowed']
        self._check_required_keys(access, required, "access")
        
        if not isinstance(access['allowed'], bool):
            raise ValueError("allowed must be a boolean")
        
        # If blocked, should have a reason
        if not access['allowed'] and not access.get('block_reason'):
            raise ValueError("block_reason required when allowed is false")
    
    def _validate_endpoints(self, endpoints: List[Dict[str, Any]]):
        """Validate endpoint configurations."""
        if not endpoints:
            raise ValueError("At least one endpoint must be configured")
        
        total_weight = 0
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        
        for i, endpoint in enumerate(endpoints):
            required = ['path', 'method', 'weight', 'is_api']
            self._check_required_keys(endpoint, required, f"endpoint {i}")
            
            if endpoint['method'] not in valid_methods:
                raise ValueError(f"Invalid HTTP method: {endpoint['method']}")
            
            if not 0 < endpoint['weight'] <= 1:
                raise ValueError(f"Endpoint weight must be between 0 and 1: {endpoint['weight']}")
            
            if not isinstance(endpoint['is_api'], bool):
                raise ValueError("is_api must be a boolean")
            
            total_weight += endpoint['weight']
        
        # Allow small floating point errors
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Endpoint weights must sum to 1.0, got {total_weight}")
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Check if a domain is valid."""
        pattern = re.compile(
            r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*'
            r'[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
        )
        return bool(pattern.match(domain))
    
    def _is_valid_hostname(self, hostname: str) -> bool:
        """Check if a hostname is valid."""
        # Same as domain validation
        return self._is_valid_domain(hostname)