"""
Activity generation for users and services.

This module orchestrates the generation of user activities, sessions,
and requests based on configured patterns.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging
import random
import uuid

from ..config.models import EnterpriseConfig, CloudService
from ..core.user import User
from ..core.session import Session
from ..utils.time_utils import get_activity_multiplier, distribute_events_naturally
from .junk_traffic import JunkTrafficGenerator


logger = logging.getLogger(__name__)


class ActivityGenerator:
    """
    Generates user activity patterns and sessions.
    
    Coordinates between users, services, and time to create
    realistic activity patterns.
    """
    
    def __init__(
        self,
        enterprise_config: EnterpriseConfig,
        services: List[CloudService],
        ip_generator: Any,
        junk_generator: JunkTrafficGenerator
    ):
        """
        Initialize the activity generator.
        
        Args:
            enterprise_config: Enterprise configuration
            services: List of available cloud services
            ip_generator: IP address generator
            junk_generator: Junk traffic generator
        """
        self.enterprise_config = enterprise_config
        self.services = services
        self.ip_generator = ip_generator
        self.junk_generator = junk_generator
        
        # Create service lookup
        self.service_map = {service.name: service for service in services}
        
        # User agent pool
        self.user_agents = self._build_user_agent_pool()
    
    def _build_user_agent_pool(self) -> List[Tuple[str, float]]:
        """Build pool of user agents from enterprise config."""
        # Default user agents if not configured
        default_agents = [
            ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0", 0.45),
            ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.0.0", 0.25),
            ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15", 0.15),
            ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Firefox/121.0", 0.15)
        ]
        
        # TODO: Parse from enterprise config when available
        return default_agents
    
    def generate_user_activity(
        self,
        user: User,
        start_time: datetime,
        end_time: datetime
    ) -> List[Session]:
        """
        Generate all activity for a user in a time period.
        
        Args:
            user: The user to generate activity for
            start_time: Start of period
            end_time: End of period
            
        Returns:
            List of sessions
        """
        sessions = []
        
        # Get activity level for this period
        activity_level = user.get_activity_level(start_time)
        
        if activity_level < 0.1:
            return sessions  # No activity
        
        # Determine which services to use
        services_to_use = user.get_services_for_hour(start_time)
        
        if not services_to_use:
            return sessions
        
        # Generate sessions for each service
        for service_name in services_to_use:
            service = self.service_map.get(service_name)
            if not service:
                continue
            
            # Determine number of sessions for this service
            if service.status == "blocked":
                # Blocked services have fewer, shorter sessions
                num_sessions = 1 if random.random() < 0.3 else 0
            else:
                # Normal services
                base_sessions = 1
                if user.profile.name == "power_user":
                    base_sessions = random.randint(1, 3)
                elif user.profile.name == "risky":
                    base_sessions = random.randint(1, 2)
                
                num_sessions = int(base_sessions * activity_level)
            
            # Generate session times
            session_times = distribute_events_naturally(
                start_time,
                end_time,
                num_sessions,
                burst_probability=0.3
            )
            
            # Create sessions
            for session_time in session_times:
                session = self._create_session(user, service, session_time)
                sessions.append(session)
        
        return sorted(sessions, key=lambda s: s.start_time)
    
    def _create_session(
        self,
        user: User,
        service: CloudService,
        start_time: datetime
    ) -> Session:
        """
        Create a session for a user and service.
        
        Args:
            user: The user
            service: The cloud service
            start_time: Session start time
            
        Returns:
            Configured session
        """
        # Determine if mobile
        is_mobile = user.should_use_mobile()
        
        # Select user agent
        if is_mobile:
            user_agent = self._get_mobile_user_agent()
        else:
            user_agent = self._get_desktop_user_agent()
        
        # Get source IP
        if random.random() < 0.1:  # 10% VPN usage
            source_ip = self.ip_generator.generate_vpn_ip() or user.source_ip
        else:
            source_ip = user.source_ip
        
        # Create session
        session = Session(
            id=str(uuid.uuid4()),
            user=user,
            service=service,
            start_time=start_time,
            is_mobile=is_mobile,
            user_agent=user_agent,
            source_ip=source_ip
        )
        
        return session
    
    def _get_desktop_user_agent(self) -> str:
        """Get a desktop user agent string."""
        agents = [(ua, weight) for ua, weight in self.user_agents if 'Mobile' not in ua]
        if not agents:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        
        weights = [w for _, w in agents]
        selected = random.choices([ua for ua, _ in agents], weights=weights)[0]
        return selected
    
    def _get_mobile_user_agent(self) -> str:
        """Get a mobile user agent string."""
        mobile_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) Mobile/15E148",
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 Mobile",
            "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) Mobile/15E148"
        ]
        return random.choice(mobile_agents)
    
    def generate_hourly_activity(
        self,
        users: List[User],
        hour_start: datetime
    ) -> Dict[str, List[Session]]:
        """
        Generate all activity for all users in an hour.
        
        Args:
            users: List of users
            hour_start: Start of the hour
            
        Returns:
            Dict mapping user ID to their sessions
        """
        hour_end = hour_start + timedelta(hours=1)
        user_sessions = {}
        
        # Calculate how many users should be active this hour
        activity_multiplier = get_activity_multiplier(
            hour_start,
            timezone=self.enterprise_config.enterprise.get('timezone', 'America/New_York')
        )
        
        # Determine active users
        num_active = int(len(users) * activity_multiplier * random.uniform(0.8, 1.2))
        active_users = random.sample(users, min(num_active, len(users)))
        
        logger.info(f"Generating activity for {len(active_users)} users at {hour_start}")
        
        # Generate activity for each active user
        for user in active_users:
            sessions = self.generate_user_activity(user, hour_start, hour_end)
            if sessions:
                user_sessions[user.id] = sessions
        
        return user_sessions
    
    def should_generate_junk_traffic(self, user: User, timestamp: datetime) -> bool:
        """
        Determine if a user should generate junk traffic.
        
        Args:
            user: The user
            timestamp: Current time
            
        Returns:
            True if junk traffic should be generated
        """
        if not self.enterprise_config.junk_traffic or not self.enterprise_config.junk_traffic.enabled:
            return False
        
        # Base probability from config
        junk_probability = self.enterprise_config.junk_traffic.percentage_of_total
        
        # Adjust based on user profile
        if user.profile.name == "risky":
            junk_probability *= 1.5
        elif user.profile.name == "normal":
            junk_probability *= 0.8
        
        return random.random() < junk_probability