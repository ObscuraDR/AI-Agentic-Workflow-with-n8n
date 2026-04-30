#!/usr/bin/env python3
"""
Test Suite for AI Agentic Workflow
Bộ test cho Quy trình Tác nhân AI
"""

import unittest
import json
import os
from pathlib import Path
from datetime import datetime
import sys

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from custom_functions import (
    EmailProcessor,
    ResponseGenerator,
    NotificationHandler,
    DataValidator,
    process_email_for_n8n,
    generate_response_for_n8n,
    format_notification_for_n8n
)

class TestEmailProcessor(unittest.TestCase):
    """Test cases for EmailProcessor class"""
    
    def setUp(self):
        self.processor = EmailProcessor()
        
    def test_extract_sender_email(self):
        """Test email extraction from From field"""
        # Test with angle brackets
        self.assertEqual(
            self.processor.extract_sender_email("John Doe <john@example.com>"),
            "john@example.com"
        )
        
        # Test without angle brackets
        self.assertEqual(
            self.processor.extract_sender_email("john@example.com"),
            "john@example.com"
        )
        
        # Test with plain text
        self.assertEqual(
            self.processor.extract_sender_email("John Doe"),
            "John Doe"
        )
    
    def test_clean_email_content(self):
        """Test email content cleaning"""
        # Test with extra whitespace
        content = "  This   has    extra   spaces  "
        self.assertEqual(
            self.processor.clean_email_content(content),
            "This has extra spaces"
        )
        
        # Test with HTML tags
        content = "Hello <b>world</b>!"
        self.assertEqual(
            self.processor.clean_email_content(content),
            "Hello world!"
        )
        
        # Test with quoted replies
        content = "Main content\n\nOn Mon, Jan 1, John wrote:\n> Quoted text"
        self.assertEqual(
            self.processor.clean_email_content(content),
            "Main content"
        )
    
    def test_detect_complaint_keywords(self):
        """Test complaint keyword detection"""
        # Vietnamese keywords
        self.assertTrue(
            self.processor.detect_complaint_keywords(
                "Phàn nàn về dịch vụ",
                "Tôi không hài lòng với sản phẩm"
            )
        )
        
        # English keywords
        self.assertTrue(
            self.processor.detect_complaint_keywords(
                "Complaint about product",
                "I am disappointed with the service"
            )
        )
        
        # No complaint keywords
        self.assertFalse(
            self.processor.detect_complaint_keywords(
                "Question about product",
                "Can you tell me more about features?"
            )
        )
    
    def test_categorize_complaint(self):
        """Test complaint categorization"""
        # Service quality
        self.assertEqual(
            self.processor.categorize_complaint(
                "Phàn nàn dịch vụ",
                "Chất lượng hỗ trợ không tốt"
            ),
            'service_quality'
        )
        
        # Product issue
        self.assertEqual(
            self.processor.categorize_complaint(
                "Lỗi sản phẩm",
                "Hàng hóa bị hỏng"
            ),
            'product_issue'
        )
        
        # Billing
        self.assertEqual(
            self.processor.categorize_complaint(
                "Vấn đề thanh toán",
                "Hóa đơn không chính xác"
            ),
            'billing'
        )
        
        # Other (default)
        self.assertEqual(
            self.processor.categorize_complaint(
                "General inquiry",
                "Just asking a question"
            ),
            'other'
        )
    
    def test_calculate_sentiment_score(self):
        """Test sentiment score calculation"""
        # Positive sentiment
        positive_text = "Tôi rất hài lòng với dịch vụ tốt"
        score = self.processor.calculate_sentiment_score(positive_text)
        self.assertGreater(score, 0)
        
        # Negative sentiment
        negative_text = "Tôi không hài lòng với dịch vụ tệ"
        score = self.processor.calculate_sentiment_score(negative_text)
        self.assertLess(score, 0)
        
        # Neutral sentiment
        neutral_text = "Tôi muốn hỏi về sản phẩm"
        score = self.processor.calculate_sentiment_score(neutral_text)
        self.assertAlmostEqual(score, 0, places=1)
    
    def test_process_email(self):
        """Test complete email processing"""
        email_data = {
            'id': 'test_123',
            'from': 'John Doe <john@example.com>',
            'subject': 'Phàn nàn về dịch vụ',
            'content': 'Tôi không hài lòng với chất lượng dịch vụ',
            'date': '2024-04-26T10:00:00Z'
        }
        
        processed = self.processor.process_email(email_data)
        
        self.assertEqual(processed['email_id'], 'test_123')
        self.assertEqual(processed['sender_email'], 'john@example.com')
        self.assertEqual(processed['subject'], 'Phàn nàn về dịch vụ')
        self.assertTrue(processed['has_complaint_keyword'])
        self.assertEqual(processed['complaint_category'], 'service_quality')
        self.assertLess(processed['sentiment_score'], 0)

