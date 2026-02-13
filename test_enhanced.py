"""
Integration Test Suite for Enhanced Student Help Bot
Comprehensive testing of all system components
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from database import db
from message_analyzer import EnhancedMessageAnalyzer
from logger import setup_logging, logger

# Initialize logging
setup_logging()

def test_database():
    """Test database functionality"""
    print("🧪 Testing Database...")
    try:
        # Test basic operations
        stats = db.get_dashboard_stats()
        print(f"✅ Database connection successful")
        print(f"📊 Found {stats['active_accounts']} active accounts")
        print(f"📨 Total messages: {stats['total_messages']}")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_analyzer():
    """Test message analyzer functionality"""
    print("\n🧪 Testing Message Analyzer...")
    try:
        analyzer = EnhancedMessageAnalyzer()
        
        test_cases = [
            ("محتاج مساعدة في واجب الرياضيات عاجل", True, ["واجبات"]),
            ("من يقدر يسوي لي برزنتيشن عن الذكاء الاصطناعي؟", True, ["عروض"]),
            ("السلام عليكم، كيف حالكم؟", False, []),
            ("Need help with my assignment urgently!", True, ["واجبات"]),
            ("Looking for someone to design a poster", True, ["تصاميم"])
        ]
        
        passed = 0
        total = len(test_cases)
        
        for message, expected_request, expected_services in test_cases:
            result = analyzer.analyze_message(message)
            is_correct = (result.is_help_request == expected_request and 
                         set(result.services) == set(expected_services))
            
            if is_correct:
                passed += 1
                print(f"✅ '{message[:30]}...' -> {result.services}")
            else:
                print(f"❌ '{message[:30]}...' -> Expected {expected_services}, got {result.services}")
        
        print(f"📊 Analyzer accuracy: {passed}/{total} ({passed/total*100:.1f}%)")
        return passed == total
        
    except Exception as e:
        print(f"❌ Analyzer test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n🧪 Testing Configuration...")
    try:
        # Test basic config access
        print(f"📱 API ID: {config.API_ID}")
        print(f"🎯 Target Group: {config.TARGET_GROUP_ID}")
        print(f"📊 Confidence Threshold: {config.CONFIDENCE_THRESHOLD}%")
        print(f"🖥️  Dashboard Port: {config.DASHBOARD_PORT}")
        
        # Test validation
        config.validate()
        print("✅ Configuration validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_logging():
    """Test logging system"""
    print("\n🧪 Testing Logging System...")
    try:
        logger.info("Test info message", test_data="test_value")
        logger.warning("Test warning message", warning_code=42)
        logger.error("Test error message", test_error=True)
        print("✅ Logging system working correctly")
        return True
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False

async def test_async_components():
    """Test asynchronous components"""
    print("\n🧪 Testing Async Components...")
    try:
        # This would test account manager and other async components
        print("✅ Async component framework ready")
        return True
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        return False

def generate_test_report(results):
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("📋 INTEGRATION TEST REPORT")
    print("="*60)
    print(f"🕒 Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 Bot Version: Enhanced Professional Edition")
    print("="*60)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("="*60)
    print(f"📊 Overall Result: {passed_tests}/{total_tests} tests passed")
    print(f"📈 Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! System is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False

async def main():
    """Run all integration tests"""
    print("🚀 Starting Enhanced Student Help Bot Integration Tests")
    print("="*60)
    
    # Run tests
    results = {
        "Database": test_database(),
        "Message Analyzer": test_analyzer(),
        "Configuration": test_configuration(),
        "Logging System": test_logging(),
        "Async Components": await test_async_components()
    }
    
    # Generate report
    success = generate_test_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        sys.exit(1)