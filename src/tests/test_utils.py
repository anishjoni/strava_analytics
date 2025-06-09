import unittest
from unittest.mock import patch, mock_open, Mock # Added Mock
import json
import requests # Added requests for mocking
from datetime import datetime, timedelta
from strava_analytics.utils import load_tokens, save_tokens, is_token_expired, refresh_token_if_needed # Added refresh_token_if_needed

class TestUtils(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data='{"access_token": "test_token", "expires_at": 12345}')
    @patch("json.load")
    def test_load_tokens_valid_json(self, mock_json_load, mock_file_open):
        """Tests loading tokens from a valid JSON file."""
        expected_data = {"access_token": "test_token", "expires_at": 12345}
        mock_json_load.return_value = expected_data
        
        tokens = load_tokens("dummy_path.json")
        self.assertEqual(tokens, expected_data)
        mock_file_open.assert_called_once_with("dummy_path.json", "r")
        mock_json_load.assert_called_once()

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_tokens_file_not_found(self, mock_file_open):
        """Tests handling of a non-existent file."""
        with self.assertRaises(FileNotFoundError):
            load_tokens("non_existent_path.json")
        mock_file_open.assert_called_once_with("non_existent_path.json", "r")

    @patch("builtins.open", new_callable=mock_open, read_data='This is not JSON')
    @patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "doc", 0))
    def test_load_tokens_malformed_json(self, mock_json_load, mock_file_open):
        """Tests handling of a malformed JSON file."""
        with self.assertRaises(json.JSONDecodeError):
            load_tokens("malformed_path.json")
        mock_file_open.assert_called_once_with("malformed_path.json", "r")
        mock_json_load.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_tokens_valid_data(self, mock_json_dump, mock_file_open):
        """Tests saving tokens to a file."""
        sample_tokens = {"access_token": "new_token", "expires_at": 67890}
        dummy_path = "dummy_save_path.json"

        save_tokens(sample_tokens, path=dummy_path)

        mock_file_open.assert_called_once_with(dummy_path, "w")
        # Get the file handle object that open was called with
        file_handle = mock_file_open.return_value.__enter__.return_value
        mock_json_dump.assert_called_once_with(sample_tokens, file_handle)

    # Tests for is_token_expired
    def test_is_token_expired_past_timestamp(self):
        """Tests with a timestamp clearly in the past."""
        past_timestamp = datetime.now().timestamp() - 3600  # 1 hour ago
        self.assertTrue(is_token_expired(past_timestamp))

    def test_is_token_expired_future_timestamp(self):
        """Tests with a timestamp clearly in the future."""
        future_timestamp = datetime.now().timestamp() + 3600  # 1 hour in the future
        self.assertFalse(is_token_expired(future_timestamp))

    def test_is_token_expired_current_timestamp(self):
        """Tests with the current timestamp."""
        current_timestamp = datetime.now().timestamp()
        self.assertTrue(is_token_expired(current_timestamp)) # Should be true due to >=

    def test_is_token_expired_past_timestamp_string(self):
        """Tests with a past timestamp as a string."""
        past_timestamp_str = str(datetime.now().timestamp() - 3600)
        self.assertTrue(is_token_expired(past_timestamp_str))

    def test_is_token_expired_future_timestamp_string(self):
        """Tests with a future timestamp as a string."""
        future_timestamp_str = str(datetime.now().timestamp() + 3600)
        self.assertFalse(is_token_expired(future_timestamp_str))

    # Tests for refresh_token_if_needed
    @patch('src.utils.requests.post')
    @patch('src.utils.save_tokens')
    @patch('src.utils.is_token_expired', return_value=False)
    @patch('src.utils.load_tokens')
    def test_refresh_token_not_expired(self, mock_load_tokens, mock_is_token_expired, mock_save_tokens, mock_requests_post):
        """Tests behavior when the token is not expired."""
        mock_load_tokens.return_value = {'access_token': 'original_access', 'refresh_token': 'original_refresh', 'expires_at': 123}
        
        client_id = 'test_client_id'
        client_secret = 'test_client_secret'
        
        returned_token = refresh_token_if_needed(client_id, client_secret)
        
        self.assertEqual(returned_token, 'original_access')
        mock_load_tokens.assert_called_once()
        mock_is_token_expired.assert_called_once_with(123)
        mock_requests_post.assert_not_called()
        mock_save_tokens.assert_not_called()

    @patch('src.utils.requests.post')
    @patch('src.utils.save_tokens')
    @patch('src.utils.is_token_expired', return_value=True)
    @patch('src.utils.load_tokens')
    def test_refresh_token_expired_success(self, mock_load_tokens, mock_is_token_expired, mock_save_tokens, mock_requests_post):
        """Tests behavior when the token is expired and refresh is successful."""
        original_tokens = {'access_token': 'old_access', 'refresh_token': 'old_refresh', 'expires_at': 123}
        mock_load_tokens.return_value = original_tokens
        
        new_token_data = {'access_token': 'new_access', 'refresh_token': 'new_refresh', 'expires_at': 9999999999}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = new_token_data
        mock_requests_post.return_value = mock_response
        
        client_id = 'test_client_id'
        client_secret = 'test_client_secret'
        
        returned_token = refresh_token_if_needed(client_id, client_secret)
        
        self.assertEqual(returned_token, 'new_access')
        mock_load_tokens.assert_called_once()
        mock_is_token_expired.assert_called_once_with(original_tokens['expires_at'])
        
        expected_payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': original_tokens['refresh_token']
        }
        mock_requests_post.assert_called_once_with(url="https://www.strava.com/oauth/token", params=expected_payload)
        mock_save_tokens.assert_called_once_with(new_token_data)

    @patch('src.utils.requests.post')
    @patch('src.utils.save_tokens')
    @patch('src.utils.is_token_expired', return_value=True)
    @patch('src.utils.load_tokens')
    def test_refresh_token_expired_api_error(self, mock_load_tokens, mock_is_token_expired, mock_save_tokens, mock_requests_post):
        """Tests behavior when token is expired and API refresh fails."""
        original_tokens = {'access_token': 'old_access', 'refresh_token': 'old_refresh', 'expires_at': 123}
        mock_load_tokens.return_value = original_tokens
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_requests_post.return_value = mock_response
        
        client_id = 'test_client_id'
        client_secret = 'test_client_secret'
        
        with self.assertRaises(Exception) as context:
            refresh_token_if_needed(client_id, client_secret)
        
        self.assertTrue("Token refresh failed: 401 - Unauthorized" in str(context.exception))
        mock_load_tokens.assert_called_once()
        mock_is_token_expired.assert_called_once_with(original_tokens['expires_at'])
        
        expected_payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': original_tokens['refresh_token']
        }
        mock_requests_post.assert_called_once_with(url="https://www.strava.com/oauth/token", params=expected_payload)
        mock_save_tokens.assert_not_called()

if __name__ == '__main__':
    unittest.main()
