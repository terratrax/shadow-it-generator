"""
Cloud service definitions and management.

This package handles cloud service configurations and provides
service-specific behavior patterns.
"""

from .registry import ServiceRegistry
from .patterns import ServicePattern

__all__ = [
    "ServiceRegistry",
    "ServicePattern",
]