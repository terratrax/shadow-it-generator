"""
YAML configuration file parser for enterprise and cloud service configs.

This module handles loading and parsing YAML configuration files,
validating their structure, and converting them to internal models.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any
import logging

from .models import EnterpriseConfig, CloudService
from .validators import validate_enterprise_config, validate_service_config


logger = logging.getLogger(__name__)


class ConfigParser:
    """Parser for YAML configuration files."""
    
    def parse_enterprise_config(self, config_path: Path) -> EnterpriseConfig:
        """
        Parse enterprise configuration YAML file.
        
        Args:
            config_path: Path to enterprise.yaml file
            
        Returns:
            Parsed and validated enterprise configuration
            
        Raises:
            ValueError: If configuration is invalid
            FileNotFoundError: If config file doesn't exist
        """
        logger.info(f"Parsing enterprise config from {config_path}")
        
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            
        # Validate configuration
        validate_enterprise_config(data)
        
        # Convert to model
        return EnterpriseConfig.from_dict(data)
    
    def parse_services_directory(self, services_dir: Path) -> List[CloudService]:
        """
        Parse all cloud service YAML files in a directory.
        
        Args:
            services_dir: Directory containing service YAML files
            
        Returns:
            List of parsed cloud service configurations
        """
        logger.info(f"Parsing cloud services from {services_dir}")
        
        services = []
        
        # Find all YAML files
        yaml_files = list(services_dir.glob("*.yaml")) + list(services_dir.glob("*.yml"))
        
        for yaml_file in yaml_files:
            # Skip example files
            if yaml_file.name.endswith('.example'):
                continue
                
            try:
                service = self.parse_service_config(yaml_file)
                services.append(service)
                logger.debug(f"Loaded service: {service.name}")
            except Exception as e:
                logger.warning(f"Failed to parse {yaml_file}: {str(e)}")
                
        logger.info(f"Loaded {len(services)} cloud services")
        return services
    
    def parse_service_config(self, config_path: Path) -> CloudService:
        """
        Parse a single cloud service configuration file.
        
        Args:
            config_path: Path to service YAML file
            
        Returns:
            Parsed cloud service configuration
        """
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            
        # Validate configuration
        validate_service_config(data)
        
        # Convert to model
        return CloudService.from_dict(data)