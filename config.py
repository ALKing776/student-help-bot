"""
Enhanced Configuration Management System
Professional Bot Configuration with Dynamic Loading
"""

import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from database import db

load_dotenv()


class Config:
    """Enhanced Configuration Management Class"""
    
    # Core API Settings
    @property
    def API_ID(self) -> int:
        return int(os.getenv('API_ID', db.get_setting('api_id', '0')))

    @property
    def API_HASH(self) -> str:
        return os.getenv('API_HASH', db.get_setting('api_hash', ''))

    @property
    def PHONE(self) -> str:
        return os.getenv('PHONE', db.get_setting('phone', ''))

    @property
    def ADMIN_USER_IDS(self) -> List[int]:
        """List of admin Telegram user IDs"""
        admin_ids_str = os.getenv('ADMIN_USER_IDS', db.get_setting('admin_user_ids', ''))
        if admin_ids_str:
            return [int(x.strip()) for x in admin_ids_str.split(',')]
        return []

    # Target Group Settings
    @property
    def TARGET_GROUP_ID(self) -> int:
        return int(os.getenv('TARGET_GROUP_ID', db.get_setting('target_group_id', '0')))

    @property
    def MONITORED_GROUP_IDS(self) -> List[int]:
        """List of groups to monitor"""
        group_ids_str = os.getenv('MONITORED_GROUP_IDS', db.get_setting('monitored_group_ids', ''))
        if group_ids_str:
            return [int(x.strip()) for x in group_ids_str.split(',')]
        return []

    # Timing and Delay Settings
    @property
    def MIN_DELAY(self) -> float:
        return float(os.getenv('MIN_DELAY', db.get_setting('min_delay', '0.5')))

    @property
    def MAX_DELAY(self) -> float:
        return float(os.getenv('MAX_DELAY', db.get_setting('max_delay', '3.0')))

    @property
    def ACCOUNT_ROTATION_DELAY(self) -> float:
        """Delay between account switches"""
        return float(os.getenv('ACCOUNT_ROTATION_DELAY', db.get_setting('account_rotation_delay', '5.0')))

    # Processing Settings
    @property
    def MIN_MESSAGE_LENGTH(self) -> int:
        return int(os.getenv('MIN_MESSAGE_LENGTH', db.get_setting('min_message_length', '10')))

    @property
    def MAX_MESSAGE_LENGTH(self) -> int:
        return int(os.getenv('MAX_MESSAGE_LENGTH', db.get_setting('max_message_length', '10000')))

    @property
    def CONFIDENCE_THRESHOLD(self) -> float:
        """Minimum confidence score to forward message"""
        return float(os.getenv('CONFIDENCE_THRESHOLD', db.get_setting('confidence_threshold', '70.0')))

    # Safety and Limits
    @property
    def FLOOD_WAIT_MULTIPLIER(self) -> float:
        return float(os.getenv('FLOOD_WAIT_MULTIPLIER', db.get_setting('flood_wait_multiplier', '1.5')))

    @property
    def MAX_RETRIES(self) -> int:
        return int(os.getenv('MAX_RETRIES', db.get_setting('max_retries', '3')))

    @property
    def MESSAGES_PER_HOUR_LIMIT(self) -> int:
        """Maximum messages to process per hour per account"""
        return int(os.getenv('MESSAGES_PER_HOUR_LIMIT', db.get_setting('messages_per_hour_limit', '100')))

    @property
    def BLACKLIST_ENABLED(self) -> bool:
        return os.getenv('BLACKLIST_ENABLED', db.get_setting('blacklist_enabled', 'true')).lower() == 'true'

    @property
    def WHITELIST_ENABLED(self) -> bool:
        return os.getenv('WHITELIST_ENABLED', db.get_setting('whitelist_enabled', 'false')).lower() == 'true'

    # Dashboard Settings
    @property
    def DASHBOARD_PORT(self) -> int:
        return int(os.getenv('DASHBOARD_PORT', db.get_setting('dashboard_port', '5000')))

    @property
    def DASHBOARD_HOST(self) -> str:
        return os.getenv('DASHBOARD_HOST', db.get_setting('dashboard_host', '0.0.0.0'))

    @property
    def DASHBOARD_PASSWORD(self) -> str:
        return os.getenv('DASHBOARD_PASSWORD', db.get_setting('dashboard_password', 'admin123'))

    # Logging Settings
    @property
    def ENABLE_LOGGING(self) -> bool:
        return os.getenv('ENABLE_LOGGING', db.get_setting('enable_logging', 'true')).lower() == 'true'

    @property
    def LOG_LEVEL(self) -> str:
        return os.getenv('LOG_LEVEL', db.get_setting('log_level', 'INFO')).upper()

    @property
    def LOG_FILE(self) -> str:
        return os.getenv('LOG_FILE', db.get_setting('log_file', 'bot.log'))

    # Database Settings
    @property
    def DATABASE_PATH(self) -> str:
        return os.getenv('DATABASE_PATH', db.get_setting('database_path', 'bot_database.db'))

    # Service Keywords (can be dynamically updated)
    @property
    def SERVICE_KEYWORDS(self) -> Dict[str, List[str]]:
        """Dynamic service keywords that can be updated"""
        default_keywords = {
            'شرح': ['شرح', 'اشرح', 'فهم', 'تفسير', 'تحليل', 'توضيح'],
            'تقارير': ['تقرير', 'تقارير', 'تلخيص', 'ملخص', 'تكليف'],
            'واجبات': ['واجب', 'واجبات', 'بحث', 'بحوث', 'مشروع', 'projects'],
            'عروض': ['برزنتيشن', 'عرض', 'بوربوينت', 'presentation'],
            'تصاميم': ['تصميم', 'تصاميم', 'غرافيك', 'logo', 'banner'],
            'خرائط': ['خريطة ذهنية', 'mind map', 'خرائط ذهنية'],
            'ماجستير': ['ماجستير', 'رسالة ماجستير', 'بحث ماجستير'],
            'تخرج': ['مشروع تخرج', 'graduation project', 'تخرج'],
            'طبي': ['تقرير طبي', 'أجازة مرضية', 'شهادة مرضية'],
            'ريبورت': ['ريبورت', 'report', 'تقرير']
        }
        
        # Try to get from database
        keywords_json = db.get_setting('service_keywords')
        if keywords_json:
            try:
                return json.loads(keywords_json)
            except:
                pass
        return default_keywords

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings"""
        errors = []
        
        # Validate core settings
        if not cls().API_ID or cls().API_ID == 0:
            errors.append("API_ID is required")
        if not cls().API_HASH:
            errors.append("API_HASH is required")
        if not cls().PHONE:
            errors.append("PHONE number is required")
        if not cls().TARGET_GROUP_ID or cls().TARGET_GROUP_ID == 0:
            errors.append("TARGET_GROUP_ID is required")
            
        if errors:
            raise ValueError(f"Configuration Errors:\n" + "\n".join(f"  • {error}" for error in errors))
        
        return True

    @classmethod
    def update_setting(cls, key: str, value: Any) -> bool:
        """Update configuration setting"""
        try:
            db.set_setting(key, str(value))
            return True
        except Exception as e:
            print(f"Error updating setting {key}: {e}")
            return False

    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """Get all current settings"""
        config = cls()
        return {
            'API_ID': config.API_ID,
            'API_HASH': config.API_HASH,
            'PHONE': config.PHONE,
            'TARGET_GROUP_ID': config.TARGET_GROUP_ID,
            'ADMIN_USER_IDS': config.ADMIN_USER_IDS,
            'MONITORED_GROUP_IDS': config.MONITORED_GROUP_IDS,
            'MIN_DELAY': config.MIN_DELAY,
            'MAX_DELAY': config.MAX_DELAY,
            'CONFIDENCE_THRESHOLD': config.CONFIDENCE_THRESHOLD,
            'MESSAGES_PER_HOUR_LIMIT': config.MESSAGES_PER_HOUR_LIMIT,
            'BLACKLIST_ENABLED': config.BLACKLIST_ENABLED,
            'WHITELIST_ENABLED': config.WHITELIST_ENABLED,
            'DASHBOARD_PORT': config.DASHBOARD_PORT,
            'DASHBOARD_HOST': config.DASHBOARD_HOST,
            'DASHBOARD_PASSWORD': config.DASHBOARD_PASSWORD,
            'ENABLE_LOGGING': config.ENABLE_LOGGING,
            'LOG_LEVEL': config.LOG_LEVEL
        }

    @classmethod
    def print_config(cls):
        """Print current configuration"""
        config = cls.get_all_settings()
        print("\n" + "="*60)
        print("⚙️  PROFESSIONAL BOT CONFIGURATION")
        print("="*60)
        print(f"📱 Phone: {config['PHONE']}")
        print(f"🎯 Target Group ID: {config['TARGET_GROUP_ID']}")
        print(f"👥 Admin Users: {len(config['ADMIN_USER_IDS'])} configured")
        print(f"⏱️  Delay Range: {config['MIN_DELAY']}-{config['MAX_DELAY']}s")
        print(f"📊 Confidence Threshold: {config['CONFIDENCE_THRESHOLD']}%")
        print(f"🔢 Hourly Limit: {config['MESSAGES_PER_HOUR_LIMIT']} msgs/account")
        print(f"🛡️  Blacklist: {'Enabled' if config['BLACKLIST_ENABLED'] else 'Disabled'}")
        print(f"✅ Whitelist: {'Enabled' if config['WHITELIST_ENABLED'] else 'Disabled'}")
        print(f"🖥️  Dashboard: {config['DASHBOARD_HOST']}:{config['DASHBOARD_PORT']}")
        print(f"📝 Logging: {config['LOG_LEVEL']} level")
        print("="*60 + "\n")

    @classmethod
    def load_from_env_file(cls, env_file_path: str = '.env'):
        """Load configuration from .env file"""
        if os.path.exists(env_file_path):
            load_dotenv(env_file_path, override=True)
            print(f"✅ Loaded configuration from {env_file_path}")
        else:
            print(f"⚠️  Environment file {env_file_path} not found")


# Global config instance
config = Config()
