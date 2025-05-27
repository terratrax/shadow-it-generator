"""
Main log generation engine that orchestrates the entire log generation process.

This module coordinates user simulation, traffic generation, and log formatting
to produce realistic shadow IT network traffic logs.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from ..config.models import EnterpriseConfig, CloudService
from ..generators.activity import ActivityGenerator
from ..formatters.base import LogFormatter
from ..formatters.leef import LEEFFormatter
from ..formatters.cef import CEFFormatter


logger = logging.getLogger(__name__)


class LogGenerationEngine:
    """
    Main engine for generating shadow IT logs.
    
    Coordinates the entire log generation process including user simulation,
    traffic pattern generation, and output formatting.
    """
    
    def __init__(
        self,
        enterprise_config: EnterpriseConfig,
        services: List[CloudService],
        output_dir: Path,
        log_format: str = "leef",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        """
        Initialize the log generation engine.
        
        Args:
            enterprise_config: Enterprise-wide configuration
            services: List of cloud service configurations
            output_dir: Directory to write log files
            log_format: Output format ('leef', 'cef', or 'both')
            start_date: Start date for log generation
            end_date: End date for log generation
        """
        self.enterprise_config = enterprise_config
        self.services = services
        self.output_dir = output_dir
        self.log_format = log_format
        
        # Set default dates if not provided
        self.end_date = end_date or datetime.now()
        self.start_date = start_date or (self.end_date - timedelta(days=30))
        
        # Initialize formatters
        self.formatters = self._init_formatters()
        
        # Initialize activity generator
        self.activity_generator = ActivityGenerator(
            enterprise_config=enterprise_config,
            services=services
        )
        
    def _init_formatters(self) -> List[LogFormatter]:
        """Initialize log formatters based on requested format."""
        formatters = []
        
        if self.log_format in ["leef", "both"]:
            formatters.append(LEEFFormatter(self.output_dir / "leef"))
            
        if self.log_format in ["cef", "both"]:
            formatters.append(CEFFormatter(self.output_dir / "cef"))
            
        return formatters
    
    def generate(self) -> None:
        """
        Generate logs for the specified time period.
        
        This is the main entry point for log generation.
        """
        logger.info(f"Starting log generation from {self.start_date} to {self.end_date}")
        
        # Create output directories
        for formatter in self.formatters:
            formatter.setup()
        
        # Generate user population
        users = self._generate_users()
        logger.info(f"Generated {len(users)} users")
        
        # Generate logs day by day
        current_date = self.start_date
        while current_date <= self.end_date:
            logger.info(f"Generating logs for {current_date.date()}")
            self._generate_daily_logs(users, current_date)
            current_date += timedelta(days=1)
            
        # Finalize formatters
        for formatter in self.formatters:
            formatter.finalize()
            
        logger.info("Log generation complete")
    
    def _generate_users(self) -> List[Dict[str, Any]]:
        """Generate the user population based on enterprise config."""
        # This will be implemented to create user profiles
        # based on the distribution specified in enterprise config
        pass
    
    def _generate_daily_logs(self, users: List[Dict[str, Any]], date: datetime) -> None:
        """Generate logs for a single day."""
        # This will be implemented to generate traffic for each user
        # throughout the day based on their profile and service adoption
        pass