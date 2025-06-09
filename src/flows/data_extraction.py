"""Data extraction flows for Strava API."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
import polars as pl

from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from prefect.cache_policies import INPUTS

from src.config import settings
from src.utils import load_tokens
from src.flows.token_management import token_refresh_flow


@task(
    cache_policy=INPUTS,
    cache_expiration=timedelta(minutes=30),
    retries=3,
    retry_delay_seconds=60
)
def get_valid_access_token() -> str:
    """Get a valid access token, refreshing if necessary."""
    logger = get_run_logger()
    
    # First, try to refresh token proactively
    refresh_result = token_refresh_flow()
    
    if not refresh_result['success']:
        raise Exception(f"Failed to ensure valid token: {refresh_result.get('error')}")
    
    # Load the current tokens
    tokens = load_tokens()
    access_token = tokens['access_token']
    
    logger.info("Valid access token obtained")
    return access_token


@task(retries=3, retry_delay_seconds=30)
def fetch_activities_page(
    access_token: str, 
    page: int = 1, 
    per_page: int = None,
    after: Optional[int] = None,
    before: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Fetch a single page of activities from Strava API."""
    logger = get_run_logger()
    
    if per_page is None:
        per_page = settings.strava_activities_per_page
    
    url = f"{settings.strava_api_base_url}/athlete/activities"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    params = {
        'per_page': per_page,
        'page': page
    }
    
    # Add optional date filters
    if after:
        params['after'] = after
    if before:
        params['before'] = before
    
    logger.info(f"Fetching activities page {page} with {per_page} items per page")
    
    try:
        response = requests.get(url=url, headers=headers, params=params)
        response.raise_for_status()
        
        activities = response.json()
        logger.info(f"Successfully fetched {len(activities)} activities from page {page}")
        
        return activities
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            logger.error("Authentication failed - token may be invalid")
            raise Exception("Authentication failed - token may be invalid")
        else:
            logger.error(f"HTTP error fetching activities: {e}")
            raise
    except Exception as e:
        logger.error(f"Error fetching activities page {page}: {e}")
        raise


@task
def fetch_all_activities(
    access_token: str,
    after: Optional[int] = None,
    before: Optional[int] = None,
    max_pages: int = 100
) -> List[Dict[str, Any]]:
    """Fetch all activities from Strava API with pagination."""
    logger = get_run_logger()
    
    all_activities = []
    page = 1
    
    logger.info(f"Starting to fetch all activities (max_pages={max_pages})")
    
    while page <= max_pages:
        try:
            activities_page = fetch_activities_page(
                access_token=access_token,
                page=page,
                after=after,
                before=before
            )
            
            if not activities_page:
                logger.info(f"No more activities found at page {page}. Stopping pagination.")
                break
            
            all_activities.extend(activities_page)
            logger.info(f"Page {page}: Added {len(activities_page)} activities. "
                       f"Total so far: {len(all_activities)}")
            
            page += 1
            
        except Exception as e:
            logger.error(f"Failed to fetch page {page}: {e}")
            if page == 1:
                # If first page fails, re-raise the exception
                raise
            else:
                # If later pages fail, log and continue with what we have
                logger.warning(f"Continuing with {len(all_activities)} activities from {page-1} pages")
                break
    
    logger.info(f"Completed fetching activities. Total: {len(all_activities)} activities from {page-1} pages")
    return all_activities


@task
def convert_to_dataframe(activities: List[Dict[str, Any]]) -> pl.DataFrame:
    """Convert activities list to Polars DataFrame."""
    logger = get_run_logger()
    
    if not activities:
        logger.warning("No activities to convert to DataFrame")
        return pl.DataFrame()
    
    logger.info(f"Converting {len(activities)} activities to DataFrame")
    
    try:
        df = pl.DataFrame(activities)
        logger.info(f"Successfully created DataFrame with shape: {df.shape}")
        return df
        
    except Exception as e:
        logger.error(f"Error converting activities to DataFrame: {e}")
        raise


@flow(name="strava-data-extraction", log_prints=True)
def strava_data_extraction_flow(
    after_date: Optional[str] = None,
    before_date: Optional[str] = None,
    max_pages: int = 100
) -> pl.DataFrame:
    """
    Main data extraction flow for Strava activities.
    
    Args:
        after_date: ISO date string (YYYY-MM-DD) to fetch activities after
        before_date: ISO date string (YYYY-MM-DD) to fetch activities before  
        max_pages: Maximum number of pages to fetch
    
    Returns:
        Polars DataFrame with activities data
    """
    logger = get_run_logger()
    logger.info("Starting Strava data extraction flow")
    
    # Convert date strings to timestamps if provided
    after_timestamp = None
    before_timestamp = None
    
    if after_date:
        after_timestamp = int(datetime.fromisoformat(after_date).timestamp())
        logger.info(f"Filtering activities after: {after_date}")
    
    if before_date:
        before_timestamp = int(datetime.fromisoformat(before_date).timestamp())
        logger.info(f"Filtering activities before: {before_date}")
    
    # Get valid access token
    access_token = get_valid_access_token()
    
    # Fetch all activities
    activities = fetch_all_activities(
        access_token=access_token,
        after=after_timestamp,
        before=before_timestamp,
        max_pages=max_pages
    )
    
    # Convert to DataFrame
    activities_df = convert_to_dataframe(activities)
    
    logger.info(f"Data extraction completed. Retrieved {len(activities_df)} activities")
    return activities_df


if __name__ == "__main__":
    # For testing
    df = strava_data_extraction_flow()
    print(f"Extracted {len(df)} activities")
    if len(df) > 0:
        print(df.head())
