"""Service registry for managing cloud services."""

from typing import Dict, List, Optional, Set
from pathlib import Path
import yaml
import logging

from ..models.cloud_service import CloudService

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """Registry for managing cloud service definitions."""
    
    def __init__(self):
        self.services: Dict[str, CloudService] = {}
        self._categories: Set[str] = set()
        self._by_status: Dict[str, List[CloudService]] = {
            "sanctioned": [],
            "unsanctioned": [],
            "blocked": []
        }
    
    def load_from_directory(self, directory: Path) -> None:
        """Load all cloud service definitions from a directory.
        
        Args:
            directory: Path to directory containing YAML service definitions
        """
        yaml_files = list(directory.glob("*.yaml"))
        logger.info(f"Loading {len(yaml_files)} service definitions from {directory}")
        
        for yaml_file in yaml_files:
            try:
                self.load_service(yaml_file)
            except Exception as e:
                logger.error(f"Failed to load service from {yaml_file}: {e}")
    
    def load_service(self, yaml_file: Path) -> CloudService:
        """Load a single service definition from YAML file.
        
        Args:
            yaml_file: Path to YAML file containing service definition
            
        Returns:
            Loaded CloudService instance
        """
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        service = CloudService(**data)
        self.register_service(service)
        return service
    
    def register_service(self, service: CloudService) -> None:
        """Register a cloud service in the registry.
        
        Args:
            service: CloudService instance to register
        """
        self.services[service.name] = service
        self._categories.add(service.category)
        self._by_status[service.status].append(service)
        
        logger.debug(f"Registered service: {service.name} "
                    f"(status={service.status}, category={service.category})")
    
    def get_service(self, name: str) -> Optional[CloudService]:
        """Get a service by name.
        
        Args:
            name: Service name
            
        Returns:
            CloudService instance or None if not found
        """
        return self.services.get(name)
    
    def get_services_by_status(self, status: str) -> List[CloudService]:
        """Get all services with a specific status.
        
        Args:
            status: Service status (sanctioned, unsanctioned, blocked)
            
        Returns:
            List of CloudService instances
        """
        return self._by_status.get(status, [])
    
    def get_services_by_category(self, category: str) -> List[CloudService]:
        """Get all services in a specific category.
        
        Args:
            category: Service category
            
        Returns:
            List of CloudService instances
        """
        return [s for s in self.services.values() if s.category == category]
    
    def get_all_services(self) -> List[CloudService]:
        """Get all registered services.
        
        Returns:
            List of all CloudService instances
        """
        return list(self.services.values())
    
    def get_categories(self) -> Set[str]:
        """Get all unique service categories.
        
        Returns:
            Set of category names
        """
        return self._categories.copy()
    
    def get_sanctioned_services(self) -> List[CloudService]:
        """Get all sanctioned services."""
        return self._by_status["sanctioned"]
    
    def get_unsanctioned_services(self) -> List[CloudService]:
        """Get all unsanctioned services."""
        return self._by_status["unsanctioned"]
    
    def get_blocked_services(self) -> List[CloudService]:
        """Get all blocked services."""
        return self._by_status["blocked"]
    
    def __len__(self) -> int:
        """Get total number of registered services."""
        return len(self.services)
    
    def __repr__(self) -> str:
        """String representation of the registry."""
        return (f"ServiceRegistry("
                f"total={len(self)}, "
                f"sanctioned={len(self._by_status['sanctioned'])}, "
                f"unsanctioned={len(self._by_status['unsanctioned'])}, "
                f"blocked={len(self._by_status['blocked'])})")