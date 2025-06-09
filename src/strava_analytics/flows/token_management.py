"""Token management flows for Strava API authentication."""

from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from prefect.cache_policies import INPUTS

from ..config import settings
from ..utils import (
    load_tokens,
    save_tokens,
    refresh_token_if_needed,
    will_token_expire_soon,
    get_time_until_token_expires
)


@task(
    cache_policy=INPUTS,
    cache_expiration=timedelta(minutes=5),
    retries=3,
    retry_delay_seconds=30
)
def check_token_status() -> Dict[str, Any]:
    """Check the current status of the access token."""
    logger = get_run_logger()
    
    try:
        tokens = load_tokens()
        
        # Check if required fields exist
        required_fields = ['access_token', 'refresh_token', 'expires_at']
        missing_fields = [field for field in required_fields if field not in tokens]
        
        if missing_fields:
            raise ValueError(f"Missing required token fields: {missing_fields}")
        
        expires_at = tokens['expires_at']
        time_until_expiry = get_time_until_token_expires(expires_at)
        will_expire_soon = will_token_expire_soon(expires_at)
        
        status = {
            'has_valid_token': True,
            'expires_at': expires_at,
            'expires_at_datetime': datetime.fromtimestamp(expires_at),
            'time_until_expiry': time_until_expiry,
            'will_expire_soon': will_expire_soon,
            'buffer_minutes': settings.token_refresh_buffer_minutes
        }
        
        logger.info(f"Token status: expires at {status['expires_at_datetime']}, "
                   f"time remaining: {time_until_expiry}, "
                   f"needs refresh: {will_expire_soon}")
        
        return status
        
    except FileNotFoundError:
        logger.error("Token file not found. Initial authentication required.")
        return {
            'has_valid_token': False,
            'error': 'Token file not found'
        }
    except Exception as e:
        logger.error(f"Error checking token status: {e}")
        return {
            'has_valid_token': False,
            'error': str(e)
        }


@task(retries=3, retry_delay_seconds=30)
def refresh_access_token(force_refresh: bool = False) -> Dict[str, Any]:
    """Refresh the Strava access token."""
    logger = get_run_logger()
    
    try:
        tokens = load_tokens()
        
        # Get client credentials from tokens or settings
        client_id = tokens.get('client_id') or settings.strava_client_id
        client_secret = tokens.get('client_secret') or settings.strava_client_secret
        
        if not client_id or not client_secret:
            raise ValueError("Client ID and Client Secret must be provided")
        
        logger.info(f"Refreshing token (force_refresh={force_refresh})")
        
        new_access_token = refresh_token_if_needed(
            client_id=client_id,
            client_secret=client_secret,
            force_refresh=force_refresh
        )
        
        # Get updated token info
        updated_tokens = load_tokens()
        
        result = {
            'success': True,
            'access_token': new_access_token,
            'expires_at': updated_tokens['expires_at'],
            'expires_at_datetime': datetime.fromtimestamp(updated_tokens['expires_at']),
            'refreshed_at': datetime.now()
        }
        
        logger.info(f"Token refreshed successfully. New expiry: {result['expires_at_datetime']}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to refresh token: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@flow(name="token-refresh-flow", log_prints=True)
def token_refresh_flow(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Main token refresh flow.
    
    Args:
        force_refresh: If True, refresh token regardless of expiry status
    
    Returns:
        Dictionary with refresh results
    """
    logger = get_run_logger()
    logger.info("Starting token refresh flow")
    
    # Check current token status
    token_status = check_token_status()
    
    if not token_status['has_valid_token']:
        logger.error(f"No valid token available: {token_status.get('error', 'Unknown error')}")
        return {
            'success': False,
            'error': 'No valid token available',
            'details': token_status
        }
    
    # Determine if refresh is needed
    needs_refresh = force_refresh or token_status['will_expire_soon']
    
    if not needs_refresh:
        logger.info(f"Token refresh not needed. Token expires at {token_status['expires_at_datetime']}")
        return {
            'success': True,
            'action': 'no_refresh_needed',
            'token_status': token_status
        }
    
    # Refresh the token
    refresh_result = refresh_access_token(force_refresh=force_refresh)
    
    if refresh_result['success']:
        logger.info("Token refresh flow completed successfully")
        return {
            'success': True,
            'action': 'token_refreshed',
            'refresh_result': refresh_result,
            'previous_status': token_status
        }
    else:
        logger.error(f"Token refresh flow failed: {refresh_result.get('error')}")
        return {
            'success': False,
            'error': 'Token refresh failed',
            'details': refresh_result
        }


@flow(name="proactive-token-management", log_prints=True)
def proactive_token_management_flow() -> Dict[str, Any]:
    """
    Proactive token management flow that checks and refreshes tokens before they expire.
    This flow should be scheduled to run regularly (e.g., every hour).
    """
    logger = get_run_logger()
    logger.info("Starting proactive token management flow")
    
    # Run the token refresh flow
    result = token_refresh_flow(force_refresh=False)
    
    if result['success']:
        logger.info("Proactive token management completed successfully")
    else:
        logger.error(f"Proactive token management failed: {result.get('error')}")
    
    return result


if __name__ == "__main__":
    # For testing
    result = token_refresh_flow()
    print(f"Token refresh result: {result}")
