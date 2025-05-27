"""
Core modules for the Shadow IT Log Generator.

This package contains the main engine and core logic for generating
realistic shadow IT network traffic logs.
"""

from .engine import LogGenerationEngine
from .user import User, UserProfile
from .session import Session
from .traffic import TrafficGenerator

__all__ = [
    "LogGenerationEngine",
    "User",
    "UserProfile",
    "Session",
    "TrafficGenerator",
]