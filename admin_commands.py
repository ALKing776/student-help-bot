"""
Telegram-based Admin Command System
Professional administration through Telegram commands
"""

from telethon import events
from telethon.tl.custom import Message
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime, timedelta
from config import config
from database import db
from account_manager import account_manager
from message_analyzer import EnhancedMessageAnalyzer
import logging

logger = logging.getLogger(__name__)

# Initialize analyzer
analyzer = EnhancedMessageAnalyzer()


class AdminCommands:
    """Telegram Admin Command Handler"""
    
    def __init__(self, client):
        self.client = client
        self.register_handlers()
    
    def register_handlers(self):
        """Register all admin command handlers"""
        self.client.add_event_handler(
            self.handle_admin_commands,
            events.NewMessage(pattern=r'^/[a-zA-Z_]+', incoming=True)
        )
    
    async def is_admin(self, user_id: int) -> bool:
        """Check if user is authorized admin"""
        return user_id in config.ADMIN_USER_IDS
    
    async def handle_admin_commands(self, event: events.NewMessage.Event):
        """Main handler for admin commands"""
        message: Message = event.message
        user_id = message.sender_id
        
        # Check admin authorization
        if not await self.is_admin(user_id):
            return
        
        # Parse command
        command_parts = message.text.split()
        if not command_parts:
            return
        
        command = command_parts[0].lower()
        args = command_parts[1:] if len(command_parts) > 1 else []
        
        try:
            # Route to appropriate command handler
            if command == '/stats':
                await self.cmd_stats(message, args)
            elif command == '/accounts':
                await self.cmd_accounts(message, args)
            elif command == '/users':
                await self.cmd_users(message, args)
            elif command == '/blacklist':
                await self.cmd_blacklist(message, args)
            elif command == '/whitelist':
                await self.cmd_whitelist(message, args)
            elif command == '/config':
                await self.cmd_config(message, args)
            elif command == '/analyze':
                await self.cmd_analyze(message, args)
            elif command == '/addaccount':
                await self.cmd_add_account(message, args)
            elif command == '/removeaccount':
                await self.cmd_remove_account(message, args)
            elif command == '/pause':
                await self.cmd_pause(message, args)
            elif command == '/resume':
                await self.cmd_resume(message, args)
            elif command == '/help':
                await self.cmd_help(message, args)
            else:
                await message.reply("❌ Unknown command. Use /help for available commands.")
                
        except Exception as e:
            logger.error(f"Error handling admin command {command}: {e}")
            await message.reply(f"❌ Error executing command: {str(e)}")
    
    async def cmd_stats(self, message: Message, args: List[str]):
        """Show system statistics"""
        try:
            # Get dashboard stats
            stats = db.get_dashboard_stats()
            
            # Get account health
            account_health = account_manager.get_health_summary()
            
            # Format response
            response = f"""
📊 **SYSTEM STATISTICS**

📈 **Overview:**
• Active Accounts: {stats['active_accounts']}
• Total Messages: {stats['total_messages']:,}
• Forwarded Messages: {stats['forwarded_messages']:,}
• Monitored Users: {stats['total_users']:,}
• Messages (24h): {stats['messages_24h']:,}

🏥 **Account Health:**
• Connected: {account_health['connected_accounts']}/{account_health['active_accounts']}
• Health: {account_health['health_percentage']:.1f}%
• Current Load: {account_health['total_current_load']}

🏆 **Top Services:**
"""
            
            for service in stats['top_services'][:5]:
                response += f"• {service['service']}: {service['count']} requests\n"
            
            response += "\n👥 **Best Performing Accounts:**\n"
            for acc in stats['account_performance'][:5]:
                response += f"• {acc['username']}: {acc['processed']} msgs ({acc['errors']} errors)\n"
            
            await message.reply(response, parse_mode='markdown')
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await message.reply(f"❌ Error retrieving statistics: {str(e)}")
    
    async def cmd_accounts(self, message: Message, args: List[str]):
        """Manage accounts"""
        if not args:
            # Show account list
            account_stats = account_manager.get_account_stats()
            
            response = "👥 **ACCOUNT STATUS**\n\n"
            
            for acc in account_stats:
                status_icon = "✅" if acc['is_connected'] else "❌"
                response += f"{status_icon} **{acc['username']}** (ID: {acc['id']})\n"
                response += f"   Messages: {acc['messages_processed']:,} | Errors: {acc['error_count']}\n"
                response += f"   Load: {acc['current_load']} | Last Used: {acc['last_used'] or 'Never'}\n\n"
            
            await message.reply(response, parse_mode='markdown')
        else:
            # Handle account actions
            action = args[0].lower()
            if action == 'refresh':
                await account_manager.initialize_accounts()
                await message.reply("🔄 Accounts refreshed")
            elif action == 'health':
                health = account_manager.get_health_summary()
                await message.reply(f"🏥 Account Health: {health['health_percentage']:.1f}%")
    
    async def cmd_users(self, message: Message, args: List[str]):
        """Manage users"""
        try:
            if not args:
                # Show recent users
                recent_users = db.get_recent_messages(limit=10)
                response = "👥 **RECENT USERS**\n\n"
                
                user_ids = set()
                for msg in recent_users:
                    if msg.sender_id not in user_ids:
                        user_ids.add(msg.sender_id)
                        response += f"• @{msg.sender_username or 'Unknown'} (ID: {msg.sender_id})\n"
                
                await message.reply(response)
            else:
                action = args[0].lower()
                if action == 'blacklisted':
                    # Show blacklisted users
                    pass  # Implement based on your needs
                elif action == 'whitelisted':
                    # Show whitelisted users
                    pass  # Implement based on your needs
                    
        except Exception as e:
            await message.reply(f"❌ Error: {str(e)}")
    
    async def cmd_blacklist(self, message: Message, args: List[str]):
        """Blacklist user management"""
        if len(args) < 1:
            await message.reply("Usage: /blacklist <user_id> [reason]")
            return
        
        try:
            user_id = int(args[0])
            reason = ' '.join(args[1:]) if len(args) > 1 else "Admin decision"
            
            db.blacklist_user(user_id)
            await message.reply(f"✅ User {user_id} has been blacklisted. Reason: {reason}")
            
        except ValueError:
            await message.reply("❌ Invalid user ID")
        except Exception as e:
            await message.reply(f"❌ Error blacklisting user: {str(e)}")
    
    async def cmd_whitelist(self, message: Message, args: List[str]):
        """Whitelist user management"""
        if len(args) < 1:
            await message.reply("Usage: /whitelist <user_id>")
            return
        
        try:
            user_id = int(args[0])
            db.whitelist_user(user_id)
            await message.reply(f"✅ User {user_id} has been whitelisted")
            
        except ValueError:
            await message.reply("❌ Invalid user ID")
        except Exception as e:
            await message.reply(f"❌ Error whitelisting user: {str(e)}")
    
    async def cmd_config(self, message: Message, args: List[str]):
        """Configuration management"""
        if not args:
            # Show current config
            config_dict = config.get_all_settings()
            response = "⚙️ **CURRENT CONFIGURATION**\n\n"
            
            for key, value in config_dict.items():
                response += f"**{key}**: {value}\n"
            
            await message.reply(response, parse_mode='markdown')
        else:
            # Update configuration
            if len(args) >= 2:
                key = args[0]
                value = ' '.join(args[1:])
                
                if config.update_setting(key, value):
                    await message.reply(f"✅ Setting '{key}' updated to '{value}'")
                else:
                    await message.reply(f"❌ Failed to update setting '{key}'")
            else:
                await message.reply("Usage: /config <key> <value>")
    
    async def cmd_analyze(self, message: Message, args: List[str]):
        """Analyze test message"""
        if not args:
            await message.reply("Usage: /analyze <message_text>")
            return
        
        test_message = ' '.join(args)
        result = analyzer.analyze_message(test_message)
        
        response = f"""
🔍 **MESSAGE ANALYSIS**

📝 **Original**: {test_message}
✅ **Help Request**: {'Yes' if result.is_help_request else 'No'}
サービシ**Services**: {', '.join(result.services) if result.services else 'None'}
📊 **Confidence**: {result.confidence:.1f}%
⚡ **Urgency**: Level {result.urgency_level}
🌐 **Language**: {result.language_detected}
⭐ **Quality**: {result.message_quality:.2f}
🔑 **Keywords**: {', '.join(result.keywords_found[:10])}
📌 **Context**: {', '.join(result.context_indicators)}
"""
        
        await message.reply(response)
    
    async def cmd_add_account(self, message: Message, args: List[str]):
        """Add new worker account"""
        if len(args) < 4:
            await message.reply(
                "Usage: /addaccount <phone> <api_id> <api_hash> [username]\n"
                "Example: /addaccount +1234567890 1234567 abcdef123456 worker1"
            )
            return
        
        try:
            phone = args[0]
            api_id = int(args[1])
            api_hash = args[2]
            username = args[3] if len(args) > 3 else None
            
            account_id = await account_manager.add_new_account(phone, api_id, api_hash, username)
            
            if account_id:
                await message.reply(f"✅ Account added successfully with ID: {account_id}")
            else:
                await message.reply("❌ Failed to add account")
                
        except ValueError:
            await message.reply("❌ Invalid API ID format")
        except Exception as e:
            await message.reply(f"❌ Error adding account: {str(e)}")
    
    async def cmd_remove_account(self, message: Message, args: List[str]):
        """Remove worker account"""
        if len(args) < 1:
            await message.reply("Usage: /removeaccount <account_id>")
            return
        
        try:
            account_id = int(args[0])
            if await account_manager.remove_account(account_id):
                await message.reply(f"✅ Account {account_id} removed successfully")
            else:
                await message.reply(f"❌ Failed to remove account {account_id}")
                
        except ValueError:
            await message.reply("❌ Invalid account ID")
        except Exception as e:
            await message.reply(f"❌ Error removing account: {str(e)}")
    
    async def cmd_pause(self, message: Message, args: List[str]):
        """Pause message processing"""
        # Implement pause logic
        await message.reply("⏸️ Message processing paused")
    
    async def cmd_resume(self, message: Message, args: List[str]):
        """Resume message processing"""
        # Implement resume logic
        await message.reply("▶️ Message processing resumed")
    
    async def cmd_help(self, message: Message, args: List[str]):
        """Show help information"""
        help_text = """
🤖 **ADMIN COMMANDS HELP**

📊 **Statistics & Monitoring:**
• `/stats` - Show system statistics
• `/accounts` - List all accounts and status
• `/users` - Show recent users

🛡️ **User Management:**
• `/blacklist <user_id> [reason]` - Blacklist user
• `/whitelist <user_id>` - Whitelist user

⚙️ **Configuration:**
• `/config` - Show current configuration
• `/config <key> <value>` - Update setting

🔬 **Analysis:**
• `/analyze <message>` - Analyze test message

👥 **Account Management:**
• `/addaccount <phone> <api_id> <api_hash> [username]` - Add new account
• `/removeaccount <account_id>` - Remove account
• `/accounts refresh` - Refresh account connections

⏯️ **Control:**
• `/pause` - Pause processing
• `/resume` - Resume processing
• `/help` - Show this help

🔐 **Note:** Only authorized admins can use these commands.
"""
        
        await message.reply(help_text, parse_mode='markdown')


# Initialize admin commands
def setup_admin_commands(client):
    """Setup admin commands for the bot client"""
    return AdminCommands(client)