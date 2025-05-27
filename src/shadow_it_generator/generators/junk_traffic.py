"""
Junk traffic generator for creating realistic noise in log streams.

This module generates traffic to popular internet sites that aren't
part of the main cloud services, adding realism to the log data.
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import numpy as np

from ..formatters.base import LogEvent
from ..utils.ip_generator import IPGenerator


class JunkTrafficGenerator:
    """
    Generates traffic to random popular internet sites.
    
    This adds noise to make the log stream more realistic by including
    traffic to news sites, blogs, forums, shopping sites, etc.
    """
    
    def __init__(
        self,
        junk_config: Dict[str, Any],
        ip_generator: IPGenerator,
        enterprise_domain: str
    ):
        """
        Initialize the junk traffic generator.
        
        Args:
            junk_config: Junk traffic configuration from enterprise config
            ip_generator: IP address generator instance
            enterprise_domain: Enterprise domain for user emails
        """
        self.config = junk_config
        self.ip_generator = ip_generator
        self.enterprise_domain = enterprise_domain
        
        # Load junk sites data
        self.junk_sites = self._load_junk_sites()
        
        # Pre-calculate category weights
        self.category_weights = list(self.config['categories'].values())
        self.categories = list(self.config['categories'].keys())
    
    def _load_junk_sites(self) -> Dict[str, Dict[str, Any]]:
        """Load junk sites from data file."""
        data_file = Path(__file__).parent.parent.parent.parent / "data" / "junk_sites.json"
        
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        return data['junk_sites']
    
    def _select_random_site(self) -> Tuple[str, str]:
        """
        Select a random site based on category weights.
        
        Returns:
            Tuple of (domain, category)
        """
        # Select category
        category = random.choices(self.categories, weights=self.category_weights)[0]
        
        # Get sites in category
        category_data = self.junk_sites[category]
        sites = category_data['sites']
        
        # Select site based on popularity weights
        site_weights = [site['popularity'] for site in sites]
        selected_site = random.choices(sites, weights=site_weights)[0]
        
        return selected_site['domain'], category
    
    def _generate_random_path(self, domain: str, category: str) -> str:
        """Generate a random but plausible path for the domain."""
        base_paths = {
            'news': [
                '/article/{id}',
                '/news/{year}/{month}/{id}',
                '/{category}/{title}',
                '/story/{id}',
                '/breaking-news/{id}',
                '/opinion/{author}/{id}',
                '/world/{region}/{id}',
                '/politics/{id}',
                '/business/{id}',
                '/technology/{id}'
            ],
            'reference': [
                '/wiki/{topic}',
                '/article/{topic}',
                '/how-to/{action}',
                '/definition/{word}',
                '/guide/{topic}',
                '/tutorial/{subject}',
                '/faq/{category}',
                '/help/{topic}',
                '/docs/{section}',
                '/learn/{subject}'
            ],
            'shopping': [
                '/product/{id}',
                '/category/{name}',
                '/search?q={query}',
                '/deals/{category}',
                '/sale/{event}',
                '/item/{sku}',
                '/browse/{department}',
                '/brand/{name}',
                '/checkout/cart',
                '/wishlist'
            ],
            'blogs': [
                '/post/{id}',
                '/{year}/{month}/{title}',
                '/blog/{author}/{title}',
                '/article/{id}',
                '/story/{slug}',
                '/{category}/{post}',
                '/archives/{year}/{month}',
                '/tag/{tag}',
                '/author/{name}',
                '/feed'
            ],
            'forums': [
                '/thread/{id}',
                '/topic/{id}',
                '/post/{id}',
                '/board/{name}',
                '/discussion/{id}',
                '/question/{id}',
                '/answer/{id}',
                '/user/{username}',
                '/search?q={query}',
                '/trending'
            ],
            'misc': [
                '/',
                '/forecast/{location}',
                '/scores/{sport}',
                '/results/{event}',
                '/schedule/{team}',
                '/player/{name}',
                '/stats/{category}',
                '/map/{location}',
                '/directions/{route}',
                '/restaurant/{id}'
            ]
        }
        
        # Get paths for category
        paths = base_paths.get(category, ['/'])
        path_template = random.choice(paths)
        
        # Replace placeholders
        replacements = {
            '{id}': str(random.randint(1000, 999999)),
            '{year}': str(random.randint(2020, 2024)),
            '{month}': f"{random.randint(1, 12):02d}",
            '{category}': random.choice(['tech', 'health', 'finance', 'sports', 'entertainment']),
            '{title}': f"article-{random.randint(100, 9999)}",
            '{topic}': random.choice(['python', 'cooking', 'fitness', 'travel', 'history']),
            '{word}': random.choice(['algorithm', 'pandemic', 'inflation', 'climate', 'innovation']),
            '{action}': random.choice(['install', 'configure', 'troubleshoot', 'optimize', 'secure']),
            '{query}': random.choice(['laptop', 'shoes', 'phone', 'book', 'game']),
            '{name}': random.choice(['electronics', 'clothing', 'home', 'sports', 'toys']),
            '{sku}': f"SKU{random.randint(100000, 999999)}",
            '{department}': random.choice(['mens', 'womens', 'kids', 'home', 'garden']),
            '{event}': random.choice(['summer', 'blackfriday', 'clearance', 'flash', 'weekend']),
            '{author}': random.choice(['john-doe', 'jane-smith', 'tech-writer', 'news-team']),
            '{slug}': f"post-{random.randint(100, 9999)}",
            '{tag}': random.choice(['tutorial', 'news', 'review', 'howto', 'update']),
            '{username}': f"user{random.randint(1000, 99999)}",
            '{sport}': random.choice(['nfl', 'nba', 'mlb', 'soccer', 'tennis']),
            '{location}': random.choice(['new-york', 'los-angeles', 'chicago', 'houston', 'phoenix']),
            '{team}': random.choice(['patriots', 'lakers', 'yankees', 'cowboys', 'warriors']),
            '{route}': 'from-here-to-there'
        }
        
        for placeholder, value in replacements.items():
            path_template = path_template.replace(placeholder, value)
        
        return path_template
    
    def _determine_action(self, category: str) -> str:
        """Determine if the request is allowed or blocked based on category."""
        category_data = self.junk_sites[category]
        if random.random() < category_data['allowed_rate']:
            return 'allowed'
        else:
            return 'blocked'
    
    def generate_junk_event(
        self,
        user_email: str,
        source_ip: str,
        timestamp: datetime,
        user_agent: str
    ) -> LogEvent:
        """
        Generate a single junk traffic event.
        
        Args:
            user_email: User's email address
            source_ip: Source IP address
            timestamp: Event timestamp
            user_agent: User agent string
            
        Returns:
            LogEvent for junk traffic
        """
        # Select random site
        domain, category = self._select_random_site()
        
        # Generate path
        path = self._generate_random_path(domain, category)
        
        # Determine action based on category
        action = self._determine_action(category)
        
        # Generate realistic response sizes
        if action == 'allowed':
            # Different categories have different typical sizes
            size_ranges = {
                'news': (5000, 50000),
                'reference': (3000, 30000),
                'shopping': (10000, 100000),
                'blogs': (2000, 20000),
                'forums': (1000, 15000),
                'misc': (1000, 20000)
            }
            min_size, max_size = size_ranges.get(category, (1000, 20000))
            bytes_received = random.randint(min_size, max_size)
            bytes_sent = random.randint(300, 2000)
            status_code = random.choices([200, 304], weights=[0.8, 0.2])[0]
            duration_ms = random.randint(50, 500)
        else:
            # Blocked requests
            bytes_received = 0
            bytes_sent = random.randint(100, 500)
            status_code = 403
            duration_ms = random.randint(10, 50)
        
        # Determine risk level based on category and action
        if action == 'blocked':
            risk_level = 'medium'
            category_name = 'blocked_content'
        else:
            risk_level = 'low'
            category_name = f'general_{category}'
        
        # Create log event
        return LogEvent(
            timestamp=timestamp,
            source_ip=source_ip,
            destination_ip=self.ip_generator.generate_destination_ip(),
            source_port=self.ip_generator.generate_source_port(),
            destination_port=443 if 'https://' in domain or random.random() > 0.1 else 80,
            username=user_email.split('@')[0],
            user_domain=self.enterprise_domain,
            url=f"https://{domain}{path}",
            method='GET' if random.random() > 0.1 else 'POST',
            status_code=status_code,
            bytes_sent=bytes_sent,
            bytes_received=bytes_received,
            duration_ms=duration_ms,
            user_agent=user_agent,
            referrer=f"https://{domain}/" if random.random() > 0.5 else None,
            action=action,
            category=category_name,
            risk_level=risk_level,
            service_name=f"Internet-{category}",
            protocol='https' if status_code != 403 else 'https',
            additional_fields={
                'junk_traffic': True,
                'site_category': category,
                'domain': domain
            }
        )
    
    def calculate_junk_events_count(self, total_events: int) -> int:
        """
        Calculate how many junk events to generate based on configuration.
        
        Args:
            total_events: Total number of events planned
            
        Returns:
            Number of junk events to generate
        """
        return int(total_events * self.config['percentage_of_total'])
    
    def generate_user_junk_events(
        self,
        user_email: str,
        source_ip: str,
        start_time: datetime,
        end_time: datetime,
        user_agent: str
    ) -> List[LogEvent]:
        """
        Generate junk traffic events for a user during a time period.
        
        Args:
            user_email: User's email address
            source_ip: Source IP address
            start_time: Start of time period
            end_time: End of time period
            user_agent: User agent string
            
        Returns:
            List of junk traffic events
        """
        events = []
        
        # Calculate number of events based on configuration
        duration_hours = (end_time - start_time).total_seconds() / 3600
        mean_per_day = self.config['requests_per_user_per_day']['mean']
        std_per_day = self.config['requests_per_user_per_day']['std_dev']
        
        # Calculate events for this time period
        events_per_hour = max(1, int(np.random.normal(mean_per_day / 24, std_per_day / 24)))
        total_events = int(events_per_hour * duration_hours)
        
        # Generate events spread across the time period
        for _ in range(total_events):
            # Random timestamp within the period
            time_offset = random.uniform(0, (end_time - start_time).total_seconds())
            event_time = start_time + datetime.timedelta(seconds=time_offset)
            
            # Generate event
            event = self.generate_junk_event(
                user_email=user_email,
                source_ip=source_ip,
                timestamp=event_time,
                user_agent=user_agent
            )
            events.append(event)
        
        return sorted(events, key=lambda e: e.timestamp)