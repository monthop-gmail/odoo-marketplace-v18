# -*- coding: utf-8 -*-
"""
LINE API Service - handles all LINE Platform API interactions
"""
import hashlib
import hmac
import base64
import json
import logging
import requests
from datetime import datetime

_logger = logging.getLogger(__name__)

# LINE API Endpoints
LINE_API_BASE = 'https://api.line.me/v2'
LINE_API_DATA = 'https://api-data.line.me/v2'
LINE_OAUTH_BASE = 'https://api.line.me/oauth2/v2.1'


class LineApiError(Exception):
    """LINE API Error"""
    def __init__(self, message, status_code=None, error_code=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class LineApiService:
    """
    LINE Messaging API Service

    Handles:
    - Push/Reply messages
    - Get user profile
    - Validate webhook signatures
    - LIFF token verification
    """

    def __init__(self, channel_access_token, channel_secret=None):
        """
        Initialize LINE API service

        Args:
            channel_access_token: LINE Channel Access Token
            channel_secret: LINE Channel Secret (for webhook signature validation)
        """
        self.channel_access_token = channel_access_token
        self.channel_secret = channel_secret
        self.headers = {
            'Authorization': f'Bearer {channel_access_token}',
            'Content-Type': 'application/json',
        }

    # ==================== Webhook Validation ====================

    def validate_signature(self, body, signature):
        """
        Validate LINE webhook signature

        Args:
            body: Request body as bytes
            signature: X-Line-Signature header value

        Returns:
            bool: True if signature is valid
        """
        if not self.channel_secret:
            _logger.warning('Channel secret not set, skipping signature validation')
            return True

        hash_value = hmac.new(
            self.channel_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).digest()

        expected_signature = base64.b64encode(hash_value).decode('utf-8')
        return hmac.compare_digest(signature, expected_signature)

    # ==================== User Profile ====================

    def get_profile(self, user_id):
        """
        Get user profile from LINE

        Args:
            user_id: LINE user ID

        Returns:
            dict: User profile {userId, displayName, pictureUrl, statusMessage}
        """
        url = f'{LINE_API_BASE}/bot/profile/{user_id}'

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to get LINE profile for {user_id}: {e}')
            raise LineApiError(f'Failed to get profile: {e}')

    def get_group_member_profile(self, group_id, user_id):
        """Get user profile in a group context"""
        url = f'{LINE_API_BASE}/bot/group/{group_id}/member/{user_id}'

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to get group member profile: {e}')
            raise LineApiError(f'Failed to get group member profile: {e}')

    # ==================== Messaging ====================

    def push_message(self, to, messages):
        """
        Send push message to user

        Args:
            to: User ID, Group ID, or Room ID
            messages: List of message objects (max 5)

        Returns:
            dict: Response from LINE API
        """
        if not isinstance(messages, list):
            messages = [messages]

        if len(messages) > 5:
            raise LineApiError('Maximum 5 messages per request')

        url = f'{LINE_API_BASE}/bot/message/push'
        data = {
            'to': to,
            'messages': messages,
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return {'success': True}
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to push message to {to}: {e}')
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    raise LineApiError(
                        error_data.get('message', str(e)),
                        e.response.status_code,
                        error_data.get('details', [{}])[0].get('property')
                    )
                except (json.JSONDecodeError, KeyError):
                    pass
            raise LineApiError(f'Failed to push message: {e}')

    def reply_message(self, reply_token, messages):
        """
        Reply to a message using reply token

        Args:
            reply_token: Reply token from webhook event
            messages: List of message objects (max 5)

        Returns:
            dict: Response from LINE API
        """
        if not isinstance(messages, list):
            messages = [messages]

        url = f'{LINE_API_BASE}/bot/message/reply'
        data = {
            'replyToken': reply_token,
            'messages': messages,
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return {'success': True}
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to reply message: {e}')
            raise LineApiError(f'Failed to reply message: {e}')

    def multicast(self, to_list, messages):
        """
        Send message to multiple users

        Args:
            to_list: List of user IDs (max 500)
            messages: List of message objects (max 5)
        """
        if len(to_list) > 500:
            raise LineApiError('Maximum 500 users per multicast')

        url = f'{LINE_API_BASE}/bot/message/multicast'
        data = {
            'to': to_list,
            'messages': messages,
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return {'success': True}
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to multicast: {e}')
            raise LineApiError(f'Failed to multicast: {e}')

    def broadcast(self, messages):
        """
        Broadcast message to all followers

        Args:
            messages: List of message objects (max 5)
        """
        url = f'{LINE_API_BASE}/bot/message/broadcast'
        data = {
            'messages': messages,
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return {'success': True}
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to broadcast: {e}')
            raise LineApiError(f'Failed to broadcast: {e}')

    # ==================== Rich Menu ====================

    def get_rich_menu_list(self):
        """Get list of rich menus"""
        url = f'{LINE_API_BASE}/bot/richmenu/list'

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get('richmenus', [])
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to get rich menu list: {e}')
            raise LineApiError(f'Failed to get rich menu list: {e}')

    def create_rich_menu(self, rich_menu_object):
        """
        Create a rich menu

        Args:
            rich_menu_object: Rich menu JSON object

        Returns:
            dict: {'richMenuId': 'richmenu-xxx'}
        """
        url = f'{LINE_API_BASE}/bot/richmenu'

        try:
            response = requests.post(
                url, headers=self.headers, json=rich_menu_object, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to create rich menu: {e}')
            if hasattr(e, 'response') and e.response is not None:
                _logger.error(f'Response: {e.response.text}')
            raise LineApiError(f'Failed to create rich menu: {e}')

    def upload_rich_menu_image(self, rich_menu_id, image_data, content_type='image/png'):
        """
        Upload image for a rich menu

        Args:
            rich_menu_id: Rich menu ID
            image_data: Image binary data
            content_type: 'image/png' or 'image/jpeg'
        """
        url = f'{LINE_API_DATA}/bot/richmenu/{rich_menu_id}/content'
        headers = {
            'Authorization': f'Bearer {self.channel_access_token}',
            'Content-Type': content_type,
        }

        try:
            response = requests.post(url, headers=headers, data=image_data, timeout=30)
            response.raise_for_status()
            return {'success': True}
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to upload rich menu image: {e}')
            if hasattr(e, 'response') and e.response is not None:
                _logger.error(f'Response: {e.response.text}')
            raise LineApiError(f'Failed to upload rich menu image: {e}')

    def set_default_rich_menu(self, rich_menu_id):
        """Set a rich menu as the default for all users"""
        url = f'{LINE_API_BASE}/bot/user/all/richmenu/{rich_menu_id}'

        try:
            response = requests.post(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return {'success': True}
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to set default rich menu: {e}')
            raise LineApiError(f'Failed to set default rich menu: {e}')

    def delete_rich_menu(self, rich_menu_id):
        """Delete a rich menu"""
        url = f'{LINE_API_BASE}/bot/richmenu/{rich_menu_id}'

        try:
            response = requests.delete(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return {'success': True}
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to delete rich menu: {e}')
            raise LineApiError(f'Failed to delete rich menu: {e}')

    def set_user_rich_menu(self, user_id, rich_menu_id):
        """Set rich menu for a specific user"""
        url = f'{LINE_API_BASE}/bot/user/{user_id}/richmenu/{rich_menu_id}'

        try:
            response = requests.post(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return {'success': True}
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to set user rich menu: {e}')
            raise LineApiError(f'Failed to set user rich menu: {e}')

    def unlink_user_rich_menu(self, user_id):
        """Remove rich menu from a specific user (reverts to default)"""
        url = f'{LINE_API_BASE}/bot/user/{user_id}/richmenu'

        try:
            response = requests.delete(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return {'success': True}
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to unlink user rich menu: {e}')
            raise LineApiError(f'Failed to unlink user rich menu: {e}')

    # ==================== LIFF Token Verification ====================

    def verify_access_token(self, access_token):
        """
        Verify LINE access token (from LIFF)

        Args:
            access_token: Access token from LIFF liff.getAccessToken()

        Returns:
            dict: Token info {scope, client_id, expires_in}
        """
        url = f'{LINE_OAUTH_BASE}/verify'
        params = {'access_token': access_token}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to verify access token: {e}')
            raise LineApiError(f'Invalid access token: {e}')

    def get_token_profile(self, access_token):
        """
        Get user profile using access token (from LIFF)

        Args:
            access_token: Access token from LIFF

        Returns:
            dict: User profile {userId, displayName, pictureUrl}
        """
        url = f'{LINE_API_BASE}/profile'
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to get profile from token: {e}')
            raise LineApiError(f'Failed to get profile: {e}')

    # ==================== Bot Info ====================

    def get_bot_info(self):
        """
        Get bot info from LINE API. Lightweight call to verify token validity.

        Returns:
            dict: Bot info {userId, basicId, displayName, pictureUrl, chatMode, markAsReadMode}
        """
        url = f'{LINE_API_BASE}/bot/info'

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to get bot info: {e}')
            raise LineApiError(f'Failed to get bot info: {e}')

    # ==================== Follower Count ====================

    def get_follower_count(self, date=None):
        """
        Get number of followers

        Args:
            date: Date string YYYYMMDD (optional, defaults to yesterday)
        """
        if not date:
            from datetime import datetime, timedelta
            date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

        url = f'{LINE_API_BASE}/bot/insight/followers'
        params = {'date': date}

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f'Failed to get follower count: {e}')
            raise LineApiError(f'Failed to get follower count: {e}')


class MockLineApiService(LineApiService):
    """
    Mock LINE API Service for testing without actual LINE API
    """

    def __init__(self, channel_access_token='mock_token', channel_secret='mock_secret'):
        super().__init__(channel_access_token, channel_secret)
        self.sent_messages = []  # Store sent messages for testing
        self.mock_profiles = {}  # Mock user profiles

    def validate_signature(self, body, signature):
        """Always return True in mock mode"""
        return True

    def get_profile(self, user_id):
        """Return mock profile"""
        if user_id in self.mock_profiles:
            return self.mock_profiles[user_id]

        return {
            'userId': user_id,
            'displayName': f'Mock User {user_id[:8]}',
            'pictureUrl': 'https://example.com/mock_avatar.png',
            'statusMessage': 'Mock status',
        }

    def push_message(self, to, messages):
        """Store message for testing"""
        if not isinstance(messages, list):
            messages = [messages]

        self.sent_messages.append({
            'type': 'push',
            'to': to,
            'messages': messages,
            'timestamp': datetime.now().isoformat(),
        })

        _logger.info(f'[MOCK] Push message to {to}: {messages}')
        return {'success': True, 'mock': True}

    def reply_message(self, reply_token, messages):
        """Store reply for testing"""
        if not isinstance(messages, list):
            messages = [messages]

        self.sent_messages.append({
            'type': 'reply',
            'reply_token': reply_token,
            'messages': messages,
            'timestamp': datetime.now().isoformat(),
        })

        _logger.info(f'[MOCK] Reply message: {messages}')
        return {'success': True, 'mock': True}

    def multicast(self, to_list, messages):
        """Store multicast for testing"""
        self.sent_messages.append({
            'type': 'multicast',
            'to': to_list,
            'messages': messages,
            'timestamp': datetime.now().isoformat(),
        })

        _logger.info(f'[MOCK] Multicast to {len(to_list)} users: {messages}')
        return {'success': True, 'mock': True}

    def verify_access_token(self, access_token):
        """Mock token verification"""
        return {
            'scope': 'profile openid',
            'client_id': 'mock_client_id',
            'expires_in': 3600,
        }

    def get_token_profile(self, access_token):
        """Mock profile from token"""
        # Extract user ID from mock token format: mock_token_USERID
        if access_token.startswith('mock_token_'):
            user_id = access_token.replace('mock_token_', '')
        else:
            user_id = 'mock_user_' + access_token[:8]

        return {
            'userId': user_id,
            'displayName': f'Mock User {user_id[:8]}',
            'pictureUrl': 'https://example.com/mock.png',
        }

    def get_sent_messages(self):
        """Get all sent messages (for testing)"""
        return self.sent_messages

    def clear_sent_messages(self):
        """Clear sent messages (for testing)"""
        self.sent_messages = []

    def add_mock_profile(self, user_id, profile):
        """Add mock profile (for testing)"""
        self.mock_profiles[user_id] = profile

    def get_bot_info(self):
        """Mock bot info"""
        return {
            'userId': 'mock_bot_user_id',
            'basicId': '@mock_bot',
            'displayName': 'Mock Bot',
            'pictureUrl': 'https://example.com/mock_bot.png',
            'chatMode': 'chat',
            'markAsReadMode': 'manual',
        }


def get_line_api_service(channel):
    """
    Factory function to create LineApiService from a line.channel record.

    Args:
        channel: line.channel recordset (ensure_one)

    Returns:
        LineApiService instance
    """
    return LineApiService(channel.channel_access_token, channel.channel_secret)
