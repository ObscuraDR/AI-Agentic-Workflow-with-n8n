#!/usr/bin/env python3
"""
Custom Functions for AI Agentic Workflow
Các hàm tùy chỉnh cho Quy trình Tác nhân AI
"""

import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class EmailProcessor:
    """Class for processing email content"""
    
    def __init__(self):
        # Vietnamese complaint keywords
        self.complaint_keywords_vn = [
            'phàn nàn', 'khiếu nại', 'không hài lòng', 'thất vọng',
            'lỗi', 'sự cố', 'vấn đề', 'trục trặc', 'gián đoạn',
            'chậm', 'trễ', 'hỏng', 'kém', 'tệ', 'dở'
        ]
        
        # English complaint keywords
        self.complaint_keywords_en = [
            'complaint', 'unhappy', 'disappointed', 'frustrated',
            'problem', 'issue', 'error', 'bug', 'broken', 'not working',
            'slow', 'delay', 'late', 'poor', 'bad', 'terrible'
        ]
        
        # Urgency indicators
        self.urgency_keywords = [
            'khẩn', 'gấp', 'ngay lập tức', 'cần ngay', 'asap', 'urgent',
            'immediately', 'emergency', 'critical'
        ]
    
    def extract_sender_email(self, from_field: str) -> str:
        """Extract email address from From field"""
        # Pattern to match email in <email@domain.com> format
        email_pattern = r'<([^>]+)>'
        match = re.search(email_pattern, from_field)
        
        if match:
            return match.group(1).strip()
        
        # If no angle brackets, return the whole string if it looks like email
        if '@' in from_field:
            return from_field.strip()
        
        return from_field.strip()
    
    def clean_email_content(self, content: str) -> str:
        """Clean and normalize email content"""
        if not content:
            return ""
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Remove quoted replies (common in email threads)
        content = re.sub(r'On.*wrote:.*$', '', content, flags=re.DOTALL)
        content = re.sub(r'>.*$', '', content, flags=re.MULTILINE)
        
        # Remove HTML tags (basic)
        content = re.sub(r'<[^>]+>', '', content)
        
        # Limit length for processing
        if len(content) > 5000:
            content = content[:5000] + "..."
        
        return content.strip()
    
    def detect_complaint_keywords(self, subject: str, content: str) -> bool:
        """Detect if email contains complaint keywords"""
        text = (subject + " " + content).lower()
        
        all_keywords = self.complaint_keywords_vn + self.complaint_keywords_en
        
        for keyword in all_keywords:
            if keyword.lower() in text:
                return True
        
        return False
    
    def detect_urgency(self, subject: str, content: str) -> str:
        """Detect urgency level"""
        text = (subject + " " + content).lower()
        
        for keyword in self.urgency_keywords:
            if keyword.lower() in text:
                return "high"
        
        return "medium"
    
    def categorize_complaint(self, subject: str, content: str) -> str:
        """Categorize complaint type"""
        text = (subject + " " + content).lower()
        
        categories = {
            'service_quality': ['dịch vụ', 'service', 'chất lượng', 'quality', 'hỗ trợ', 'support'],
            'product_issue': ['sản phẩm', 'product', 'hàng', 'item', 'lỗi', 'defect'],
            'billing': ['thanh toán', 'payment', 'hóa đơn', 'invoice', 'giá', 'price'],
            'technical': ['kỹ thuật', 'technical', 'hệ thống', 'system', 'truy cập', 'access'],
            'shipping': ['giao hàng', 'delivery', 'shipping', 'vận chuyển', 'transport']
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        return 'other'
    
    def calculate_sentiment_score(self, text: str) -> float:
        """Simple sentiment scoring (can be enhanced with proper NLP)"""
        # Positive words
        positive_words = ['tốt', 'hay', 'hài lòng', 'good', 'great', 'excellent', 'happy', 'satisfied']
        
        # Negative words
        negative_words = ['xấu', 'kém', 'tệ', 'không hài lòng', 'bad', 'poor', 'terrible', 'unhappy', 'disappointed']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text_lower.split())
        
        if total_words == 0:
            return 0.0
        
        # Simple sentiment calculation
        sentiment = (positive_count - negative_count) / max(total_words, 1)
        
        # Normalize to -1 to 1 range
        return max(-1.0, min(1.0, sentiment * 10))
    
    def process_email(self, email_data: Dict) -> Dict:
        """Main email processing function"""
        processed = {
            'email_id': email_data.get('id', ''),
            'sender_email': self.extract_sender_email(email_data.get('from', '')),
            'subject': email_data.get('subject', ''),
            'content': self.clean_email_content(email_data.get('content', email_data.get('snippet', ''))),
            'received_at': email_data.get('date', datetime.now().isoformat()),
            'has_complaint_keyword': self.detect_complaint_keywords(
                email_data.get('subject', ''),
                email_data.get('content', email_data.get('snippet', ''))
            ),
            'urgency_level': self.detect_urgency(
                email_data.get('subject', ''),
                email_data.get('content', email_data.get('snippet', ''))
            ),
            'complaint_category': self.categorize_complaint(
                email_data.get('subject', ''),
                email_data.get('content', email_data.get('snippet', ''))
            ),
            'sentiment_score': self.calculate_sentiment_score(
                email_data.get('content', email_data.get('snippet', ''))
            ),
            'processed_at': datetime.now().isoformat()
        }
        
        return processed

