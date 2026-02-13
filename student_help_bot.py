"""
بوت تحليل طلبات المساعدة الطلابية
Telegram Userbot for Student Service Requests Analysis
"""

from telethon import TelegramClient, events, functions, types
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import asyncio
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# استيراد المكونات المحلية
from config import Config
from message_analyzer import MessageAnalyzer

# تحميل المتغيرات البيئية
load_dotenv()

# إعدادات التسجيل
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StudentHelpBot:
    def __init__(self):
        # التحقق من صحة التكوين قبل البدء
        Config.validate()
        
        self.client = TelegramClient('session_name', Config.API_ID, Config.API_HASH)
        self.analyzer = MessageAnalyzer()
        self.processed_messages = set()
        self.last_action_time = None
        
    async def random_delay(self, min_seconds=None, max_seconds=None):
        """تأخير عشوائي لمحاكاة السلوك البشري"""
        import random
        min_val = min_seconds if min_seconds is not None else Config.MIN_DELAY
        max_val = max_seconds if max_seconds is not None else Config.MAX_DELAY
        delay = random.uniform(min_val, max_val)
        logger.info(f"🕐 تأخير عشوائي: {delay:.2f} ثانية")
        await asyncio.sleep(delay)
        
    async def human_like_delay(self):
        """تأخير متغير يعتمد على آخر إجراء"""
        import random
        if self.last_action_time:
            time_since_last = (datetime.now() - self.last_action_time).total_seconds()
            if time_since_last < 1:
                # إذا كان الإجراء سريع جداً، أضف تأخير إضافي
                extra_delay = random.uniform(1, 2)
                logger.info(f"🤖 اكتشف نشاط سريع، إضافة تأخير: {extra_delay:.2f} ثانية")
                await asyncio.sleep(extra_delay)
        
        self.last_action_time = datetime.now()
        await self.random_delay()
        
    def extract_links(self, message):
        """استخراج الروابط من الرسالة"""
        # استخدام معرف الشات بدون بادئة -100 للروابط العامة إذا كان متاحاً
        chat_id = str(message.chat_id).replace("-100", "")
        return {
            'message_link': f"https://t.me/c/{chat_id}/{message.id}",
            'direct_chat': f"https://t.me/{message.sender.username}" if hasattr(message, 'sender') and message.sender and message.sender.username else "غير متوفر"
        }
        
    async def forward_to_target_group(self, message, analysis_result):
        """نقل الرسالة المحتوية على طلب مساعدة إلى الجروب المستهدف"""
        try:
            # الحصول على معلومات المرسل
            sender = await message.get_sender()
            sender_name = f"@{sender.username}" if sender and hasattr(sender, 'username') and sender.username else "غير معروف"
            
            # استخراج الروابط
            links = self.extract_links(message)
            
            # تجهيز أنواع الخدمات المكتشفة
            services_str = ', '.join(analysis_result['services'])
            
            # إنشاء رسالة منسقة
            forwarded_message = f"""
🎯 **اكتشاف طلب مساعدة جديد!**

📝 **الخدمات المطلوبة:** {services_str}
📊 **نسبة الثقة:** {analysis_result['confidence']}%

👤 **المرسل:** {sender_name}

📄 **نص الرسالة الأصلية:**
{message.text}

🔗 **الروابط:**
• [الانتقال للرسالة الأصلية]({links['message_link']})
• [دردشة مباشرة]({links['direct_chat']})

⏰ **وقت الاكتشاف:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await self.client.send_message(
                Config.TARGET_GROUP_ID,
                forwarded_message,
                parse_mode='markdown'
            )
            
            logger.info(f"✅ تم نقل طلب مساعدة (الخدمات: {services_str})")
            return True
            
        except FloodWaitError as e:
            wait_time = e.seconds * Config.FLOOD_WAIT_MULTIPLIER
            logger.warning(f"⚠️ FloodWaitError: انتظار {wait_time} ثانية")
            await asyncio.sleep(wait_time)
            # محاولة مرة أخرى
            return await self.forward_to_target_group(message, analysis_result)
        except Exception as e:
            logger.error(f"❌ خطأ في نقل الرسالة: {str(e)}")
            return False
            
    async def message_handler(self, event):
        """معالج الرسائل الرئيسي"""
        message = event.message
        
        # تجاهل الرسائل الخاصة
        if message.is_private:
            return
            
        # تجاهل الرسائل التي تمت معالجتها مسبقاً
        message_id = f"{message.chat_id}_{message.id}"
        if message_id in self.processed_messages:
            return
            
        self.processed_messages.add(message_id)
        
        # الحصول على نص الرسالة
        message_text = message.text or message.message or ""
        
        # تحليل الرسالة باستخدام المحلل المتقدم
        analysis = self.analyzer.analyze_message(message_text)
        
        if analysis['is_help_request']:
            logger.info(f"🔍 اكتشاف طلب مساعدة: {', '.join(analysis['services'])} (ثقة: {analysis['confidence']}%)")
            
            # تأخير بشري قبل النقل
            await self.human_like_delay()
            
            # نقل الرسالة إلى الجروب المستهدف
            success = await self.forward_to_target_group(message, analysis)
            
            if success:
                logger.info(f"✅ تم معالجة طلب المساعدة بنجاح")
        else:
            # تأخير صغير جداً للرسائل العادية لتجنب استهلاك المعالج
            await asyncio.sleep(0.01)
            
    async def get_group_chats(self):
        """الحصول على قائمة الجروبات المراقبة"""
        try:
            chats = []
            last_date = None
            chunk_size = 200
            
            while True:
                result = await self.client(GetDialogsRequest(
                    offset_date=last_date,
                    offset_id=0,
                    offset_peer=InputPeerEmpty(),
                    limit=chunk_size,
                    hash=0
                ))
                
                if not result.chats:
                    break
                    
                chats.extend(result.chats)
                last_date = result.messages[-1].date
                if len(result.chats) < chunk_size:
                    break
                
            # تصفية الجروبات فقط
            groups = [chat for chat in chats if hasattr(chat, 'megagroup') and chat.megagroup]
            return groups
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب الجروبات: {str(e)}")
            return []
            
    async def start(self):
        """بدء تشغيل البوت"""
        # طباعة الإعدادات الحالية للتحقق
        Config.print_config()
        
        await self.client.start(phone=Config.PHONE)
        logger.info("🚀 بدء تشغيل البوت بنجاح!")
        
        # عرض الجروبات المتاحة
        groups = await self.get_group_chats()
        if groups:
            logger.info(f"📊 تم العثور على {len(groups)} جروب للمراقبة")
            for group in groups[:10]:  # عرض أول 10 جروبات
                logger.info(f"  • {group.title} (ID: {group.id})")
        else:
            logger.warning("⚠️ لم يتم العثور على جروبات")
            
        # تسجيل معالج الرسائل
        self.client.add_event_handler(
            self.message_handler,
            events.NewMessage(incoming=True)
        )
        
        logger.info("👀 البوت جاهز للمراقبة والتحليل...")
        
        # البقاء في حالة تشغيل
        await self.client.run_until_disconnected()


async def main():
    bot = StudentHelpBot()
    await bot.start()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ حدث خطأ غير متوقع: {e}")
