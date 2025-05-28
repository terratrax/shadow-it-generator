#!/usr/bin/env python3
"""Minimal log generator without external dependencies."""

import yaml
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import os

# Simple user name data
FIRST_NAMES = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "James", "Mary", 
                "Robert", "Jennifer", "William", "Linda", "Richard", "Barbara", "Joseph",
                "Susan", "Thomas", "Jessica", "Charles", "Karen", "Christopher", "Nancy",
                "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Helen", "Donald", "Sandra",
                "Mark", "Donna", "Paul", "Carol", "Steven", "Ruth", "Andrew", "Sharon",
                "Kenneth", "Michelle", "Joshua", "Laura", "Kevin", "Sarah", "Brian", "Kimberly",
                "George", "Deborah", "Edward", "Jessica", "Ronald", "Shirley", "Timothy", "Cynthia"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
               "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
               "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
               "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
               "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
               "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
               "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker"]


class MinimalLogGenerator:
    """Minimal log generator implementation."""
    
    def __init__(self, config_path: str, services_dir: str, output_dir: str):
        self.config = self._load_config(config_path)
        self.services = self._load_services(services_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.junk_sites = self._load_junk_sites()
        self.users = self._generate_users()
        
    def _load_config(self, config_path: str) -> dict:
        """Load enterprise configuration."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_services(self, services_dir: str) -> list:
        """Load cloud service definitions."""
        services = []
        for yaml_file in Path(services_dir).glob('*.yaml'):
            with open(yaml_file, 'r') as f:
                service = yaml.safe_load(f)
                services.append(service)
        return services
    
    def _load_junk_sites(self) -> dict:
        """Load junk sites data."""
        junk_path = Path('data/junk_sites.json')
        if junk_path.exists():
            with open(junk_path, 'r') as f:
                data = json.load(f)
                return data.get('junk_sites', {})
        return {}
    
    def _generate_users(self) -> list:
        """Generate user list."""
        users = []
        total_users = self.config['enterprise']['total_users']
        domain = self.config['enterprise']['domain']
        
        for i in range(min(total_users, 100)):  # Limit to 100 for minimal version
            first_name = random.choice(FIRST_NAMES).lower()
            last_name = random.choice(LAST_NAMES).lower()
            email = f"{first_name}.{last_name}@{domain}"
            
            users.append({
                'id': i + 1,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'ip': self._generate_ip(),
                'profile': self._assign_profile()
            })
        
        return users
    
    def _generate_ip(self) -> str:
        """Generate random internal IP."""
        return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    
    def _assign_profile(self) -> str:
        """Assign user profile based on distribution."""
        rand = random.random() * 100
        if rand < 70:
            return 'normal'
        elif rand < 90:
            return 'power_user'
        else:
            return 'risky'
    
    def generate_logs(self, start_time: datetime, duration_hours: int = 24):
        """Generate logs for specified duration."""
        print(f"Generating logs for {duration_hours} hours starting from {start_time}")
        
        # Create output file
        output_file = self.output_dir / f"shadow_it_logs_{start_time.strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(output_file, 'w') as f:
            current_time = start_time
            end_time = start_time + timedelta(hours=duration_hours)
            
            while current_time < end_time:
                # Generate events for this time slot
                events = self._generate_time_slot_events(current_time)
                
                # Write events to file
                for event in events:
                    leef_line = self._format_leef(event)
                    f.write(leef_line + '\n')
                
                # Move to next time slot (5 minutes)
                current_time += timedelta(minutes=5)
        
        print(f"Generated {output_file}")
        return output_file
    
    def _generate_time_slot_events(self, timestamp: datetime) -> list:
        """Generate events for a 5-minute time slot."""
        events = []
        hour = timestamp.hour
        
        # Determine activity level based on hour
        if hour >= 9 and hour <= 17:  # Business hours
            activity_level = 1.0
        elif hour >= 6 and hour <= 9 or hour >= 17 and hour <= 20:  # Early/late
            activity_level = 0.5
        else:  # Night
            activity_level = 0.1
        
        # Sample active users
        num_active = int(len(self.users) * activity_level * 0.3)  # 30% active at peak
        active_users = random.sample(self.users, num_active)
        
        for user in active_users:
            # Generate 1-5 events per user
            num_events = random.randint(1, 5)
            
            for _ in range(num_events):
                # 70% cloud service traffic, 30% junk traffic
                if random.random() < 0.7:
                    event = self._generate_service_event(user, timestamp)
                else:
                    event = self._generate_junk_event(user, timestamp)
                
                if event:
                    events.append(event)
        
        return events
    
    def _generate_service_event(self, user: dict, timestamp: datetime) -> dict:
        """Generate cloud service access event."""
        # Pick a service based on user profile
        if user['profile'] == 'risky':
            # Prefer unsanctioned/blocked services
            service_list = [s for s in self.services if s['service']['status'] in ['unsanctioned', 'blocked']]
        else:
            # Prefer sanctioned services
            service_list = [s for s in self.services if s['service']['status'] == 'sanctioned']
        
        if not service_list:
            service_list = self.services
        
        service = random.choice(service_list)
        
        # Determine if blocked
        block_rate = service['security_events'].get('block_rate', 0)
        blocked = random.random() < block_rate
        
        # Generate event
        domain = service['network']['domains'][0].replace('*.', '')
        
        return {
            'timestamp': timestamp,
            'user': user['email'],
            'source_ip': user['ip'],
            'destination': domain,
            'url': f"https://{domain}/api/v1/resource",
            'action': 'blocked' if blocked else 'allowed',
            'category': service['service']['category'],
            'service_name': service['service']['name'],
            'bytes_sent': random.randint(500, 5000),
            'bytes_received': random.randint(1000, 50000),
            'status_code': 403 if blocked else 200
        }
    
    def _generate_junk_event(self, user: dict, timestamp: datetime) -> dict:
        """Generate junk traffic event."""
        if not self.junk_sites:
            return None
        
        # Pick a category
        category = random.choice(list(self.junk_sites.keys()))
        category_data = self.junk_sites[category]
        
        # Pick a site
        site = random.choice(category_data['sites'])
        
        # Determine if blocked
        blocked = random.random() < category_data.get('blocked_rate', 0.05)
        
        return {
            'timestamp': timestamp,
            'user': user['email'],
            'source_ip': user['ip'],
            'destination': site['domain'],
            'url': f"https://{site['domain']}/",
            'action': 'blocked' if blocked else 'allowed',
            'category': category,
            'service_name': site['domain'],  # Use domain as name
            'bytes_sent': random.randint(300, 2000),
            'bytes_received': random.randint(5000, 100000),
            'status_code': 403 if blocked else 200
        }
    
    def _format_leef(self, event: dict) -> str:
        """Format event as LEEF log line."""
        # LEEF header
        header = "LEEF:2.0|McAfee|Web Gateway|10.15.0.623|302|"
        
        # Format timestamp
        dev_time = event['timestamp'].strftime('%b %d %Y %H:%M:%S')
        
        # Build fields
        fields = {
            'devTime': dev_time,
            'src': event['source_ip'],
            'dst': self._generate_ip(),  # Random destination IP
            'srcPort': random.randint(40000, 60000),
            'dstPort': 443,
            'usrName': event['user'],
            'request': event['url'],
            'action': event['action'],
            'cat': event['category'],
            'app': event['service_name'],
            'bytesIn': event['bytes_received'],
            'bytesOut': event['bytes_sent'],
            'responseCode': event['status_code']
        }
        
        # Join fields
        field_str = '\t'.join([f"{k}={v}" for k, v in fields.items()])
        
        return header + field_str


def main():
    """Run the minimal log generator."""
    print("Shadow IT Log Generator - Minimal Version")
    print("=" * 50)
    
    # Initialize generator
    generator = MinimalLogGenerator(
        config_path='config/enterprise.yaml',
        services_dir='config/cloud-services',
        output_dir='output'
    )
    
    # Generate logs for the last 2 hours
    start_time = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=2)
    
    output_file = generator.generate_logs(start_time, duration_hours=2)
    
    # Show some stats
    with open(output_file, 'r') as f:
        lines = f.readlines()
    
    print(f"\nGenerated {len(lines)} log entries")
    print(f"Output file: {output_file}")
    print(f"File size: {os.path.getsize(output_file) / 1024:.2f} KB")
    
    # Show sample entries
    print("\nSample log entries:")
    for line in lines[:3]:
        print(f"  {line[:150]}...")


if __name__ == "__main__":
    main()