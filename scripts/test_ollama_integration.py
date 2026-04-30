#!/usr/bin/env python3
"""
Test Ollama Integration for AI Agentic Workflow
Script kiểm tra tích hợp Ollama cho Quy trình Tác nhân AI
"""

import sys
import json
import time
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

from ollama_integration import (
    OllamaClient,
    OllamaEmailAnalyzer,
    OllamaResponseGenerator,
    analyze_email_with_ollama,
    generate_response_with_ollama
)

def test_ollama_connection():
    """Test basic Ollama connection"""
    print("🔗 Testing Ollama connection...")
    
    client = OllamaClient()
    
    if not client.is_available():
        print("❌ Ollama is not running!")
        print("📋 Please start Ollama first:")
        print("   Windows: ollama serve")
        print("   Linux: sudo systemctl start ollama")
        return False
    
    print("✅ Ollama is running!")
    
    # List available models
    try:
        models = client.list_models()
        print(f"📋 Available models: {[m['name'] for m in models]}")
        
        if not models:
            print("⚠️  No models found. Please pull a model:")
            print("   ollama pull llama3.2")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return False

def test_basic_generation():
    """Test basic text generation"""
    print("\n🧪 Testing basic text generation...")
    
    client = OllamaClient()
    
    try:
        response = client.generate(
            prompt="Hello! Please respond with 'Hello back!'",
            temperature=0.1,
            max_tokens=50
        )
        
        result = response.get('response', '').strip()
        print(f"📝 Response: {result}")
        
        if result and len(result) > 0:
            print("✅ Basic generation works!")
            return True
        else:
            print("❌ Empty response received")
            return False
            
    except Exception as e:
        print(f"❌ Error in basic generation: {e}")
        return False

def test_email_analysis():
    """Test email analysis functionality"""
    print("\n🔍 Testing email analysis...")
    
    test_cases = [
        {
            'name': 'Complaint Email',
            'subject': 'Phàn nàn về chất lượng dịch vụ',
            'content': 'Tôi rất không hài lòng với dịch vụ của quý công ty. Sản phẩm bị lỗi và nhân viên hỗ trợ rất kém.',
            'sender': 'customer@example.com',
            'expected_complaint': True
        },
        {
            'name': 'Inquiry Email',
            'subject': 'Câu hỏi về sản phẩm',
            'content': 'Tôi muốn hỏi thêm về tính năng mới của sản phẩm ABC. Liệu có thể tích hợp với hệ thống hiện tại không?',
            'sender': 'user@example.com',
            'expected_complaint': False
        },
        {
            'name': 'Technical Issue',
            'subject': 'Lỗi hệ thống không đăng nhập được',
            'content': 'Tôi không thể đăng nhập vào tài khoản đã 2 ngày nay. Luôn báo lỗi "Invalid credentials" dù mật khẩu đúng.',
            'sender': 'techuser@company.com',
            'expected_complaint': True
        }
    ]
    
    client = OllamaClient()
    analyzer = OllamaEmailAnalyzer(client)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  📧 Test Case {i}: {test_case['name']}")
        
        try:
            result = analyzer.analyze_email(
                test_case['subject'],
                test_case['content'],
                test_case['sender']
            )
            
            print(f"    🎯 Is Complaint: {result['is_complaint']}")
            print(f"    🏷️  Category: {result['complaint_category']}")
            print(f"    📊 Sentiment: {result['sentiment_score']:.2f}")
            print(f"    ⚡ Urgency: {result['urgency_level']}")
            print(f"    🔑 Key Issues: {result['key_issues']}")
            
            # Validate result structure
            required_fields = ['is_complaint', 'complaint_category', 'sentiment_score', 'urgency_level', 'key_issues']
            for field in required_fields:
                if field not in result:
                    print(f"    ❌ Missing field: {field}")
                    all_passed = False
            
            # Check if complaint detection is reasonable
            if result['is_complaint'] != test_case['expected_complaint']:
                print(f"    ⚠️  Complaint detection differs from expected")
                print(f"       Expected: {test_case['expected_complaint']}")
                print(f"       Got: {result['is_complaint']}")
            
            print(f"    ✅ Analysis completed")
            
        except Exception as e:
            print(f"    ❌ Error analyzing email: {e}")
            all_passed = False
    
    return all_passed