class ResponseGenerator:
    """Class for generating AI responses"""
    
    def __init__(self):
        self.response_templates = {
            'service_quality': {
                'greeting': 'Kính gửi Quý khách {name},',
                'acknowledgment': 'Chúng tôi rất tiếc khi biết về trải nghiệm không tốt của Quý khách với dịch vụ của chúng tôi.',
                'apology': 'Chúng tôi chân thành xin lỗi về sự bất tiện này.',
                'action': 'Chúng tôi đã ghi nhận phản hồi của Quý khách và sẽ xem xét lại quy trình dịch vụ.',
                'timeline': 'Quý khách sẽ nhận được phản hồi chi tiết trong vòng 24 giờ.',
                'closing': 'Trân trọng,\\nĐội ngũ hỗ trợ khách hàng'
            },
            'product_issue': {
                'greeting': 'Kính gửi Quý khách {name},',
                'acknowledgment': 'Chúng tôi đã nhận được thông báo về vấn đề với sản phẩm của Quý khách.',
                'apology': 'Chúng tôi rất tiếc về sự cố này và xin lỗi Quý khách vì trải nghiệm không tốt.',
                'action': 'Chúng tôi sẽ tiến hành kiểm tra sản phẩm và cung cấp giải pháp thay thế nếu cần.',
                'timeline': 'Trong vòng 48 giờ, chúng tôi sẽ liên hệ với Quý khách để hướng dẫn các bước tiếp theo.',
                'closing': 'Trân trọng,\\nĐội ngũ kỹ thuật'
            },
            'billing': {
                'greeting': 'Kính gửi Quý khách {name},',
                'acknowledgment': 'Chúng tôi đã nhận được khiếu nại của Quý khách về vấn đề thanh toán.',
                'apology': 'Chúng tôi xin lỗi về sự nhầm lẫn trong quá trình thanh toán.',
                'action': 'Kế toán của chúng tôi sẽ kiểm tra lại giao dịch và xử lý theo quy định.',
                'timeline': 'Vấn đề sẽ được giải quyết trong vòng 24 giờ làm việc.',
                'closing': 'Trân trọng,\\nBộ phận kế toán'
            },
            'technical': {
                'greeting': 'Kính gửi Quý khách {name},',
                'acknowledgment': 'Chúng tôi đã nhận được báo cáo về vấn đề kỹ thuật của Quý khách.',
                'apology': 'Chúng tôi xin lỗi về sự cố kỹ thuật này.',
                'action': 'Đội ngũ kỹ thuật của chúng tôi đang điều tra và khắc phục vấn đề.',
                'timeline': 'Quý khách sẽ được thông báo khi vấn đề được giải quyết.',
                'closing': 'Trân trọng,\\nĐội ngũ kỹ thuật'
            }
        }
    
    def generate_response(self, complaint_data: Dict) -> str:
        """Generate response based on complaint data"""
        category = complaint_data.get('complaint_category', 'other')
        urgency = complaint_data.get('urgency_level', 'medium')
        
        # Get template for category
        template = self.response_templates.get(category, self.response_templates['service_quality'])
        
        # Extract sender name from email
        sender_email = complaint_data.get('sender_email', '')
        sender_name = sender_email.split('@')[0] if '@' in sender_email else 'Quý khách'
        
        # Build response
        response_parts = [
            template['greeting'].format(name=sender_name.title()),
            '',
            template['acknowledgment'],
            template['apology'],
            '',
            template['action'],
            template['timeline'],
            '',
            'Chi tiết khiếu nại:',
            f'- Tiêu đề: {complaint_data.get("subject", "")}',
            f'- Mức độ khẩn: {urgency}',
            f'- Điểm cảm xúc: {complaint_data.get("sentiment_score", 0):.2f}',
            '',
            template['closing']
        ]
        
        return '\\n'.join(response_parts)
    
    def enhance_response_with_ai(self, base_response: str, complaint_data: Dict) -> str:
        """Enhance base response with AI (placeholder for OpenAI integration)"""
        # This would be called from n8n with OpenAI
        # For now, return the base response
        return base_response

