"""
Database Layer for Professional Student Help Bot
SQLite-based storage with SQLAlchemy ORM
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager


@dataclass
class Account:
    """Worker account model"""
    id: Optional[int] = None
    username: str = ""
    phone: str = ""
    api_id: int = 0
    api_hash: str = ""
    session_file: str = ""
    is_active: bool = True
    last_used: Optional[datetime] = None
    messages_processed: int = 0
    error_count: int = 0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ProcessedMessage:
    """Processed message record"""
    id: Optional[int] = None
    original_chat_id: int = 0
    original_message_id: int = 0
    message_text: str = ""
    sender_username: str = ""
    sender_id: int = 0
    detected_services: str = ""  # JSON serialized list
    confidence_score: float = 0.0
    is_forwarded: bool = False
    forwarded_to_group: Optional[int] = None
    account_id: Optional[int] = None
    processed_at: datetime = None
    
    def __post_init__(self):
        if self.processed_at is None:
            self.processed_at = datetime.now()


@dataclass
class UserRecord:
    """User tracking record"""
    id: Optional[int] = None
    telegram_id: int = 0
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    is_blacklisted: bool = False
    is_whitelisted: bool = False
    messages_sent: int = 0
    help_requests: int = 0
    last_seen: datetime = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_seen is None:
            self.last_seen = datetime.now()


@dataclass
class Statistic:
    """Statistics record"""
    id: Optional[int] = None
    stat_type: str = ""  # daily, hourly, service_type, account_performance
    stat_key: str = ""
    stat_value: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class DatabaseManager:
    """Main database manager class"""
    
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Accounts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    phone TEXT UNIQUE,
                    api_id INTEGER,
                    api_hash TEXT,
                    session_file TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_used TIMESTAMP,
                    messages_processed INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Processed messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_chat_id INTEGER,
                    original_message_id INTEGER,
                    message_text TEXT,
                    sender_username TEXT,
                    sender_id INTEGER,
                    detected_services TEXT,
                    confidence_score REAL,
                    is_forwarded BOOLEAN DEFAULT FALSE,
                    forwarded_to_group INTEGER,
                    account_id INTEGER,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            """)
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_blacklisted BOOLEAN DEFAULT FALSE,
                    is_whitelisted BOOLEAN DEFAULT FALSE,
                    messages_sent INTEGER DEFAULT 0,
                    help_requests INTEGER DEFAULT 0,
                    last_seen TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_type TEXT,
                    stat_key TEXT,
                    stat_value TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE,
                    setting_value TEXT,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    # Account Management Methods
    def add_account(self, account: Account) -> int:
        """Add new worker account"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO accounts (username, phone, api_id, api_hash, session_file, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                account.username, account.phone, account.api_id, 
                account.api_hash, account.session_file, account.is_active
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_accounts(self, active_only: bool = True) -> List[Account]:
        """Get all accounts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM accounts"
            params = []
            
            if active_only:
                query += " WHERE is_active = ?"
                params.append(True)
            
            query += " ORDER BY last_used ASC"
            cursor.execute(query, params)
            
            return [Account(**dict(row)) for row in cursor.fetchall()]
    
    def update_account_stats(self, account_id: int, messages_processed: int = 0, error_increment: int = 0):
        """Update account statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE accounts 
                SET messages_processed = messages_processed + ?,
                    error_count = error_count + ?,
                    last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (messages_processed, error_increment, account_id))
            conn.commit()
    
    def deactivate_account(self, account_id: int):
        """Deactivate an account"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE accounts SET is_active = FALSE WHERE id = ?", (account_id,))
            conn.commit()
    
    # Message Processing Methods
    def save_processed_message(self, message: ProcessedMessage) -> int:
        """Save processed message record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processed_messages (
                    original_chat_id, original_message_id, message_text,
                    sender_username, sender_id, detected_services,
                    confidence_score, is_forwarded, forwarded_to_group, account_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message.original_chat_id, message.original_message_id,
                message.message_text, message.sender_username, message.sender_id,
                message.detected_services, message.confidence_score,
                message.is_forwarded, message.forwarded_to_group, message.account_id
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_recent_messages(self, limit: int = 100) -> List[ProcessedMessage]:
        """Get recent processed messages"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM processed_messages 
                ORDER BY processed_at DESC 
                LIMIT ?
            """, (limit,))
            
            return [ProcessedMessage(**dict(row)) for row in cursor.fetchall()]
    
    # User Management Methods
    def get_or_create_user(self, telegram_id: int, username: str = "", 
                          first_name: str = "", last_name: str = "") -> UserRecord:
        """Get existing user or create new one"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            row = cursor.fetchone()
            
            if row:
                # Update last seen
                cursor.execute("""
                    UPDATE users SET last_seen = CURRENT_TIMESTAMP,
                                   username = ?, first_name = ?, last_name = ?
                    WHERE telegram_id = ?
                """, (username, first_name, last_name, telegram_id))
                conn.commit()
                return UserRecord(**dict(row))
            else:
                # Create new user
                user = UserRecord(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                cursor.execute("""
                    INSERT INTO users (telegram_id, username, first_name, last_name, last_seen)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (telegram_id, username, first_name, last_name))
                conn.commit()
                user.id = cursor.lastrowid
                return user
    
    def update_user_stats(self, telegram_id: int, messages_sent: int = 1, help_requests: int = 0):
        """Update user statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET messages_sent = messages_sent + ?,
                    help_requests = help_requests + ?,
                    last_seen = CURRENT_TIMESTAMP
                WHERE telegram_id = ?
            """, (messages_sent, help_requests, telegram_id))
            conn.commit()
    
    def blacklist_user(self, telegram_id: int):
        """Blacklist a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET is_blacklisted = TRUE, is_whitelisted = FALSE 
                WHERE telegram_id = ?
            """, (telegram_id,))
            conn.commit()
    
    def whitelist_user(self, telegram_id: int):
        """Whitelist a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET is_whitelisted = TRUE, is_blacklisted = FALSE 
                WHERE telegram_id = ?
            """, (telegram_id,))
            conn.commit()
    
    # Statistics Methods
    def save_statistic(self, stat_type: str, stat_key: str, stat_value: str):
        """Save statistic record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO statistics (stat_type, stat_key, stat_value)
                VALUES (?, ?, ?)
            """, (stat_type, stat_key, stat_value))
            conn.commit()
    
    def get_statistics(self, stat_type: str, hours: int = 24) -> List[Statistic]:
        """Get statistics for a specific type"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM statistics 
                WHERE stat_type = ? AND timestamp > datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
            """, (stat_type, hours))
            
            return [Statistic(**dict(row)) for row in cursor.fetchall()]
    
    # Settings Methods
    def get_setting(self, key: str, default: str = "") -> str:
        """Get setting value"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT setting_value FROM settings WHERE setting_key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default
    
    def set_setting(self, key: str, value: str, description: str = ""):
        """Set setting value"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO settings (setting_key, setting_value, description)
                VALUES (?, ?, ?)
            """, (key, value, description))
            conn.commit()
    
    # Analytics Methods
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total counts
            cursor.execute("SELECT COUNT(*) FROM accounts WHERE is_active = TRUE")
            active_accounts = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM processed_messages")
            total_messages = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM processed_messages WHERE is_forwarded = TRUE")
            forwarded_messages = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # Recent activity (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM processed_messages 
                WHERE processed_at > datetime('now', '-1 day')
            """)
            messages_24h = cursor.fetchone()[0]
            
            # Top services
            cursor.execute("""
                SELECT detected_services, COUNT(*) as count
                FROM processed_messages 
                WHERE is_forwarded = TRUE
                GROUP BY detected_services
                ORDER BY count DESC
                LIMIT 5
            """)
            top_services = [{"service": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Account performance
            cursor.execute("""
                SELECT username, messages_processed, error_count
                FROM accounts 
                WHERE is_active = TRUE
                ORDER BY messages_processed DESC
                LIMIT 10
            """)
            account_performance = [
                {"username": row[0], "processed": row[1], "errors": row[2]} 
                for row in cursor.fetchall()
            ]
            
            return {
                "active_accounts": active_accounts,
                "total_messages": total_messages,
                "forwarded_messages": forwarded_messages,
                "total_users": total_users,
                "messages_24h": messages_24h,
                "top_services": top_services,
                "account_performance": account_performance
            }


# Global database instance
db = DatabaseManager()