class TestResponseGenerator(unittest.TestCase):
    """Test cases for ResponseGenerator class"""
    
    def setUp(self):
        self.generator = ResponseGenerator()
    
    def test_generate_response_service_quality(self):
        """Test response generation for service quality complaints"""
        complaint_data = {
            'sender_email': 'customer@example.com',
            'complaint_category': 'service_quality',
            'urgency_level': 'medium',
            'sentiment_score': -0.5,
            'subject': 'Phàn nàn dịch vụ'
        }
        
        response = self.generator.generate_response(complaint_data)
        
        self.assertIn('Kính gửi Quý khách Customer', response)
        self.assertIn('dịch vụ', response)
        self.assertIn('Trân trọng', response)
    
    def test_generate_response_product_issue(self):
        """Test response generation for product issues"""
        complaint_data = {
            'sender_email': 'user@company.com',
            'complaint_category': 'product_issue',
            'urgency_level': 'high',
            'sentiment_score': -0.8,
            'subject': 'Lỗi sản phẩm'
        }
        
        response = self.generator.generate_response(complaint_data)
        
        self.assertIn('sản phẩm', response)
        self.assertIn('kỹ thuật', response)
    
    def test_generate_response_other_category(self):
        """Test response generation for other categories (fallback)"""
        complaint_data = {
            'sender_email': 'client@example.com',
            'complaint_category': 'other',
            'urgency_level': 'low',
            'sentiment_score': -0.2,
            'subject': 'General feedback'
        }
        
        response = self.generator.generate_response(complaint_data)
        
        # Should use service_quality template as fallback
        self.assertIn('Kính gửi Quý khách Client', response)

class TestNotificationHandler(unittest.TestCase):
    """Test cases for NotificationHandler class"""
    
    def setUp(self):
        self.handler = NotificationHandler()
    
    def test_format_slack_message(self):
        """Test Slack message formatting"""
        complaint_data = {
            'sender_email': 'customer@example.com',
            'subject': 'Phàn nàn dịch vụ',
            'complaint_category': 'service_quality',
            'sentiment_score': -0.5,
            'urgency_level': 'medium',
            'key_issues': ['chất lượng kém', 'thời gian chờ lâu']
        }
        
        message = self.handler.format_slack_message(complaint_data)
        
        self.assertIn('attachments', message)
        self.assertIn('fields', message['attachments'][0])
        self.assertEqual(message['attachments'][0]['color'], 'danger')
    
    def test_format_discord_message(self):
        """Test Discord message formatting"""
        complaint_data = {
            'sender_email': 'customer@example.com',
            'subject': 'Phàn nàn sản phẩm',
            'complaint_category': 'product_issue',
            'sentiment_score': -0.7,
            'urgency_level': 'high',
            'key_issues': ['sản phẩm lỗi', 'không hoạt động']
        }
        
        message = self.handler.format_discord_message(complaint_data)
        
        self.assertIn('embeds', message)
        self.assertIn('title', message['embeds'][0])
        self.assertEqual(message['embeds'][0]['color'], 0xFF0000)

class TestDataValidator(unittest.TestCase):
    """Test cases for DataValidator class"""
    
    def test_validate_email_data_valid(self):
        """Test validation of valid email data"""
        email_data = {
            'id': 'test_123',
            'from': 'john@example.com',
            'subject': 'Test subject',
            'date': '2024-04-26T10:00:00Z'
        }
        
        is_valid, errors = DataValidator.validate_email_data(email_data)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_email_data_missing_fields(self):
        """Test validation of email data with missing fields"""
        email_data = {
            'id': 'test_123',
            'from': 'john@example.com'
            # Missing subject and date
        }
        
        is_valid, errors = DataValidator.validate_email_data(email_data)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertIn('Missing required field: subject', errors)
        self.assertIn('Missing required field: date', errors)
    
    def test_validate_complaint_data_valid(self):
        """Test validation of valid complaint data"""
        complaint_data = {
            'email_id': 'test_123',
            'sender_email': 'customer@example.com',
            'subject': 'Test complaint',
            'content': 'This is a complaint',
            'sentiment_score': -0.5
        }
        
        is_valid, errors = DataValidator.validate_complaint_data(complaint_data)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_complaint_data_invalid_sentiment(self):
        """Test validation of complaint data with invalid sentiment score"""
        complaint_data = {
            'email_id': 'test_123',
            'sender_email': 'customer@example.com',
            'subject': 'Test complaint',
            'content': 'This is a complaint',
            'sentiment_score': 2.0  # Invalid: > 1
        }
        
        is_valid, errors = DataValidator.validate_complaint_data(complaint_data)
        
        self.assertFalse(is_valid)
        self.assertIn('Invalid sentiment score', errors[0])