class NotificationHandler:
    """Class for handling notifications"""
    
    def __init__(self):
        self.notification_templates = {
            'slack': {
                'complaint': {
                    'title': '🚨 Khiếu nại mới từ khách hàng',
                    'color': 'danger',
                    'fields': [
                        {'title': '📧 Email', 'value': '{sender_email}', 'short': True},
                        {'title': '📝 Tiêu đề', 'value': '{subject}', 'short': True},
                        {'title': '🏷️ Danh mục', 'value': '{category}', 'short': True},
                        {'title': '📊 Cảm xúc', 'value': '{sentiment}', 'short': True},
                        {'title': '⚡ Khẩn cấp', 'value': '{urgency}', 'short': True},
                        {'title': '🔑 Vấn đề', 'value': '{issues}', 'short': False}
                    ],
                    'footer': 'Phản hồi đã được soạn thảo và chờ duyệt'
                }
            },
            'discord': {
                'complaint': {
                    'title': '🚨 Khiếu nại mới từ khách hàng',
                    'color': 0xFF0000,
                    'fields': [
                        {'name': '📧 Email', 'value': '{sender_email}', 'inline': True},
                        {'name': '📝 Tiêu đề', 'value': '{subject}', 'inline': True},
                        {'name': '🏷️ Danh mục', 'value': '{category}', 'inline': True},
                        {'name': '📊 Cảm xúc', 'value': '{sentiment}', 'inline': True},
                        {'name': '⚡ Khẩn cấp', 'value': '{urgency}', 'inline': True},
                        {'name': '🔑 Vấn đề', 'value': '{issues}', 'inline': False}
                    ],
                    'footer': {'text': 'Phản hồi đã được soạn thảo và chờ duyệt'}
                }
            }
        }
    
    def format_slack_message(self, complaint_data: Dict) -> Dict:
        """Format message for Slack"""
        template = self.notification_templates['slack']['complaint']
        
        message = {
            'text': template['title'],
            'attachments': [{
                'color': template['color'],
                'fields': [
                    {
                        'title': field['title'],
                        'value': field['value'].format(**self._format_complaint_data(complaint_data)),
                        'short': field['short']
                    }
                    for field in template['fields']
                ],
                'footer': template['footer'],
                'ts': datetime.now().timestamp()
            }]
        }
        
        return message
    
    def format_discord_message(self, complaint_data: Dict) -> Dict:
        """Format message for Discord"""
        template = self.notification_templates['discord']['complaint']
        
        embed = {
            'title': template['title'],
            'color': template['color'],
            'fields': [
                {
                    'name': field['name'],
                    'value': field['value'].format(**self._format_complaint_data(complaint_data)),
                    'inline': field['inline']
                }
                for field in template['fields']
            ],
            'footer': template['footer'],
            'timestamp': datetime.now().isoformat()
        }
        
        return {'embeds': [embed]}
    
    def _format_complaint_data(self, complaint_data: Dict) -> Dict:
        """Format complaint data for template substitution"""
        return {
            'sender_email': complaint_data.get('sender_email', ''),
            'subject': complaint_data.get('subject', ''),
            'category': complaint_data.get('complaint_category', 'other'),
            'sentiment': f"{complaint_data.get('sentiment_score', 0):.2f}",
            'urgency': complaint_data.get('urgency_level', 'medium'),
            'issues': ', '.join(complaint_data.get('key_issues', []))
        }

