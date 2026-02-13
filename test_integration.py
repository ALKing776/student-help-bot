
import os
from message_analyzer import MessageAnalyzer
from config import Config

def test_analyzer():
    print("🧪 اختبار محلل الرسائل...")
    analyzer = MessageAnalyzer()
    test_msgs = [
        "محتاج مساعدة في حل واجب الرياضيات",
        "من يقدر يسوي لي برزنتيشن عن الذكاء الاصطناعي؟",
        "السلام عليكم، كيف حالكم؟"
    ]
    
    for msg in test_msgs:
        result = analyzer.analyze_message(msg)
        print(f"الرسالة: {msg}")
        print(f"النتيجة: {'طلب مساعدة' if result['is_help_request'] else 'ليست طلب مساعدة'}")
        if result['is_help_request']:
            print(f"الخدمات: {result['services']} (ثقة: {result['confidence']}%)")
        print("-" * 20)

def test_config():
    print("🧪 اختبار التكوين...")
    # إعداد متغيرات وهمية للاختبار
    os.environ['API_ID'] = '12345'
    os.environ['API_HASH'] = 'test_hash'
    os.environ['PHONE'] = '+966500000000'
    os.environ['TARGET_GROUP_ID'] = '-100123456'
    
    try:
        Config.validate()
        print("✅ التحقق من التكوين نجح")
        Config.print_config()
    except Exception as e:
        print(f"❌ فشل التحقق من التكوين: {e}")

if __name__ == "__main__":
    test_analyzer()
    test_config()
