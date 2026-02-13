"""
Enhanced Student Help Bot - Professional Version
Integrated system with multi-account management, admin dashboard, and advanced analytics
"""

import asyncio
import signal
import sys
import json
from datetime import datetime
from typing import Optional

from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# Import our enhanced components
from config import config
from database import db
from account_manager import account_manager
from message_analyzer import EnhancedMessageAnalyzer
from admin_commands import setup_admin_commands
from analytics import analytics_engine
from logger import setup_logging, logger, perf_monitor, alert_manager
from dashboard.app import start_dashboard

# Initialize logging system
setup_logging()

# Initialize analyzer
analyzer = EnhancedMessageAnalyzer()

# Global state
running = True
processed_message_count = 0


class EnhancedStudentHelpBot:
    """Enhanced professional student help bot"""
    
    def __init__(self):
        self.main_client: Optional[TelegramClient] = None
        self.admin_handler: Optional[object] = None
        self.stats_collection_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize all bot components"""
        logger.info("🚀 Initializing Enhanced Student Help Bot...")
        
        try:
            # Validate configuration
            config.validate()
            logger.info("✅ Configuration validated")
            
            # Initialize database
            logger.info("🗄️  Initializing database...")
            # Database is already initialized in database.py
            
            # Initialize account manager
            logger.info("👥 Initializing account manager...")
            await account_manager.initialize_accounts()
            
            # Initialize main client
            logger.info("📱 Initializing main Telegram client...")
            self.main_client = TelegramClient('main_session', config.API_ID, config.API_HASH)
            await self.main_client.start(phone=config.PHONE)
            
            # Setup admin commands
            logger.info("🔧 Setting up admin commands...")
            self.admin_handler = setup_admin_commands(self.main_client)
            
            # Start analytics collection
            logger.info("📊 Starting analytics collection...")
            self.stats_collection_task = asyncio.create_task(
                analytics_engine.collect_periodic_stats()
            )
            
            logger.info("✅ Bot initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error("❌ Failed to initialize bot", exception=e)
            return False
    
    async def message_handler(self, event):
        """Enhanced message handler with multi-account processing"""
        global processed_message_count
        
        try:
            message = event.message
            
            # Skip private messages
            if message.is_private:
                return
            
            # Skip already processed messages
            message_key = f"{message.chat_id}_{message.id}"
            
            # Analyze message
            analysis_result = analyzer.analyze_message(message.text or "")
            
            if analysis_result.is_help_request and analysis_result.confidence >= config.CONFIDENCE_THRESHOLD:
                logger.info(
                    "🎯 Help request detected",
                    services=analysis_result.services,
                    confidence=analysis_result.confidence,
                    urgency=analysis_result.urgency_level
                )
                
                # Distribute processing across accounts
                message_data = {
                    'original_message': message,
                    'analysis_result': analysis_result,
                    'chat_id': message.chat_id,
                    'message_id': message.id
                }
                
                success = await account_manager.distribute_message_processing(message_data)
                
                if success:
                    processed_message_count += 1
                    perf_monitor.increment_counter("messages_processed")
                    perf_monitor.increment_counter("help_requests_forwarded")
                    
                    # Save to database
                    await self.save_processed_message(message, analysis_result, True)
                    
                    logger.info("✅ Help request processed and forwarded")
                else:
                    perf_monitor.increment_counter("processing_failures")
                    await self.save_processed_message(message, analysis_result, False)
                    logger.warning("⚠️  Failed to process help request")
            
            else:
                # Save non-help requests for analytics
                await self.save_processed_message(message, analysis_result, False)
                
                # Small delay for non-help messages to reduce CPU usage
                await asyncio.sleep(0.01)
                
        except FloodWaitError as e:
            logger.warning(f"⏳ FloodWait encountered: {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error("❌ Error in message handler", exception=e)
            perf_monitor.increment_counter("handler_errors")
    
    async def save_processed_message(self, message, analysis_result, is_forwarded: bool):
        """Save processed message to database"""
        try:
            from database import ProcessedMessage
            
            processed_msg = ProcessedMessage(
                original_chat_id=message.chat_id,
                original_message_id=message.id,
                message_text=message.text or "",
                sender_username=getattr(message.sender, 'username', '') if hasattr(message, 'sender') else '',
                sender_id=message.sender_id or 0,
                detected_services=json.dumps(analysis_result.services),
                confidence_score=analysis_result.confidence,
                is_forwarded=is_forwarded,
                forwarded_to_group=config.TARGET_GROUP_ID if is_forwarded else None
            )
            
            db.save_processed_message(processed_msg)
            
        except Exception as e:
            logger.error("❌ Error saving processed message", exception=e)
    
    async def start_message_monitoring(self):
        """Start monitoring messages"""
        if not self.main_client:
            logger.error("❌ Main client not initialized")
            return
        
        # Register message handler
        self.main_client.add_event_handler(
            self.message_handler,
            events.NewMessage(incoming=True)
        )
        
        logger.info("👀 Bot is now monitoring messages...")
        
        # Keep running
        try:
            await self.main_client.run_until_disconnected()
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error("❌ Bot encountered error", exception=e)
    
    async def graceful_shutdown(self):
        """Gracefully shutdown all components"""
        global running
        running = False
        
        logger.info("🔄 Initiating graceful shutdown...")
        
        try:
            # Cancel stats collection
            if self.stats_collection_task:
                self.stats_collection_task.cancel()
                try:
                    await self.stats_collection_task
                except asyncio.CancelledError:
                    pass
            
            # Cleanup account manager
            await account_manager.cleanup()
            
            # Disconnect main client
            if self.main_client and self.main_client.is_connected():
                await self.main_client.disconnect()
            
            # Save final statistics
            final_stats = perf_monitor.get_metrics()
            db.save_statistic('system', 'shutdown_stats', json.dumps(final_stats))
            
            logger.info("✅ Graceful shutdown completed")
            
        except Exception as e:
            logger.error("❌ Error during shutdown", exception=e)


async def main():
    """Main bot execution function"""
    bot = EnhancedStudentHelpBot()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(bot.graceful_shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize bot
        if not await bot.initialize():
            logger.error("❌ Failed to initialize bot, exiting...")
            return
        
        # Print welcome message
        logger.info("=" * 60)
        logger.info("🎓 ENHANCED STUDENT HELP BOT - PROFESSIONAL EDITION")
        logger.info("=" * 60)
        logger.info(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📊 Dashboard available at: http://{config.DASHBOARD_HOST}:{config.DASHBOARD_PORT}")
        logger.info(f"🔐 Admin password: {config.DASHBOARD_PASSWORD}")
        logger.info("=" * 60)
        
        # Start dashboard in background
        dashboard_task = asyncio.create_task(asyncio.to_thread(start_dashboard))
        
        # Start message monitoring
        await bot.start_message_monitoring()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot interrupted by user")
    except Exception as e:
        logger.error("💥 Fatal error in main loop", exception=e)
    finally:
        await bot.graceful_shutdown()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)