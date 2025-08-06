#!/usr/bin/env python3
"""
Quinfall API Client for syncing storage data with official game servers
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIEndpoint(Enum):
    """Quinfall API endpoints"""
    # Authentication
    LOGIN = "/auth/login"
    REFRESH_TOKEN = "/auth/refresh"
    LOGOUT = "/auth/logout"
    
    # Player data
    PLAYER_INFO = "/player/info"
    PLAYER_STORAGE = "/player/storage"
    PLAYER_INVENTORY = "/player/inventory"
    
    # Storage operations
    STORAGE_SYNC = "/storage/sync"
    STORAGE_UPDATE = "/storage/update"
    STORAGE_LOCATIONS = "/storage/locations"
    
    # Market data
    MARKET_PRICES = "/market/prices"
    MARKET_HISTORY = "/market/history"

@dataclass
class APIConfig:
    """Configuration for Quinfall API client"""
    base_url: str = "https://api.thequinfall.com/v1"  # Official API URL (when available)
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Authentication
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    
    # Sync settings
    auto_sync_interval: int = 300  # 5 minutes
    sync_on_startup: bool = True
    sync_on_shutdown: bool = True
    
    # Cache settings
    cache_duration: int = 60  # 1 minute
    enable_cache: bool = True

class QuinfallAPIClient:
    """
    Official Quinfall API client for syncing storage data
    
    This client handles:
    - Authentication with Quinfall servers
    - Storage data synchronization
    - Market price updates
    - Player data sync
    - Error handling and retry logic
    """
    
    def __init__(self, config: APIConfig = None):
        self.config = config or APIConfig()
        self.session = requests.Session()
        self.session.timeout = self.config.timeout
        
        # Authentication state
        self.authenticated = False
        self.last_auth_time = None
        self.token_expires_at = None
        
        # Cache
        self.cache = {}
        self.cache_timestamps = {}
        
        # Load saved credentials
        self._load_credentials()
        
        logger.info("🔌 Quinfall API Client initialized")
    
    def _load_credentials(self):
        """Load saved API credentials"""
        try:
            creds_file = Path("saves/api_credentials.json")
            if creds_file.exists():
                with open(creds_file, 'r') as f:
                    creds = json.load(f)
                    self.config.access_token = creds.get('access_token')
                    self.config.refresh_token = creds.get('refresh_token')
                    self.config.api_key = creds.get('api_key')
                    logger.info("📋 Loaded saved API credentials")
        except Exception as e:
            logger.warning(f"⚠️ Could not load credentials: {e}")
    
    def _save_credentials(self):
        """Save API credentials securely"""
        try:
            creds_file = Path("saves/api_credentials.json")
            creds_file.parent.mkdir(exist_ok=True)
            
            creds = {
                'access_token': self.config.access_token,
                'refresh_token': self.config.refresh_token,
                'api_key': self.config.api_key,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(creds_file, 'w') as f:
                json.dump(creds, f, indent=2)
                
            logger.info("💾 Saved API credentials")
        except Exception as e:
            logger.error(f"❌ Could not save credentials: {e}")
    
    def _make_request(self, method: str, endpoint: APIEndpoint, data: Dict = None, params: Dict = None) -> Tuple[bool, Dict]:
        """
        Make authenticated API request with retry logic
        
        Returns:
            Tuple[bool, Dict]: (success, response_data)
        """
        url = f"{self.config.base_url}{endpoint.value}"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'QuinfallCompanion/1.0'
        }
        
        # Add authentication
        if self.config.access_token:
            headers['Authorization'] = f'Bearer {self.config.access_token}'
        elif self.config.api_key:
            headers['X-API-Key'] = self.config.api_key
        
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"🌐 API Request: {method.upper()} {endpoint.value} (attempt {attempt + 1})")
                
                if method.lower() == 'get':
                    response = self.session.get(url, headers=headers, params=params)
                elif method.lower() == 'post':
                    response = self.session.post(url, headers=headers, json=data)
                elif method.lower() == 'put':
                    response = self.session.put(url, headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle response
                if response.status_code == 200:
                    logger.info(f"✅ API request successful")
                    return True, response.json()
                elif response.status_code == 401:
                    logger.warning("🔒 Authentication failed, attempting to refresh token")
                    if self._refresh_token():
                        continue  # Retry with new token
                    else:
                        return False, {'error': 'Authentication failed'}
                elif response.status_code == 429:
                    logger.warning("⏱️ Rate limited, waiting before retry")
                    import time
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                else:
                    logger.error(f"❌ API request failed: {response.status_code} - {response.text}")
                    return False, {'error': f'HTTP {response.status_code}', 'details': response.text}
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"🌐 Network error (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    import time
                    time.sleep(self.config.retry_delay)
                    continue
                return False, {'error': 'Network error', 'details': str(e)}
        
        return False, {'error': 'Max retries exceeded'}
    
    def authenticate(self, username: str = None, password: str = None, api_key: str = None) -> bool:
        """
        Authenticate with Quinfall API
        
        Args:
            username: Game username
            password: Game password
            api_key: API key (alternative to username/password)
        
        Returns:
            bool: Authentication success
        """
        try:
            if api_key:
                # API key authentication
                self.config.api_key = api_key
                self.authenticated = True
                self._save_credentials()
                logger.info("🔑 Authenticated with API key")
                return True
            
            elif username and password:
                # Username/password authentication
                auth_data = {
                    'username': username,
                    'password': password
                }
                
                success, response = self._make_request('POST', APIEndpoint.LOGIN, data=auth_data)
                
                if success:
                    self.config.access_token = response.get('access_token')
                    self.config.refresh_token = response.get('refresh_token')
                    self.authenticated = True
                    self.last_auth_time = datetime.now()
                    
                    # Calculate token expiry
                    expires_in = response.get('expires_in', 3600)  # Default 1 hour
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    self._save_credentials()
                    logger.info("🔐 Authenticated with username/password")
                    return True
                else:
                    logger.error(f"❌ Authentication failed: {response}")
                    return False
            
            else:
                logger.error("❌ No authentication credentials provided")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def _refresh_token(self) -> bool:
        """Refresh access token using refresh token"""
        if not self.config.refresh_token:
            return False
        
        try:
            refresh_data = {'refresh_token': self.config.refresh_token}
            success, response = self._make_request('POST', APIEndpoint.REFRESH_TOKEN, data=refresh_data)
            
            if success:
                self.config.access_token = response.get('access_token')
                self.config.refresh_token = response.get('refresh_token', self.config.refresh_token)
                
                expires_in = response.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                self._save_credentials()
                logger.info("🔄 Token refreshed successfully")
                return True
            else:
                logger.error("❌ Token refresh failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Token refresh error: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated and token is valid"""
        if not self.authenticated:
            return False
        
        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            logger.info("🔄 Token expired, attempting refresh")
            return self._refresh_token()
        
        return True
    
    def get_player_storage(self, player_id: str = None) -> Tuple[bool, Dict]:
        """
        Get player storage data from API
        
        Returns:
            Tuple[bool, Dict]: (success, storage_data)
        """
        if not self.is_authenticated():
            return False, {'error': 'Not authenticated'}
        
        params = {}
        if player_id:
            params['player_id'] = player_id
        
        return self._make_request('GET', APIEndpoint.PLAYER_STORAGE, params=params)
    
    def update_player_storage(self, storage_data: Dict, player_id: str = None) -> Tuple[bool, Dict]:
        """
        Update player storage data via API
        
        Args:
            storage_data: Storage data to sync
            player_id: Player ID (optional)
        
        Returns:
            Tuple[bool, Dict]: (success, response)
        """
        if not self.is_authenticated():
            return False, {'error': 'Not authenticated'}
        
        sync_data = {
            'storage_data': storage_data,
            'timestamp': datetime.now().isoformat()
        }
        
        if player_id:
            sync_data['player_id'] = player_id
        
        return self._make_request('POST', APIEndpoint.STORAGE_SYNC, data=sync_data)
    
    def get_market_prices(self, materials: List[str] = None) -> Tuple[bool, Dict]:
        """
        Get current market prices from API
        
        Args:
            materials: List of material names to get prices for
        
        Returns:
            Tuple[bool, Dict]: (success, price_data)
        """
        # Check cache first
        cache_key = f"market_prices_{','.join(materials) if materials else 'all'}"
        if self.config.enable_cache and cache_key in self.cache:
            cache_time = self.cache_timestamps.get(cache_key)
            if cache_time and (datetime.now() - cache_time).seconds < self.config.cache_duration:
                logger.info("📋 Using cached market prices")
                return True, self.cache[cache_key]
        
        params = {}
        if materials:
            params['materials'] = ','.join(materials)
        
        success, response = self._make_request('GET', APIEndpoint.MARKET_PRICES, params=params)
        
        # Cache successful responses
        if success and self.config.enable_cache:
            self.cache[cache_key] = response
            self.cache_timestamps[cache_key] = datetime.now()
        
        return success, response
    
    def sync_storage_with_game(self, storage_system) -> Tuple[bool, str]:
        """
        Sync local storage system with game API
        
        Args:
            storage_system: QuinfallStorageSystem instance
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if not self.is_authenticated():
                return False, "❌ Not authenticated with Quinfall API"
            
            logger.info("🔄 Starting storage sync with Quinfall API...")
            
            # Get current storage data from API
            success, api_storage = self.get_player_storage()
            
            if not success:
                return False, f"❌ Failed to get storage data from API: {api_storage.get('error', 'Unknown error')}"
            
            # Compare and merge storage data
            sync_summary = self._merge_storage_data(storage_system, api_storage)
            
            # Upload updated storage data to API
            local_storage_data = storage_system.to_api_format()
            success, response = self.update_player_storage(local_storage_data)
            
            if not success:
                return False, f"❌ Failed to update storage on API: {response.get('error', 'Unknown error')}"
            
            # Mark all containers as synced
            for location in storage_system.containers.keys():
                storage_system.mark_container_synced(location, datetime.now().isoformat())
            
            storage_system.save()
            
            logger.info("✅ Storage sync completed successfully")
            return True, f"✅ Storage synced successfully. {sync_summary}"
            
        except Exception as e:
            logger.error(f"❌ Storage sync error: {e}")
            return False, f"❌ Storage sync failed: {str(e)}"
    
    def _merge_storage_data(self, local_storage, api_storage: Dict) -> str:
        """
        Merge local and API storage data, resolving conflicts
        
        Returns:
            str: Summary of merge operations
        """
        conflicts_resolved = 0
        items_updated = 0
        
        # Simple merge strategy: API data takes precedence for conflicts
        # In a real implementation, you might want more sophisticated conflict resolution
        
        api_containers = api_storage.get('containers', {})
        
        for location_name, api_container in api_containers.items():
            try:
                from data.storage_system import StorageLocation
                location = StorageLocation(location_name)
                
                local_container = local_storage.get_container(location)
                api_items = api_container.get('items', {})
                
                for material_id, api_quantity in api_items.items():
                    local_quantity = local_container.items.get(material_id, 0)
                    
                    if local_quantity != api_quantity:
                        conflicts_resolved += 1
                        local_container.items[material_id] = api_quantity
                        items_updated += 1
                        
            except ValueError:
                # Unknown location, skip
                continue
        
        return f"Updated {items_updated} items, resolved {conflicts_resolved} conflicts"
    
    def disconnect(self):
        """Disconnect from API and cleanup"""
        if self.authenticated and self.config.access_token:
            try:
                self._make_request('POST', APIEndpoint.LOGOUT)
            except:
                pass  # Ignore logout errors
        
        self.authenticated = False
        self.session.close()
        logger.info("🔌 Disconnected from Quinfall API")


# Convenience functions for easy integration
def create_api_client(username: str = None, password: str = None, api_key: str = None) -> QuinfallAPIClient:
    """Create and authenticate API client"""
    client = QuinfallAPIClient()
    
    if username and password:
        client.authenticate(username, password)
    elif api_key:
        client.authenticate(api_key=api_key)
    
    return client

def test_api_connection() -> bool:
    """Test API connection without authentication"""
    try:
        client = QuinfallAPIClient()
        # Try a simple request that doesn't require auth
        response = requests.get(f"{client.config.base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False
