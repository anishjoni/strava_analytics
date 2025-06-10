# Import libraries
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import requests

from prefect.blocks.system import Secret
from prefect.blocks.data import JSON # Import the JSON block
from prefect.utilities.logging import get_run_logger

# Add the project root to Python path to avoid relative import issues

from strava_analytics.config import settings

logger = get_run_logger()

# Define your JSON Block name
TOKEN_DATA_BLOCK_NAME = "strava-auth-token" 

# Utility functions
def load_tokens() -> Dict[str, Any]:
    """Load Strava tokens from the Prefect JSON block."""
    logger.info(f"Attempting to load tokens from Prefect JSON Block: {TOKEN_DATA_BLOCK_NAME}")
    try:
        json_block = JSON.load(TOKEN_DATA_BLOCK_NAME)
        # The .value attribute of a JSON block holds the deserialized JSON data
        tokens = json_block.value
        if not tokens: # If the block is empty JSON {}
            logger.warning(f"Prefect JSON Block '{TOKEN_DATA_BLOCK_NAME}' is empty. No existing token found.")
            return {}
        logger.info(f"Successfully loaded token data from block. Keys: {list(tokens.keys())}")
        return tokens
    except Exception as e:
        logger.error(f"Failed to load tokens from Prefect JSON Block '{TOKEN_DATA_BLOCK_NAME}': {e}")
        # If the block itself doesn't exist, this will also catch it
        return {} #

def save_tokens(tokens: Dict[str, Any], path: Optional[str] = None) -> None:
  """Save Strava tokens to the Prefect JSON block."""
    logger.info(f"Attempting to save tokens to Prefect JSON Block: {TOKEN_DATA_BLOCK_NAME}")
    try:
        # Create a new JSON block instance with the updated data
        json_block = JSON(value=tokens)
        # Save (and overwrite) the block with the new data
        json_block.save(name=TOKEN_DATA_BLOCK_NAME, overwrite=True)
        logger.info(f"Successfully saved new token data to Prefect JSON Block: {TOKEN_DATA_BLOCK_NAME}")
    except Exception as e:
        logger.error(f"Failed to save tokens to Prefect JSON Block '{TOKEN_DATA_BLOCK_NAME}': {e}")
        raise # Critical failure if we can't save the token

def is_token_expired(expires_at: Any, buffer_minutes: int = 0) -> bool:
    """Check if token is expired or will expire within buffer_minutes."""
    if isinstance(expires_at, str):
        expires_at = int(float(expires_at))

    # Add buffer to check if token will expire soon
    buffer_seconds = buffer_minutes * 60
    current_time = datetime.now().timestamp()

    return current_time >= (expires_at - buffer_seconds)

def will_token_expire_soon(expires_at: Any, buffer_minutes: int = None) -> bool:
    """Check if token will expire within the specified buffer time."""
    if buffer_minutes is None:
        buffer_minutes = settings.token_refresh_buffer_minutes

    return is_token_expired(expires_at, buffer_minutes)

def get_time_until_token_expires(expires_at: Any) -> timedelta:
    """Get the time remaining until token expires."""
    if isinstance(expires_at, str):
        expires_at = int(float(expires_at))

    current_time = datetime.now().timestamp()
    seconds_remaining = expires_at - current_time

    return timedelta(seconds=max(0, seconds_remaining))

def refresh_token_if_needed(client_id: str, client_secret: str, force_refresh: bool = False) -> str:
    """Refresh token if needed or forced."""
    tokens = load_tokens()

    if force_refresh or is_token_expired(tokens['expires_at']):
        print('Access token expired or refresh forced. Refreshing...')

        url = "https://www.strava.com/oauth/token"
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': tokens['refresh_token']
        }

        r = requests.post(url=url, params=payload)

        if r.status_code == 200:
            new_tokens = r.json()
            tokens = {
                "access_token": new_tokens['access_token'],
                "refresh_token": new_tokens['refresh_token'],
                "expires_at": new_tokens['expires_at'],
                "client_id": client_id,
                "client_secret": client_secret
            }
            save_tokens(tokens)
            print(f"Token refreshed successfully. New expiry: {datetime.fromtimestamp(tokens['expires_at'])}")
        else:
            raise Exception(f"Token refresh failed: {r.status_code} - {r.text}")

    else:
        print('No token refresh needed.')

    return tokens['access_token']
        