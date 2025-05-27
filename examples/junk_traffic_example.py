#!/usr/bin/env python3
"""
Example demonstrating junk traffic generation.

This shows how junk traffic is integrated into the log stream
to create more realistic network logs.
"""

from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.shadow_it_generator.generators.junk_traffic import JunkTrafficGenerator
from src.shadow_it_generator.utils.ip_generator import IPGenerator
from src.shadow_it_generator.formatters.leef import LEEFFormatter


def main():
    """Demonstrate junk traffic generation."""
    
    # Example configuration
    junk_config = {
        'enabled': True,
        'percentage_of_total': 0.30,
        'allowed_rate': 0.85,
        'blocked_rate': 0.15,
        'requests_per_user_per_day': {
            'mean': 150,
            'std_dev': 75
        },
        'categories': {
            'news': 0.25,
            'reference': 0.20,
            'shopping': 0.15,
            'blogs': 0.15,
            'forums': 0.10,
            'misc': 0.15
        }
    }
    
    # Network configuration
    network_config = {
        'internal_subnets': ['10.0.0.0/8', '192.168.0.0/16'],
        'egress_ips': ['203.0.113.1', '203.0.113.2'],
        'proxy_ips': ['10.0.1.100']
    }
    
    # Initialize components
    ip_generator = IPGenerator(
        internal_subnets=network_config['internal_subnets'],
        egress_ips=network_config['egress_ips'],
        proxy_ips=network_config['proxy_ips']
    )
    
    junk_generator = JunkTrafficGenerator(
        junk_config=junk_config,
        ip_generator=ip_generator,
        enterprise_domain='acme.com'
    )
    
    # Initialize formatter
    output_dir = Path('output/examples')
    output_dir.mkdir(parents=True, exist_ok=True)
    formatter = LEEFFormatter(output_dir)
    formatter.setup()
    
    # Generate some example events
    print("Generating junk traffic examples...\n")
    
    # User details
    user_email = 'john.doe@acme.com'
    source_ip = ip_generator.generate_internal_ip()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
    
    # Time period (1 hour)
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=1)
    
    # Generate events
    events = junk_generator.generate_user_junk_events(
        user_email=user_email,
        source_ip=source_ip,
        start_time=start_time,
        end_time=end_time,
        user_agent=user_agent
    )
    
    print(f"Generated {len(events)} junk traffic events\n")
    
    # Display some examples
    print("Example events:")
    print("-" * 80)
    
    for i, event in enumerate(events[:10]):  # Show first 10
        print(f"\nEvent {i+1}:")
        print(f"  Time: {event.timestamp}")
        print(f"  URL: {event.url}")
        print(f"  Category: {event.category}")
        print(f"  Action: {event.action}")
        print(f"  Status: {event.status_code}")
        print(f"  Bytes: {event.bytes_received}")
        
        # Also write to LEEF format
        formatter.write_event(event)
    
    # Show distribution
    print("\n" + "-" * 80)
    print("\nTraffic distribution:")
    
    # Count by category
    category_counts = {}
    for event in events:
        if 'site_category' in event.additional_fields:
            cat = event.additional_fields['site_category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for cat, count in sorted(category_counts.items()):
        percentage = (count / len(events)) * 100
        print(f"  {cat}: {count} events ({percentage:.1f}%)")
    
    # Count by action
    print("\nAction distribution:")
    allowed = sum(1 for e in events if e.action == 'allowed')
    blocked = len(events) - allowed
    print(f"  Allowed: {allowed} ({(allowed/len(events))*100:.1f}%)")
    print(f"  Blocked: {blocked} ({(blocked/len(events))*100:.1f}%)")
    
    formatter.finalize()
    print(f"\nLEEF logs written to: {output_dir}")


if __name__ == "__main__":
    main()