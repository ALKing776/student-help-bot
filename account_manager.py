"""
Multi-Account Management System
Handles pool of worker accounts for distributed message processing
"""

import asyncio
import random
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.errors import FloodWaitError, AuthKeyUnregisteredError
from dataclasses import dataclass
from database import db, Account
from config import config
import logging

logger = logging.getLogger(__name__)


@dataclass
class AccountStatus:
    """Account health and performance status"""
    account_id: int
    username: str
    is_active: bool
    is_connected: bool
    last_used: Optional[datetime]
    messages_processed: int
    error_count: int
    current_load: int  # Messages being processed
    last_error: Optional[str]
    next_available: Optional[datetime]


class AccountManager:
    """Manages multiple Telegram accounts for load distribution"""
    
    def __init__(self):
        self.accounts: Dict[int, TelegramClient] = {}
        self.account_status: Dict[int, AccountStatus] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.active_sessions: int = 0
        self.max_concurrent_sessions: int = 10  # Limit concurrent sessions
        self.rotation_index: int = 0
        
    async def initialize_accounts(self) -> bool:
        """Initialize all configured accounts"""
        try:
            # Get active accounts from database
            db_accounts = db.get_accounts(active_only=True)
            
            if not db_accounts:
                logger.warning("⚠️  No active accounts found in database")
                return False
            
            logger.info(f"🔄 Initializing {len(db_accounts)} accounts...")
            
            initialized_count = 0
            for acc in db_accounts:
                if await self.add_account(acc):
                    initialized_count += 1
            
            logger.info(f"✅ Successfully initialized {initialized_count}/{len(db_accounts)} accounts")
            return initialized_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize accounts: {e}")
            return False
    
    async def add_account(self, account: Account) -> bool:
        """Add and connect a new account"""
        try:
            # Create Telegram client
            client = TelegramClient(
                account.session_file or f"sessions/{account.username}",
                account.api_id,
                account.api_hash
            )
            
            # Connect and authenticate
            await client.start(phone=account.phone)
            
            if not await client.is_user_authorized():
                logger.warning(f"⚠️  Account {account.username} not authorized")
                return False
            
            # Store client and status
            self.accounts[account.id] = client
            self.account_status[account.id] = AccountStatus(
                account_id=account.id,
                username=account.username,
                is_active=True,
                is_connected=True,
                last_used=account.last_used,
                messages_processed=account.messages_processed,
                error_count=account.error_count,
                current_load=0,
                last_error=None,
                next_available=None
            )
            
            logger.info(f"✅ Account {account.username} connected successfully")
            return True
            
        except FloodWaitError as e:
            wait_time = e.seconds
            logger.warning(f"⏳ Account {account.username} rate limited for {wait_time}s")
            self._set_account_unavailable(account.id, wait_time)
            return False
        except Exception as e:
            logger.error(f"❌ Failed to add account {account.username}: {e}")
            return False
    
    def _set_account_unavailable(self, account_id: int, wait_seconds: int):
        """Mark account as temporarily unavailable"""
        if account_id in self.account_status:
            status = self.account_status[account_id]
            status.next_available = datetime.now() + timedelta(seconds=wait_seconds)
            status.is_connected = False
            status.last_error = f"FloodWait for {wait_seconds} seconds"
    
    async def get_available_account(self) -> Optional[tuple[int, TelegramClient]]:
        """Get next available account using round-robin with health checks"""
        if not self.accounts:
            logger.warning("⚠️  No accounts available")
            return None
        
        # Try accounts in round-robin order
        account_ids = list(self.accounts.keys())
        start_index = self.rotation_index
        
        for i in range(len(account_ids)):
            index = (start_index + i) % len(account_ids)
            account_id = account_ids[index]
            status = self.account_status.get(account_id)
            
            if not status or not status.is_active:
                continue
            
            # Check if account is connected and available
            if status.is_connected:
                client = self.accounts[account_id]
                if client.is_connected():
                    # Update rotation index for next call
                    self.rotation_index = (index + 1) % len(account_ids)
                    status.current_load += 1
                    return account_id, client
            
            # Check if rate-limited account is now available
            elif status.next_available and datetime.now() >= status.next_available:
                if await self._reconnect_account(account_id):
                    self.rotation_index = (index + 1) % len(account_ids)
                    status.current_load += 1
                    return account_id, self.accounts[account_id]
        
        logger.warning("⚠️  No available accounts found")
        return None
    
    async def _reconnect_account(self, account_id: int) -> bool:
        """Attempt to reconnect a disconnected account"""
        try:
            status = self.account_status[account_id]
            client = self.accounts[account_id]
            
            # Disconnect first
            await client.disconnect()
            
            # Reconnect
            await client.connect()
            
            if await client.is_user_authorized():
                status.is_connected = True
                status.next_available = None
                status.last_error = None
                logger.info(f"✅ Account {status.username} reconnected successfully")
                return True
            else:
                logger.warning(f"⚠️  Account {status.username} authorization lost")
                status.is_active = False
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to reconnect account {account_id}: {e}")
            if account_id in self.account_status:
                self.account_status[account_id].last_error = str(e)
            return False
    
    async def release_account(self, account_id: int, success: bool = True, error_msg: str = None):
        """Release account after use and update statistics"""
        if account_id in self.account_status:
            status = self.account_status[account_id]
            status.current_load = max(0, status.current_load - 1)
            
            if success:
                status.messages_processed += 1
                db.update_account_stats(account_id, messages_processed=1)
            else:
                status.error_count += 1
                status.last_error = error_msg
                db.update_account_stats(account_id, error_increment=1)
            
            status.last_used = datetime.now()
    
    async def handle_flood_wait(self, account_id: int, wait_seconds: int):
        """Handle FloodWaitError for specific account"""
        logger.warning(f"⏳ Handling FloodWait for account {account_id}: {wait_seconds}s")
        self._set_account_unavailable(account_id, wait_seconds)
        
        # Try to switch to another account immediately
        return await self.get_available_account()
    
    def get_account_stats(self) -> List[Dict[str, Any]]:
        """Get comprehensive account statistics"""
        stats = []
        for account_id, status in self.account_status.items():
            client = self.accounts.get(account_id)
            
            stats.append({
                'id': account_id,
                'username': status.username,
                'is_active': status.is_active,
                'is_connected': status.is_connected,
                'current_load': status.current_load,
                'messages_processed': status.messages_processed,
                'error_count': status.error_count,
                'last_used': status.last_used.isoformat() if status.last_used else None,
                'next_available': status.next_available.isoformat() if status.next_available else None,
                'last_error': status.last_error,
                'is_client_connected': client.is_connected() if client else False
            })
        return stats
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall account pool health"""
        total_accounts = len(self.account_status)
        active_accounts = sum(1 for s in self.account_status.values() if s.is_active)
        connected_accounts = sum(1 for s in self.account_status.values() if s.is_connected)
        total_load = sum(s.current_load for s in self.account_status.values())
        
        return {
            'total_accounts': total_accounts,
            'active_accounts': active_accounts,
            'connected_accounts': connected_accounts,
            'disconnected_accounts': active_accounts - connected_accounts,
            'total_current_load': total_load,
            'average_load_per_account': total_load / active_accounts if active_accounts > 0 else 0,
            'health_percentage': (connected_accounts / active_accounts * 100) if active_accounts > 0 else 0
        }
    
    async def add_new_account(self, phone: str, api_id: int, api_hash: str, 
                            username: str = None) -> Optional[int]:
        """Add a new account to the system"""
        try:
            # Create account record
            account = Account(
                username=username or f"worker_{int(time.time())}",
                phone=phone,
                api_id=api_id,
                api_hash=api_hash,
                session_file=f"sessions/{username or f'worker_{int(time.time())}'}"
            )
            
            # Save to database
            account_id = db.add_account(account)
            account.id = account_id
            
            # Try to connect
            if await self.add_account(account):
                logger.info(f"✅ New account {account.username} added successfully")
                return account_id
            else:
                logger.error(f"❌ Failed to connect new account {account.username}")
                db.deactivate_account(account_id)
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to add new account: {e}")
            return None
    
    async def remove_account(self, account_id: int) -> bool:
        """Remove account from system"""
        try:
            # Disconnect client
            if account_id in self.accounts:
                client = self.accounts[account_id]
                await client.disconnect()
                del self.accounts[account_id]
            
            # Remove from status tracking
            if account_id in self.account_status:
                del self.account_status[account_id]
            
            # Deactivate in database
            db.deactivate_account(account_id)
            
            logger.info(f"🗑️  Account {account_id} removed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove account {account_id}: {e}")
            return False
    
    async def distribute_message_processing(self, message_data: Dict[str, Any]) -> bool:
        """Distribute message processing across available accounts"""
        account_result = await self.get_available_account()
        
        if not account_result:
            logger.error("❌ No available accounts for message processing")
            return False
        
        account_id, client = account_result
        
        try:
            # Process message using the selected account
            # This would integrate with your existing message processing logic
            # For now, simulate processing
            await asyncio.sleep(random.uniform(config.MIN_DELAY, config.MAX_DELAY))
            
            # Release account
            await self.release_account(account_id, success=True)
            
            logger.info(f"✅ Message processed using account {account_id}")
            return True
            
        except FloodWaitError as e:
            # Handle rate limiting
            new_account_result = await self.handle_flood_wait(account_id, e.seconds)
            if new_account_result:
                # Retry with different account
                return await self.distribute_message_processing(message_data)
            else:
                await self.release_account(account_id, success=False, error_msg=str(e))
                return False
        except Exception as e:
            logger.error(f"❌ Error processing message with account {account_id}: {e}")
            await self.release_account(account_id, success=False, error_msg=str(e))
            return False
    
    async def cleanup(self):
        """Clean up all connections"""
        logger.info("🧹 Cleaning up account connections...")
        
        for account_id, client in self.accounts.items():
            try:
                await client.disconnect()
                logger.info(f"🔌 Disconnected account {account_id}")
            except Exception as e:
                logger.error(f"❌ Error disconnecting account {account_id}: {e}")
        
        self.accounts.clear()
        self.account_status.clear()
        logger.info("✅ Account cleanup completed")


# Global account manager instance
account_manager = AccountManager()