"""
Main entry point for the Shadow IT Log Generator CLI application.

This module provides the command-line interface for generating shadow IT logs
based on enterprise and cloud service configurations.
"""

import click
import sys
from pathlib import Path
from typing import Optional

from .core.engine import LogGenerationEngine
from .config.parser import ConfigParser
from .utils.logger import setup_logging


@click.command()
@click.option(
    '--enterprise-config', '-e',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help='Path to enterprise configuration YAML file'
)
@click.option(
    '--services-dir', '-s',
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default='config/cloud-services',
    help='Directory containing cloud service YAML files'
)
@click.option(
    '--output', '-o',
    type=click.Path(path_type=Path),
    default='output/logs',
    help='Output directory for generated logs'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['leef', 'cef', 'both']),
    default='leef',
    help='Output log format'
)
@click.option(
    '--start-date',
    type=click.DateTime(),
    help='Start date for log generation (default: 30 days ago)'
)
@click.option(
    '--end-date',
    type=click.DateTime(),
    help='End date for log generation (default: now)'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose logging'
)
def main(
    enterprise_config: Path,
    services_dir: Path,
    output: Path,
    format: str,
    start_date: Optional[click.DateTime],
    end_date: Optional[click.DateTime],
    verbose: bool
) -> None:
    """
    Shadow IT Log Generator - Generate realistic shadow IT network traffic logs.
    
    This tool generates logs based on enterprise configuration and cloud service
    definitions to simulate realistic shadow IT activity patterns.
    """
    
    # Setup logging
    setup_logging(verbose)
    
    try:
        # Parse configurations
        config_parser = ConfigParser()
        enterprise_conf = config_parser.parse_enterprise_config(enterprise_config)
        services = config_parser.parse_services_directory(services_dir)
        
        # Create output directory
        output.mkdir(parents=True, exist_ok=True)
        
        # Initialize and run the log generation engine
        engine = LogGenerationEngine(
            enterprise_config=enterprise_conf,
            services=services,
            output_dir=output,
            log_format=format,
            start_date=start_date,
            end_date=end_date
        )
        
        click.echo("Starting log generation...")
        engine.generate()
        click.echo(f"Logs generated successfully in {output}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()