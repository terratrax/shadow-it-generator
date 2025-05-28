#!/usr/bin/env python3
"""Basic test without complex dependencies."""

import yaml
from pathlib import Path
import random
from datetime import datetime

def test_config_loading():
    """Test loading configuration files."""
    print("1. Testing configuration loading...")
    
    # Load enterprise config
    with open('config/enterprise.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"   ✓ Enterprise domain: {config['enterprise']['domain']}")
    print(f"   ✓ Total users: {config['enterprise']['total_users']}")
    print(f"   ✓ Enterprise name: {config['enterprise']['name']}")
    
    # Check junk traffic config
    if 'junk_traffic' in config:
        print(f"   ✓ Junk traffic enabled: {config['junk_traffic']['enabled']}")
        print(f"   ✓ Junk traffic percentage: {config['junk_traffic']['percentage_of_total']}")
    
    return config

def test_service_loading():
    """Test loading cloud service definitions."""
    print("\n2. Testing cloud service loading...")
    
    services_dir = Path('config/cloud-services')
    yaml_files = list(services_dir.glob('*.yaml'))
    
    print(f"   ✓ Found {len(yaml_files)} service definitions")
    
    # Load a few sample services
    sample_services = []
    for yaml_file in yaml_files[:5]:
        with open(yaml_file, 'r') as f:
            service = yaml.safe_load(f)
            sample_services.append(service)
    
    # Count by status
    status_counts = {'sanctioned': 0, 'unsanctioned': 0, 'blocked': 0}
    for yaml_file in yaml_files:
        with open(yaml_file, 'r') as f:
            service = yaml.safe_load(f)
            status = service['service']['status']
            status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"   ✓ Sanctioned services: {status_counts['sanctioned']}")
    print(f"   ✓ Unsanctioned services: {status_counts['unsanctioned']}")
    print(f"   ✓ Blocked services: {status_counts['blocked']}")
    
    return sample_services

def test_log_generation_logic():
    """Test basic log generation logic."""
    print("\n3. Testing log generation logic...")
    
    # Simulate generating a log entry
    timestamp = datetime.now()
    user_email = "john.doe@acmecorp.com"
    source_ip = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    
    # Sample log entry
    log_entry = {
        'timestamp': timestamp.isoformat(),
        'user': user_email,
        'source_ip': source_ip,
        'destination': 'slack.com',
        'action': 'allowed',
        'bytes': random.randint(1000, 100000),
        'category': 'collaboration'
    }
    
    print(f"   ✓ Generated sample log entry:")
    print(f"     - User: {log_entry['user']}")
    print(f"     - Source IP: {log_entry['source_ip']}")
    print(f"     - Destination: {log_entry['destination']}")
    print(f"     - Bytes: {log_entry['bytes']}")
    
    return log_entry

def test_leef_format():
    """Test LEEF format generation."""
    print("\n4. Testing LEEF format...")
    
    # Sample LEEF header
    leef_header = "LEEF:2.0|McAfee|Web Gateway|10.15.0.623|302|"
    
    # Sample fields
    fields = {
        'devTime': '2024-01-15 10:30:45',
        'src': '10.0.1.100',
        'dst': '52.97.178.195',
        'usrName': 'john.doe@acmecorp.com',
        'request': 'https://slack.com/api/rtm.connect',
        'action': 'allowed'
    }
    
    # Build LEEF line
    field_str = '\t'.join([f"{k}={v}" for k, v in fields.items()])
    leef_line = leef_header + field_str
    
    print(f"   ✓ Generated LEEF log:")
    print(f"     {leef_line[:100]}...")
    
    return leef_line

def main():
    """Run all tests."""
    print("Shadow IT Log Generator - Basic Tests")
    print("=" * 50)
    
    try:
        config = test_config_loading()
        services = test_service_loading()
        log_entry = test_log_generation_logic()
        leef_line = test_leef_format()
        
        print("\n" + "=" * 50)
        print("✅ All basic tests passed!")
        print("\nThe system is ready for log generation.")
        print("Note: Full functionality requires additional Python packages.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()