class TestN8nIntegration(unittest.TestCase):
    """Test cases for n8n integration functions"""
    
    def test_process_email_for_n8n(self):
        """Test email processing function for n8n"""
        email_data = {
            'id': 'test_123',
            'from': 'customer@example.com',
            'subject': 'Phàn nàn',
            'content': 'Tôi không hài lòng',
            'date': '2024-04-26T10:00:00Z'
        }
        
        result = process_email_for_n8n(email_data)
        
        self.assertIn('email_id', result)
        self.assertIn('sender_email', result)
        self.assertIn('complaint_category', result)
        self.assertIn('sentiment_score', result)
    
    def test_generate_response_for_n8n(self):
        """Test response generation function for n8n"""
        complaint_data = {
            'sender_email': 'customer@example.com',
            'complaint_category': 'service_quality',
            'urgency_level': 'medium',
            'sentiment_score': -0.5,
            'subject': 'Test complaint'
        }
        
        response = generate_response_for_n8n(complaint_data)
        
        self.assertIsInstance(response, str)
        self.assertIn('Kính gửi', response)
    
    def test_format_notification_for_n8n_slack(self):
        """Test Slack notification formatting for n8n"""
        complaint_data = {
            'sender_email': 'customer@example.com',
            'subject': 'Test complaint',
            'complaint_category': 'service_quality',
            'sentiment_score': -0.5,
            'urgency_level': 'medium',
            'key_issues': ['issue1', 'issue2']
        }
        
        message = format_notification_for_n8n(complaint_data, 'slack')
        
        self.assertIn('attachments', message)
        self.assertIn('text', message)
    
    def test_format_notification_for_n8n_discord(self):
        """Test Discord notification formatting for n8n"""
        complaint_data = {
            'sender_email': 'customer@example.com',
            'subject': 'Test complaint',
            'complaint_category': 'service_quality',
            'sentiment_score': -0.5,
            'urgency_level': 'medium',
            'key_issues': ['issue1', 'issue2']
        }
        
        message = format_notification_for_n8n(complaint_data, 'discord')
        
        self.assertIn('embeds', message)
    
    def test_format_notification_for_n8n_unsupported_platform(self):
        """Test notification formatting for unsupported platform"""
        complaint_data = {
            'sender_email': 'customer@example.com',
            'subject': 'Test complaint'
        }
        
        with self.assertRaises(ValueError):
            format_notification_for_n8n(complaint_data, 'unsupported')

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_complete_workflow_simulation(self):
        """Test complete workflow simulation"""
        # Simulate incoming email
        email_data = {
            'id': 'integration_test_001',
            'from': 'Nguyen Van A <nguyen@example.com>',
            'subject': 'Phàn nàn về chất lượng sản phẩm',
            'content': 'Tôi rất không hài lòng với sản phẩm nhận được. Sản phẩm bị lỗi và không hoạt động như quảng cáo. Đã 3 ngày liên hệ hỗ trợ nhưng chưa được giải quyết.',
            'date': '2024-04-26T10:00:00Z'
        }
        
        # Step 1: Process email
        processed = process_email_for_n8n(email_data)
        self.assertTrue(processed['has_complaint_keyword'])
        self.assertEqual(processed['complaint_category'], 'product_issue')
        
        # Step 2: Generate response
        response = generate_response_for_n8n(processed)
        self.assertIn('sản phẩm', response)
        self.assertIn('kỹ thuật', response)
        
        # Step 3: Format notifications
        slack_message = format_notification_for_n8n(processed, 'slack')
        discord_message = format_notification_for_n8n(processed, 'discord')
        
        self.assertIn('attachments', slack_message)
        self.assertIn('embeds', discord_message)
        
        # Step 4: Validate data
        is_valid, errors = DataValidator.validate_complaint_data(processed)
        self.assertTrue(is_valid, f"Validation errors: {errors}")

def create_test_data():
    """Create test data files"""
    test_dir = Path("tests/test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Sample emails for testing
    test_emails = [
        {
            'id': 'test_complaint_001',
            'from': 'Customer A <customer.a@example.com>',
            'subject': 'Phàn nàn về giao hàng trễ',
            'content': 'Đơn hàng của tôi bị trễ 3 ngày so với dự kiến. Rất không hài lòng!',
            'date': '2024-04-26T09:00:00Z',
            'expected_category': 'shipping',
            'expected_complaint': True
        },
        {
            'id': 'test_inquiry_001',
            'from': 'Customer B <customer.b@example.com>',
            'subject': 'Câu hỏi về tính năng sản phẩm',
            'content': 'Tôi muốn hỏi thêm về tính năng mới của sản phẩm ABC.',
            'date': '2024-04-26T10:00:00Z',
            'expected_category': 'other',
            'expected_complaint': False
        },
        {
            'id': 'test_billing_001',
            'from': 'Customer C <customer.c@example.com>',
            'subject': 'Lỗi thanh toán',
            'content': 'Tôi bị trùng tiền cho đơn hàng #12345. Xin vui lòng hoàn lại.',
            'date': '2024-04-26T11:00:00Z',
            'expected_category': 'billing',
            'expected_complaint': True
        }
    ]
    
    with open(test_dir / "test_emails.json", 'w') as f:
        json.dump(test_emails, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Test data created in {test_dir}")

if __name__ == '__main__':
    # Create test data
    create_test_data()
    
    # Run tests
    print("🧪 Running AI Agentic Workflow Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestEmailProcessor,
        TestResponseGenerator,
        TestNotificationHandler,
        TestDataValidator,
        TestN8nIntegration,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
