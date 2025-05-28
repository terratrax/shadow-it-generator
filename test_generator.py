#!/usr/bin/env python3
"""Test script for Shadow IT Log Generator."""

import logging
from datetime import datetime, timedelta
from pathlib import Path

from src.shadow_it_generator.core.engine import LogGeneratorEngine
from src.shadow_it_generator.models.config import EnterpriseConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run a test generation."""
    print("Shadow IT Log Generator Test")
    print("=" * 50)
    
    # Load configuration
    config_path = Path("config/enterprise.yaml")
    print(f"\nLoading configuration from: {config_path}")
    config = EnterpriseConfig.from_yaml(config_path)
    
    # Create output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize engine
    print("\nInitializing log generator engine...")
    engine = LogGeneratorEngine(config, output_dir)
    
    # Generate logs for a short test period
    start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=2)  # 2 hour test
    
    print(f"\nGenerating logs from {start_time} to {end_time}")
    print(f"Output directory: {output_dir}")
    print("\nStarting generation...\n")
    
    engine.generate_logs(start_time, end_time)
    
    print("\n" + "=" * 50)
    print("Test generation complete!")
    print(f"\nCheck the output in: {output_dir}/")
    
    # Show some statistics
    log_files = list(output_dir.glob("*.log"))
    if log_files:
        print(f"\nGenerated {len(log_files)} log file(s):")
        for log_file in sorted(log_files):
            size_mb = log_file.stat().st_size / (1024 * 1024)
            print(f"  - {log_file.name}: {size_mb:.2f} MB")

if __name__ == "__main__":
    main()