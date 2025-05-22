# Import libraries
import json
from datetime import datetime
import requests

# Utility functions
def load_tokens(path="../data/tokens.json"):
    with open(path, "r") as f:
       return json.load(f)

def save_tokens(tokens, path="../data/tokens.json"):
    with open(path, "w") as f:
        json.dump(tokens, f)

def is_token_expired(expires_at):
    if type(expires_at) == str:
        expires_at = int(float(expires_at)) # Convert to float first, then int
    else:
        expires_at # No change if it's already a number (int or float)
    return datetime.now().timestamp() >= expires_at

def refresh_token_if_needed(client_id, client_secret):
    tokens = load_tokens()

    if is_token_expired(tokens['expires_at']):
        print('Access token expired. Refreshing...')

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
                "expires_at": new_tokens['expires_at']
            }
            save_tokens(tokens)
        else:
            raise Exception(f"Token refresh failed: {r.status_code} - {r.text}")
    
    else:
        print('No token refresh needed.')
        
    return tokens['access_token']
        