class DataValidator:
    """Class for validating data"""
    
    @staticmethod
    def validate_email_data(email_data: Dict) -> Tuple[bool, List[str]]:
        """Validate email data"""
        errors = []
        
        required_fields = ['id', 'from', 'subject', 'date']
        for field in required_fields:
            if field not in email_data or not email_data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate email format
        if 'from' in email_data:
            from_field = email_data['from']
            if '@' not in from_field and '<' not in from_field:
                errors.append("Invalid email format in 'from' field")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_complaint_data(complaint_data: Dict) -> Tuple[bool, List[str]]:
        """Validate complaint data"""
        errors = []
        
        required_fields = ['email_id', 'sender_email', 'subject', 'content']
        for field in required_fields:
            if field not in complaint_data or not complaint_data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate sentiment score
        if 'sentiment_score' in complaint_data:
            score = complaint_data['sentiment_score']
            if not isinstance(score, (int, float)) or score < -1 or score > 1:
                errors.append("Invalid sentiment score (must be between -1 and 1)")
        
        return len(errors) == 0, errors

# Utility functions
def generate_email_hash(email_data: Dict) -> str:
    """Generate unique hash for email"""
    content = f"{email_data.get('id', '')}{email_data.get('date', '')}{email_data.get('from', '')}"
    return hashlib.md5(content.encode()).hexdigest()

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

# Example usage functions for n8n
def process_email_for_n8n(email_data: Dict) -> Dict:
    """Process email data for n8n workflow"""
    processor = EmailProcessor()
    return processor.process_email(email_data)

def generate_response_for_n8n(complaint_data: Dict) -> str:
    """Generate response for n8n workflow"""
    generator = ResponseGenerator()
    return generator.generate_response(complaint_data)

def format_notification_for_n8n(complaint_data: Dict, platform: str = 'slack') -> Dict:
    """Format notification for n8n workflow"""
    handler = NotificationHandler()
    
    if platform == 'slack':
        return handler.format_slack_message(complaint_data)
    elif platform == 'discord':
        return handler.format_discord_message(complaint_data)
    else:
        raise ValueError(f"Unsupported platform: {platform}")

if __name__ == "__main__":
    # Test the functions
    sample_email = {
        'id': 'test_123',
        'from': 'customer@example.com',
        'subject': 'Phàn nàn về dịch vụ',
        'content': 'Tôi không hài lòng với dịch vụ của quý công ty',
        'date': '2024-04-26T10:00:00Z'
    }
    
    processor = EmailProcessor()
    processed = processor.process_email(sample_email)
    print("Processed email:", json.dumps(processed, indent=2, ensure_ascii=False))
    
    generator = ResponseGenerator()
    response = generator.generate_response(processed)
    print("\\nGenerated response:")
    print(response)