def test_response_generation():
    """Test response generation functionality"""
    print("\n✍️  Testing response generation...")
    
    test_complaints = [
        {
            'name': 'Service Quality Complaint',
            'complaint_category': 'service_quality',
            'sentiment_score': -0.8,
            'urgency_level': 'high',
            'key_issues': ['nhân viên kém', 'thời gian chờ lâu'],
            'subject': 'Phàn nàn dịch vụ',
            'content': 'Nhân viên hỗ trợ rất thiếu chuyên nghiệp và tôi phải chờ 2 tiếng.'
        },
        {
            'name': 'Product Issue Complaint',
            'complaint_category': 'product_issue',
            'sentiment_score': -0.6,
            'urgency_level': 'medium',
            'key_issues': ['sản phẩm lỗi', 'không hoạt động'],
            'subject': 'Sản phẩm hỏng',
            'content': 'Sản phẩm tôi nhận được bị lỗi và không thể bật lên.'
        }
    ]
    
    client = OllamaClient()
    generator = OllamaResponseGenerator(client)
    
    all_passed = True
    
    for i, complaint in enumerate(test_complaints, 1):
        print(f"\n  📝 Test Case {i}: {complaint['name']}")
        
        try:
            response = generator.generate_response(complaint)
            
            print(f"    📄 Response length: {len(response)} characters")
            print(f"    📄 Preview: {response[:100]}...")
            
            # Validate response
            if len(response) < 50:
                print(f"    ⚠️  Response too short")
            elif len(response) > 1000:
                print(f"    ⚠️  Response too long")
            else:
                print(f"    ✅ Response length appropriate")
            
            # Check for Vietnamese content
            vietnamese_keywords = ['Kính gửi', 'Quý khách', 'Trân trọng', 'Cảm ơn']
            vietnamese_found = any(keyword in response for keyword in vietnamese_keywords)
            
            if vietnamese_found:
                print(f"    ✅ Vietnamese content detected")
            else:
                print(f"    ⚠️  May not be in Vietnamese")
            
            # Check for professional tone
            professional_keywords = ['xin lỗi', 'giải quyết', 'hỗ trợ', 'liên hệ']
            professional_found = any(keyword in response for keyword in professional_keywords)
            
            if professional_found:
                print(f"    ✅ Professional tone detected")
            else:
                print(f"    ⚠️  May lack professional tone")
            
        except Exception as e:
            print(f"    ❌ Error generating response: {e}")
            all_passed = False
    
    return all_passed

def test_integration_functions():
    """Test the integration functions"""
    print("\n🔧 Testing integration functions...")
    
    try:
        # Test analyze_email_with_ollama function
        print("  📧 Testing analyze_email_with_ollama...")
        result = analyze_email_with_ollama(
            subject="Test complaint",
            content="This is a test complaint about poor service",
            sender="test@example.com"
        )
        
        required_fields = ['is_complaint', 'complaint_category', 'sentiment_score', 'urgency_level', 'key_issues']
        for field in required_fields:
            if field not in result:
                print(f"    ❌ Missing field in integration function: {field}")
                return False
        
        print("    ✅ analyze_email_with_ollama works!")
        
        # Test generate_response_with_ollama function
        print("  📝 Testing generate_response_with_ollama...")
        response = generate_response_with_ollama(result)
        
        if len(response) < 50:
            print(f"    ❌ Response too short from integration function")
            return False
        
        print("    ✅ generate_response_with_ollama works!")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Error in integration functions: {e}")
        return False

def test_performance():
    """Test performance metrics"""
    print("\n⚡ Testing performance...")
    
    client = OllamaClient()
    
    # Test response time
    start_time = time.time()
    
    try:
        response = client.generate(
            prompt="Briefly respond with 'Performance test complete'",
            temperature=0.1,
            max_tokens=20
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"    ⏱️  Response time: {response_time:.2f} seconds")
        
        if response_time < 10:
            print("    ✅ Response time acceptable")
        else:
            print("    ⚠️  Response time slow")
        
        # Test concurrent requests (simple test)
        print("    🔄 Testing multiple requests...")
        start_time = time.time()
        
        for i in range(3):
            client.generate(
                prompt=f"Quick response {i+1}",
                temperature=0.1,
                max_tokens=10
            )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"    ⏱️  3 requests time: {total_time:.2f} seconds")
        print(f"    ⏱️  Average per request: {total_time/3:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Performance test failed: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    print("\n🚨 Testing error handling...")
    
    # Test invalid model
    print("  📋 Testing invalid model...")
    try:
        client = OllamaClient(model="invalid-model-name")
        response = client.generate("Test")
        print("    ⚠️  Should have failed with invalid model")
        return False
    except Exception as e:
        print(f"    ✅ Correctly handled invalid model: {type(e).__name__}")
    
    # Test empty prompt
    print("  📝 Testing empty prompt...")
    try:
        client = OllamaClient()
        response = client.generate("")
        print("    ✅ Handled empty prompt")
    except Exception as e:
        print(f"    ⚠️  Error with empty prompt: {e}")
    
    return True

def run_all_tests():
    """Run all tests"""
    print("🧪 Ollama Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Connection Test", test_ollama_connection),
        ("Basic Generation", test_basic_generation),
        ("Email Analysis", test_email_analysis),
        ("Response Generation", test_response_generation),
        ("Integration Functions", test_integration_functions),
        ("Performance Test", test_performance),
        ("Error Handling", test_error_handling)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.ljust(25)}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Ollama integration is ready!")
        print("\n📋 Next steps:")
        print("1. Update your project to use Ollama")
        print("2. Import the new n8n workflow")
        print("3. Test with real email data")
        print("4. Deploy to production")
    else:
        print(f"\n⚠️  {total-passed} tests failed. Please check the issues above.")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Pull required model: ollama pull llama3.2")
        print("3. Check system resources (RAM/CPU)")
        print("4. Verify network connectivity to localhost:11434")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
