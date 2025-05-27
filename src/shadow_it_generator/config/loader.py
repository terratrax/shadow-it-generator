"""Configuration file loading and validation.

This module handles loading YAML configuration files for enterprise
settings and cloud service definitions.
"""

from pathlib import Path
from typing import List, Dict, Any
import yaml
import logging

from .models import EnterpriseConfig, CloudService
from .validator import ConfigValidator


logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and validates configuration files.
    
    This class handles loading YAML configurations from disk and
    converting them to appropriate model objects.
    """
    
    def __init__(self,
                 enterprise_config_path: str = None,
                 services_dir: str = None):
        """Initialize the configuration loader.
        
        Args:
            enterprise_config_path: Path to enterprise config file
            services_dir: Directory containing cloud service configs
        """
        self.enterprise_config_path = enterprise_config_path
        self.services_dir = services_dir
        self.validator = ConfigValidator()
    
    def load_enterprise_config(self) -> EnterpriseConfig:
        """Load and validate enterprise configuration.
        
        Returns:
            Validated EnterpriseConfig object
            
        Raises:
            ValueError: If configuration is invalid
            FileNotFoundError: If config file not found
        """
        if not self.enterprise_config_path:
            raise ValueError("Enterprise config path not specified")
        
        config_path = Path(self.enterprise_config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        logger.info(f"Loading enterprise config from {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Validate configuration
        self.validator.validate_enterprise_config(config_data)
        
        # Convert to model object
        return EnterpriseConfig.from_dict(config_data)
    
    def load_cloud_services(self) -> List[CloudService]:
        """Load all cloud service configurations.
        
        Returns:
            List of validated CloudService objects
            
        Raises:
            ValueError: If any service config is invalid
        """
        if not self.services_dir:
            raise ValueError("Services directory not specified")
        
        services_path = Path(self.services_dir)
        if not services_path.exists():
            raise FileNotFoundError(f"Services directory not found: {services_path}")
        
        services = []
        
        # Load all YAML files in the directory
        for yaml_file in services_path.glob("*.yaml"):
            if yaml_file.name.endswith('.example'):
                continue  # Skip example files
            
            try:
                service = self._load_service_file(yaml_file)
                services.append(service)
            except Exception as e:
                logger.error(f"Failed to load service {yaml_file}: {e}")
                raise
        
        logger.info(f"Loaded {len(services)} cloud service definitions")
        return services
    
    def _load_service_file(self, file_path: Path) -> CloudService:
        """Load a single cloud service configuration file.
        
        Args:
            file_path: Path to the service YAML file
            
        Returns:
            Validated CloudService object
        """
        logger.debug(f"Loading service config from {file_path}")
        
        with open(file_path, 'r') as f:
            service_data = yaml.safe_load(f)
        
        # Validate configuration
        self.validator.validate_service_config(service_data)
        
        # Convert to model object
        return CloudService.from_dict(service_data)
    
    def validate_enterprise_config(self, config_path: str):
        """Validate an enterprise configuration file.
        
        Args:
            config_path: Path to config file to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        self.validator.validate_enterprise_config(config_data)
        logger.info(f"Enterprise config valid: {config_path}")
    
    def validate_service_config(self, config_path: str):
        """Validate a cloud service configuration file.
        
        Args:
            config_path: Path to config file to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        self.validator.validate_service_config(config_data)
        logger.info(f"Service config valid: {config_path}")
    
    def create_example_configs(self, output_dir: Path):
        """Create example configuration files.
        
        Args:
            output_dir: Directory to write example configs
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create example enterprise config
        enterprise_example = self._get_enterprise_example()
        with open(output_dir / 'enterprise.yaml.example', 'w') as f:
            yaml.dump(enterprise_example, f, default_flow_style=False)
        
        # Create example service config
        service_example = self._get_service_example()
        services_dir = output_dir / 'cloud-services'
        services_dir.mkdir(exist_ok=True)
        
        with open(services_dir / 'office365.yaml.example', 'w') as f:
            yaml.dump(service_example, f, default_flow_style=False)
    
    def _get_enterprise_example(self) -> Dict[str, Any]:
        """Get example enterprise configuration.
        
        Returns:
            Dictionary with example configuration
        """
        return {
            'enterprise': {
                'name': 'Acme Corporation',
                'total_users': 5000,
                'domain': 'acme.com'
            },
            'network': {
                'source_ips': ['10.10.0.0/16', '192.168.0.0/16'],
                'proxy_ip': '10.10.1.100'
            },
            'user_behavior': {
                'working_hours': {
                    'start': '08:00',
                    'end': '18:00',
                    'timezone': 'America/New_York'
                },
                'user_profiles': {
                    'normal_users': {
                        'percentage': 70,
                        'avg_services_per_day': 10,
                        'service_variance': 3
                    },
                    'power_users': {
                        'percentage': 20,
                        'avg_services_per_day': 25,
                        'service_variance': 5
                    },
                    'risky_users': {
                        'percentage': 10,
                        'avg_services_per_day': 30,
                        'service_variance': 10,
                        'risky_app_preference': 0.4
                    }
                },
                'activity_patterns': {
                    'peak_hours': [9, 10, 11, 14, 15, 16],
                    'lunch_dip': True,
                    'weekend_activity': 0.1
                }
            },
            'browsers': [
                {
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124',
                    'weight': 0.5
                },
                {
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/91.0.864.59',
                    'weight': 0.3
                },
                {
                    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/14.1.1',
                    'weight': 0.2
                }
            ],
            'output': {
                'format': 'logs/{year}/{month}/{day}/webgateway_{timestamp}.log',
                'rotation': 'hourly',
                'compression': True
            },
            'policies': [
                {
                    'name': 'Default Policy',
                    'id': 'POL001'
                }
            ]
        }
    
    def _get_service_example(self) -> Dict[str, Any]:
        """Get example cloud service configuration.
        
        Returns:
            Dictionary with example configuration
        """
        return {
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
        }