#!/usr/bin/env python3
"""Simple test script for Shadow IT Log Generator."""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.shadow_it_generator.models.config import EnterpriseConfig
from src.shadow_it_generator.models.cloud_service import CloudService
from src.shadow_it_generator.services.registry import ServiceRegistry

def main():
    """Run a simple test."""
    print("Shadow IT Log Generator Simple Test")
    print("=" * 50)
    
    # Test loading configuration
    config_path = Path("config/enterprise.yaml")
    print(f"\n1. Loading configuration from: {config_path}")
    try:
        config = EnterpriseConfig.from_yaml(config_path)
        print(f"   ✓ Loaded config for domain: {config.get_domain()}")
        print(f"   ✓ User count: {config.get_user_count()}")
        print(f"   ✓ Output format: {config.get_output_format()}")
    except Exception as e:
        print(f"   ✗ Error loading config: {e}")
        return
    
    # Test loading cloud services
    services_dir = Path("config/cloud-services")
    print(f"\n2. Loading cloud services from: {services_dir}")
    try:
        registry = ServiceRegistry()
        registry.load_from_directory(services_dir)
        print(f"   ✓ Loaded {len(registry)} services")
        print(f"   ✓ Sanctioned: {len(registry.get_sanctioned_services())}")
        print(f"   ✓ Unsanctioned: {len(registry.get_unsanctioned_services())}")
        print(f"   ✓ Blocked: {len(registry.get_blocked_services())}")
    except Exception as e:
        print(f"   ✗ Error loading services: {e}")
        return
    
    # Test creating users
    print(f"\n3. Testing user creation")
    try:
        from src.shadow_it_generator.models.user import User
        test_profile = config.user_profiles[0] if config.user_profiles else {"name": "normal"}
        user = User(1, config.get_domain(), test_profile)
        print(f"   ✓ Created user: {user.email}")
        print(f"   ✓ User IP: {user.ip_address}")
    except Exception as e:
        print(f"   ✗ Error creating user: {e}")
        return
    
    # Test log formatting
    print(f"\n4. Testing log formatters")
    try:
        from src.shadow_it_generator.formatters.leef import LEEFFormatter
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        formatter = LEEFFormatter(output_dir)
        print(f"   ✓ LEEF formatter initialized")
        print(f"   ✓ Output directory: {output_dir}")
    except Exception as e:
        print(f"   ✗ Error with formatter: {e}")
        return
    
    print("\n" + "=" * 50)
    print("Basic tests completed successfully!")
    print("\nNote: Full log generation requires additional dependencies.")
    print("This test validates core functionality without external packages.")

if __name__ == "__main__":
    main()