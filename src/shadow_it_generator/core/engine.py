"""
Main log generation engine that orchestrates the entire log generation process.

This module coordinates user simulation, traffic generation, and log formatting
to produce realistic shadow IT network traffic logs.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import uuid
import random

from ..models.config import EnterpriseConfig
from ..models.cloud_service import CloudService
from ..generators.activity import ActivityGenerator
from ..generators.junk_traffic import JunkTrafficGenerator
from ..formatters.base import LogFormatter, LogEvent
from ..formatters.leef import LEEFFormatter
from ..formatters.cef import CEFFormatter
from ..utils.ip_generator import IPGenerator
from ..utils.user_generator import UserGenerator
from ..core.user import User


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
        
        # Initialize generators
        self.ip_generator = IPGenerator(
            internal_subnets=enterprise_config.network.get('internal_subnets', []),
            egress_ips=enterprise_config.network.get('egress_ips', []),
            proxy_ips=enterprise_config.network.get('proxy_ips', []),
            vpn_subnets=enterprise_config.network.get('vpn_subnets', [])
        )
        
        self.user_generator = UserGenerator(
            enterprise_domain=enterprise_config.enterprise['domain']
        )
        
        # Initialize junk traffic generator if enabled
        if enterprise_config.junk_traffic and enterprise_config.junk_traffic.get('enabled', False):
            self.junk_generator = JunkTrafficGenerator(
                junk_config=enterprise_config.junk_traffic,
                ip_generator=self.ip_generator,
                enterprise_domain=enterprise_config.enterprise['domain']
            )
        else:
            self.junk_generator = None
        
        # Initialize activity generator
        self.activity_generator = ActivityGenerator(
            enterprise_config=enterprise_config,
            services=services,
            ip_generator=self.ip_generator,
            junk_generator=self.junk_generator
        )
        
        # User cache
        self.users: List[User] = []
        
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
    
    def _generate_users(self) -> List[User]:
        """Generate the user population based on enterprise config."""
        if self.users:  # Already generated
            return self.users
        
        total_users = self.enterprise_config.users['total_count']
        logger.info(f"Generating {total_users} users")
        
        # Generate user identities
        user_data = self.user_generator.generate_users(total_users)
        
        # Create User objects with profiles
        users = []
        user_id = 1
        
        for profile in self.enterprise_config.user_profiles:
            # Calculate number of users for this profile
            profile_count = int(total_users * profile.get('percentage', 0.1))
            
            for i in range(profile_count):
                if user_id > len(user_data):
                    break
                
                user_info = user_data[user_id - 1]
                
                # Create user with profile
                user = User(
                    id=str(user_id),
                    email=user_info['email'],
                    username=user_info['username'],
                    full_name=user_info['full_name'],
                    profile=profile,
                    source_ip=self.ip_generator.generate_internal_ip(),
                    locale=user_info['locale']
                )
                
                # Assign services to user
                user.assign_services(self.services)
                
                users.append(user)
                user_id += 1
        
        self.users = users
        logger.info(f"Generated {len(users)} users with service assignments")
        return users
    
    def _generate_daily_logs(self, users: List[User], date: datetime) -> None:
        """Generate logs for a single day."""
        # Process hour by hour
        current_time = datetime.combine(date.date(), datetime.min.time())
        current_time = current_time.replace(tzinfo=date.tzinfo)
        
        for hour in range(24):
            hour_start = current_time + timedelta(hours=hour)
            logger.debug(f"Generating logs for {hour_start}")
            
            # Generate user sessions for this hour
            user_sessions = self.activity_generator.generate_hourly_activity(users, hour_start)
            
            # Process each user's sessions
            for user_id, sessions in user_sessions.items():
                user = next(u for u in users if u.id == user_id)
                
                for session in sessions:
                    # Generate requests for the session
                    requests = session.generate_requests()
                    
                    # Convert requests to log events
                    for request in requests:
                        log_event = self._create_log_event(user, session, request)
                        
                        # Write to all formatters
                        for formatter in self.formatters:
                            formatter.write_event(log_event)
                
                # Generate junk traffic for active users
                if self.junk_generator and self.activity_generator.should_generate_junk_traffic(user, hour_start):
                    junk_events = self._generate_user_junk_traffic(user, hour_start)
                    for event in junk_events:
                        for formatter in self.formatters:
                            formatter.write_event(event)
    
    def _create_log_event(self, user: User, session: Any, request: Dict[str, Any]) -> LogEvent:
        """Convert a session request to a log event."""
        # Determine destination based on service
        if session.service.network.ip_ranges:
            dest_ip = self.ip_generator.generate_destination_ip(
                session.service.network.ip_ranges
            )
        else:
            dest_ip = self.ip_generator.generate_destination_ip()
        
        # Build URL
        domain = random.choice(session.service.network.domains)
        # Remove wildcards from domain
        domain = domain.replace('*.', '')
        url = f"https://{domain}{request['path']}"
        
        # Determine action
        if request.get('type') == 'blocked' or request.get('status_code') == 403:
            action = 'blocked'
        else:
            action = 'allowed'
        
        # Create log event
        return LogEvent(
            timestamp=request['timestamp'],
            source_ip=session.source_ip,
            destination_ip=dest_ip,
            source_port=self.ip_generator.generate_source_port(),
            destination_port=443,
            username=user.username,
            user_domain=self.enterprise_config.enterprise['domain'],
            url=url,
            method=request['method'],
            status_code=request['status_code'],
            bytes_sent=request.get('bytes_sent', 0),
            bytes_received=request.get('bytes_received', 0),
            duration_ms=request['duration_ms'],
            user_agent=session.user_agent,
            action=action,
            category=session.service.category,
            risk_level=session.service.risk_level,
            service_name=session.service.name,
            protocol='https',
            additional_fields={
                'session_id': session.id,
                'request_type': request.get('type', 'unknown'),
                'block_reason': request.get('block_reason')
            } if request.get('block_reason') else None
        )
    
    def _generate_user_junk_traffic(self, user: User, hour_start: datetime) -> List[LogEvent]:
        """Generate junk traffic events for a user during an hour."""
        hour_end = hour_start + timedelta(hours=1)
        
        return self.junk_generator.generate_user_junk_events(
            user_email=user.email,
            source_ip=user.source_ip,
            start_time=hour_start,
            end_time=hour_end,
            user_agent=self.activity_generator._get_desktop_user_agent()
        )


# Alias for compatibility
LogGeneratorEngine = LogGenerationEngine