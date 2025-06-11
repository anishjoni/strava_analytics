# -*- coding: utf-8 -*-
# Import libraries
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import requests

from prefect.blocks.system import Secret
from prefect.variables import Variable
from prefect import get_run_logger

# Add the project root to Python path to avoid relative import issues

from strava_analytics.config import settings

# Note: get_run_logger() should only be called within flow/task context
# We'll get the logger in each function instead

# Define your Prefect Variable name for storing tokens
TOKEN_DATA_VARIABLE_NAME = "strava-auth-token"

# Utility functions
def load_tokens() -> Dict[str, Any]:
    """Load Strava tokens from the Prefect Variable."""
    try:
        # Only get logger if we're in a flow/task context
        try:
            logger = get_run_logger()
            logger.info(f"Attempting to load tokens from Prefect Variable: {TOKEN_DATA_VARIABLE_NAME}")
        except:
            # If no context, use print for debugging
            print(f"Attempting to load tokens from Prefect Variable: {TOKEN_DATA_VARIABLE_NAME}")
            logger = None

        token_json = Variable.get(TOKEN_DATA_VARIABLE_NAME)
        if token_json is None:
            if logger:
                logger.warning(f"Prefect Variable '{TOKEN_DATA_VARIABLE_NAME}' not found. No existing token found.")
            else:
                print(f"Prefect Variable '{TOKEN_DATA_VARIABLE_NAME}' not found. No existing token found.")
            return {}

        # Parse the JSON string to dictionary
        if isinstance(token_json, str):
            # Check if the string is empty or whitespace
            if not token_json.strip():
                if logger:
                    logger.warning(f"Prefect Variable '{TOKEN_DATA_VARIABLE_NAME}' contains empty string.")
                else:
                    print(f"Prefect Variable '{TOKEN_DATA_VARIABLE_NAME}' contains empty string.")
                return {}
            try:
                tokens = json.loads(token_json)
            except json.JSONDecodeError as e:
                if logger:
                    logger.error(f"Invalid JSON in Prefect Variable '{TOKEN_DATA_VARIABLE_NAME}': {e}")
                else:
                    print(f"Invalid JSON in Prefect Variable '{TOKEN_DATA_VARIABLE_NAME}': {e}")
                return {}
        elif isinstance(token_json, dict):
            tokens = token_json
        else:
            if logger:
                logger.warning(f"Unexpected token data type: {type(token_json)}")
            else:
                print(f"Unexpected token data type: {type(token_json)}")
            return {}
        if not tokens: # If the variable is empty JSON {}
            if logger:
                logger.warning(f"Prefect Variable '{TOKEN_DATA_VARIABLE_NAME}' is empty. No existing token found.")
            else:
                print(f"Prefect Variable '{TOKEN_DATA_VARIABLE_NAME}' is empty. No existing token found.")
            return {}
        if logger:
            logger.info(f"Successfully loaded token data from variable. Keys: {list(tokens.keys())}")
        else:
            print(f"Successfully loaded token data from variable. Keys: {list(tokens.keys())}")
        return tokens
    except Exception as e:
        try:
            logger = get_run_logger()
            logger.error(f"Failed to load tokens from Prefect Variable '{TOKEN_DATA_VARIABLE_NAME}': {e}")
        except:
            print(f"Failed to load tokens from Prefect Variable '{TOKEN_DATA_VARIABLE_NAME}': {e}")
        # If the variable itself doesn't exist, this will also catch it
        return {} #

def save_tokens(tokens: Dict[str, Any], path: Optional[str] = None) -> None:
    """Save Strava tokens to the Prefect Variable."""
    try:
        # Only get logger if we're in a flow/task context
        try:
            logger = get_run_logger()
            logger.info(f"Attempting to save tokens to Prefect Variable: {TOKEN_DATA_VARIABLE_NAME}")
        except:
            # If no context, use print for debugging
            print(f"Attempting to save tokens to Prefect Variable: {TOKEN_DATA_VARIABLE_NAME}")
            logger = None

        # Convert tokens dictionary to JSON string
        token_json = json.dumps(tokens)
        # Save to Prefect Variable
        Variable.set(name=TOKEN_DATA_VARIABLE_NAME, value=token_json, overwrite=True)
        if logger:
            logger.info(f"Successfully saved new token data to Prefect Variable: {TOKEN_DATA_VARIABLE_NAME}")
        else:
            print(f"Successfully saved new token data to Prefect Variable: {TOKEN_DATA_VARIABLE_NAME}")
    except Exception as e:
        try:
            logger = get_run_logger()
            logger.error(f"Failed to save tokens to Prefect Variable '{TOKEN_DATA_VARIABLE_NAME}': {e}")
        except:
            print(f"Failed to save tokens to Prefect Variable '{TOKEN_DATA_VARIABLE_NAME}': {e}")
        raise # Critical failure if we can't save the token

def is_token_expired(expires_at: Any, buffer_minutes: int = 0) -> bool:
    """Check if token is expired or will expire within buffer_minutes."""
    if isinstance(expires_at, str):
        expires_at = int(float(expires_at))

    # Add buffer to check if token will expire soon
    buffer_seconds = buffer_minutes * 60
    current_time = datetime.now().timestamp()

    return current_time >= (expires_at - buffer_seconds)

def will_token_expire_soon(expires_at: Any, buffer_minutes: Optional[int] = None) -> bool:
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
        