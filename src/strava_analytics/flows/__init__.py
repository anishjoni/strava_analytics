"""
Prefect flows for Strava analytics pipeline.

This module contains all the Prefect flows for the automated Strava data pipeline:
- Token management and refresh
- Data extraction from Strava API
- Data transformation and cleaning
- Database operations
- Main pipeline orchestration
"""

# Import all flows for easy access using absolute imports
import sys
import os

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from strava_analytics.flows.token_management import (
    proactive_token_management_flow,
    token_refresh_flow,
    check_token_status,
    refresh_access_token
)

from strava_analytics.flows.data_extraction import (
    strava_data_extraction_flow,
    get_valid_access_token,
    fetch_activities_page,
    fetch_all_activities
)

from strava_analytics.flows.data_transformation import (
    strava_data_transformation_flow,
    select_core_columns,
    create_derived_columns,
    apply_data_types,
    add_feature_engineering
)

from strava_analytics.flows.database_operations import (
    strava_database_operations_flow,
    create_database_connection,
    load_data_to_database
)

from strava_analytics.flows.main_pipeline import (
    strava_analytics_pipeline_flow,
    daily_strava_sync_flow,
    weekly_full_sync_flow
)

__all__ = [
    # Token management
    "proactive_token_management_flow",
    "token_refresh_flow",
    "check_token_status",
    "refresh_access_token",

    # Data extraction
    "strava_data_extraction_flow",
    "get_valid_access_token",
    "fetch_activities_page",
    "fetch_all_activities",

    # Data transformation
    "strava_data_transformation_flow",
    "select_core_columns",
    "create_derived_columns",
    "apply_data_types",
    "add_feature_engineering",

    # Database operations
    "strava_database_operations_flow",
    "create_database_connection",
    "load_data_to_database",

    # Main pipeline
    "strava_analytics_pipeline_flow",
    "daily_strava_sync_flow",
    "weekly_full_sync_flow"
]
