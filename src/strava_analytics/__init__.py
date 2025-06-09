"""
Strava Analytics - Automated data pipeline for Strava activity data.

This package provides automated extraction, transformation, and loading of Strava
activity data using Prefect for orchestration and scheduling.

Main components:
- Token management with proactive refresh
- Data extraction from Strava API
- Data transformation and cleaning
- Database operations and loading
- Complete pipeline orchestration
"""

__version__ = "1.0.0"
__author__ = "Strava Analytics Team"

# Import main components for easy access
from .config import settings
from .utils import (
    load_tokens,
    save_tokens,
    refresh_token_if_needed,
    is_token_expired,
    will_token_expire_soon
)

__all__ = [
    "settings",
    "load_tokens", 
    "save_tokens",
    "refresh_token_if_needed",
    "is_token_expired",
    "will_token_expire_soon"
]
