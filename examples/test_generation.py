#!/usr/bin/env python3
"""
Test script to verify the log generation engine works.
"""

from datetime import datetime, timedelta
from pathlib import Path
import sys
import yaml

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.shadow_it_generator.config.models import EnterpriseConfig
from src.shadow_it_generator.config.parser import ConfigParser
from src.shadow_it_generator.core.engine import LogGenerationEngine
from src.shadow_it_generator.utils.logger import setup_logging


def main():
    """Test the log generation engine."""
    # Setup logging
    setup_logging(verbose=True)
    
    # Load configurations
    config_parser = ConfigParser()
    
    # Load enterprise config
    enterprise_config_path = Path(__file__).parent.parent / "config" / "enterprise.yaml.example"
    enterprise_config = config_parser.parse_enterprise_config(enterprise_config_path)
    
    # Load a few service configs for testing
    services_dir = Path(__file__).parent.parent / "config" / "cloud-services"
    test_services = [
        "slack.yaml",
        "dropbox.yaml",
        "discord.yaml",
        "microsoft-365.yaml",
        "github.yaml"
    ]
    
    services = []
    for service_file in test_services:
        service_path = services_dir / service_file
        if service_path.exists():
            service = config_parser.parse_service_config(service_path)
            services.append(service)
            print(f"Loaded service: {service.name}")
    
    print(f"\nLoaded {len(services)} services for testing")
    
    # Create output directory
    output_dir = Path("output/test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize engine
    engine = LogGenerationEngine(
        enterprise_config=enterprise_config,
        services=services,
        output_dir=output_dir,
        log_format="both",  # Generate both LEEF and CEF
        start_date=datetime.now() - timedelta(hours=2),
        end_date=datetime.now()
    )
    
    print("\nStarting log generation...")
    print(f"Time period: {engine.start_date} to {engine.end_date}")
    print(f"Output directory: {output_dir}")
    
    # Generate logs
    engine.generate()
    
    print("\nGeneration complete!")
    print("\nGenerated files:")
    for fmt in ["leef", "cef"]:
        fmt_dir = output_dir / fmt
        if fmt_dir.exists():
            files = list(fmt_dir.glob("*.log"))
            for f in files:
                size = f.stat().st_size
                print(f"  {f.name}: {size:,} bytes")


if __name__ == "__main__":
    main()