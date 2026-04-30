#!/usr/bin/env python3
"""
Ollama Integration for AI Agentic Workflow
Tích hợp Ollama cho Quy trình Tác nhân AI
"""

import requests
import json
import time
from typing import Dict, List, Optional, Union
from datetime import datetime

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = 120  # 2 minutes timeout
        
    def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make HTTP request to Ollama API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.post(
                url,
                json=data,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}. Make sure Ollama is running.")
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to Ollama timed out after {self.timeout} seconds.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Model '{self.model}' not found. Please pull it first with: ollama pull {self.model}")
            else:
                raise ValueError(f"Ollama API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[Dict]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            return response.json().get('models', [])
        except Exception as e:
            raise RuntimeError(f"Failed to list models: {str(e)}")
    
    def pull_model(self, model: str = None) -> bool:
        """Pull a model (requires Ollama CLI)"""
        model = model or self.model
        print(f"Pulling model {model}...")
        print(f"Run this command in terminal: ollama pull {model}")
        return False  # This needs to be done via CLI
    
    def generate(self, prompt: str, **kwargs) -> Dict:
        """Generate text using Ollama API"""
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        
        return self._make_request("/api/generate", data)
    
    def chat(self, messages: List[Dict], **kwargs) -> Dict:
        """Chat using Ollama API (OpenAI-compatible)"""
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            **kwargs
        }
        
        return self._make_request("/api/chat", data)
    
    def embed(self, prompt: str) -> List[float]:
        """Generate embeddings using Ollama API"""
        data = {
            "model": self.model,
            "prompt": prompt
        }
        
        response = self._make_request("/api/embeddings", data)
        return response.get("embedding", [])

class OllamaEmailAnalyzer:
    """Email analyzer using Ollama"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client
        
    def analyze_email(self, subject: str, content: str, sender: str = "") -> Dict:
        """Analyze email for complaint detection"""
        prompt = f"""Analyze the following email and determine if it's a complaint. Provide a JSON response with:
1. is_complaint (boolean)
2. complaint_category (string: service_quality, product_issue, billing, technical, other)
3. sentiment_score (float: -1 to 1, where negative indicates complaint)
4. urgency_level (string: low, medium, high)
5. key_issues (array of strings, maximum 3 items)

Email:
Subject: {subject}
From: {sender}
Content: {content}

Respond only with valid JSON. No additional text."""

        try:
            response = self.client.generate(
                prompt=prompt,
                temperature=0.3,
                top_p=0.9,
                max_tokens=500
            )
            
            # Parse the response
            response_text = response.get('response', '').strip()
            
            # Try to extract JSON from response
            try:
                # Find JSON in the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                    
                    # Validate and sanitize result
                    return {
                        'is_complaint': bool(result.get('is_complaint', False)),
                        'complaint_category': result.get('complaint_category', 'other'),
                        'sentiment_score': float(result.get('sentiment_score', 0.0)),
                        'urgency_level': result.get('urgency_level', 'medium'),
                        'key_issues': result.get('key_issues', [])[:3]  # Limit to 3 items
                    }
                else:
                    # Fallback if no JSON found
                    return self._fallback_analysis(subject, content)
                    
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._fallback_analysis(subject, content)
                
        except Exception as e:
            print(f"Error analyzing email: {str(e)}")
            return self._fallback_analysis(subject, content)
    
    def _fallback_analysis(self, subject: str, content: str) -> Dict:
        """Fallback analysis using keyword detection"""
        text = (subject + " " + content).lower()
        
        # Complaint keywords
        complaint_keywords = [
            'phàn nàn', 'khiếu nại', 'không hài lòng', 'thất vọng',
            'lỗi', 'sự cố', 'vấn đề', 'complaint', 'unhappy', 'disappointed',
            'problem', 'issue', 'error', 'bug', 'broken', 'not working'
        ]
        
        is_complaint = any(keyword in text for keyword in complaint_keywords)
        
        # Category detection
        if any(word in text for word in ['dịch vụ', 'service', 'hỗ trợ', 'support']):
            category = 'service_quality'
        elif any(word in text for word in ['sản phẩm', 'product', 'hàng', 'item']):
            category = 'product_issue'
        elif any(word in text for word in ['thanh toán', 'payment', 'hóa đơn', 'invoice']):
            category = 'billing'
        elif any(word in text for word in ['kỹ thuật', 'technical', 'hệ thống', 'system']):
            category = 'technical'
        else:
            category = 'other'
        
        # Simple sentiment
        positive_words = ['tốt', 'hay', 'hài lòng', 'good', 'great', 'happy']
        negative_words = ['xấu', 'kém', 'tệ', 'không hài lòng', 'bad', 'poor', 'unhappy']
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        sentiment = (pos_count - neg_count) / max(len(text.split()), 1) * 10
        sentiment = max(-1.0, min(1.0, sentiment))
        
        return {
            'is_complaint': is_complaint,
            'complaint_category': category,
            'sentiment_score': sentiment,
            'urgency_level': 'medium',
            'key_issues': ['keyword_analysis_fallback']
        }

class OllamaResponseGenerator:
    """Response generator using Ollama"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client
    
    def generate_response(self, complaint_data: Dict) -> str:
        """Generate professional response for complaint"""
        prompt = f"""You are a customer service representative. Generate a professional and empathetic response in Vietnamese for this customer complaint.

Complaint Details:
- Category: {complaint_data.get('complaint_category', 'other')}
- Sentiment: {complaint_data.get('sentiment_score', 0):.2f}
- Urgency: {complaint_data.get('urgency_level', 'medium')}
- Key Issues: {', '.join(complaint_data.get('key_issues', []))}

Original Email:
Subject: {complaint_data.get('subject', '')}
Content: {complaint_data.get('content', '')}

Requirements:
1. Acknowledge the issue
2. Apologize for the inconvenience  
3. Explain next steps
4. Provide timeline for resolution
5. Include contact information for follow-up
6. Keep it professional and empathetic
7. Response should be 150-250 words
8. Write in Vietnamese

Generate the response:"""

        try:
            response = self.client.generate(
                prompt=prompt,
                temperature=0.7,
                top_p=0.9,
                max_tokens=400
            )
            
            return response.get('response', '').strip()
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return self._fallback_response(complaint_data)
    
    def _fallback_response(self, complaint_data: Dict) -> str:
        """Fallback response template"""
        category = complaint_data.get('complaint_category', 'other')
        
        templates = {
            'service_quality': """Kính gửi Quý khách,

Chúng tôi đã nhận được phản hồi của Quý khách về dịch vụ và rất tiếc về trải nghiệm không tốt. Chúng tôi xin chân thành xin lỗi về sự bất tiện này.

Chúng tôi đã ghi nhận khiếu nại của Quý khách và sẽ xem xét lại quy trình dịch vụ để cải thiện chất lượng. Quý khách sẽ nhận được phản hồi chi tiết trong vòng 24 giờ.

Cảm ơn Quý khách đã thông báo cho chúng tôi.

Trân trọng,
Đội ngũ hỗ trợ khách hàng""",
            
            'product_issue': """Kính gửi Quý khách,

Chúng tôi đã nhận được thông báo về vấn đề với sản phẩm của Quý khách. Chúng tôi rất tiếc về sự cố này và xin lỗi Quý khách vì trải nghiệm không tốt.

Chúng tôi sẽ tiến hành kiểm tra sản phẩm và cung cấp giải pháp thay thế nếu cần. Trong vòng 48 giờ, chúng tôi sẽ liên hệ với Quý khách để hướng dẫn các bước tiếp theo.

Cảm ơn sự kiên nhẫn của Quý khách.

Trân trọng,
Đội ngũ kỹ thuật""",
            
            'billing': """Kính gửi Quý khách,

Chúng tôi đã nhận được khiếu nại của Quý khách về vấn đề thanh toán. Chúng tôi xin lỗi về sự nhầm lẫn trong quá trình thanh toán.

Kế toán của chúng tôi sẽ kiểm tra lại giao dịch và xử lý theo quy định. Vấn đề sẽ được giải quyết trong vòng 24 giờ làm việc.

Cảm ơn Quý khách đã thông báo cho chúng tôi.

Trân trọng,
Bộ phận kế toán""",
            
            'technical': """Kính gửi Quý khách,

Chúng tôi đã nhận được báo cáo về vấn đề kỹ thuật của Quý khách. Chúng tôi xin lỗi về sự cố kỹ thuật này.

Đội ngũ kỹ thuật của chúng tôi đang điều tra và khắc phục vấn đề. Quý khách sẽ được thông báo khi vấn đề được giải quyết.

Cảm ơn sự thông cảm của Quý khách.

Trân trọng,
Đội ngũ kỹ thuật""",
            
            'other': """Kính gửi Quý khách,

Chúng tôi đã nhận được thông tin từ Quý khách và rất ghi nhận phản hồi này. Chúng tôi sẽ xem xét kỹ lưỡng nội dung Quý khách đã gửi.

Chúng tôi sẽ liên hệ lại với Quý khách trong thời gian sớm nhất để cung cấp thông tin chi tiết.

Cảm ơn Quý khách đã liên hệ.

Trân trọng,
Đội ngũ hỗ trợ"""
        }
        
        return templates.get(category, templates['other'])

# Utility functions for n8n integration
def create_ollama_client(model: str = "llama3.2") -> OllamaClient:
    """Create and return Ollama client"""
    return OllamaClient(model=model)

def analyze_email_with_ollama(subject: str, content: str, sender: str = "", model: str = "llama3.2") -> Dict:
    """Analyze email using Ollama"""
    client = create_ollama_client(model)
    analyzer = OllamaEmailAnalyzer(client)
    return analyzer.analyze_email(subject, content, sender)

def generate_response_with_ollama(complaint_data: Dict, model: str = "llama3.2") -> str:
    """Generate response using Ollama"""
    client = create_ollama_client(model)
    generator = OllamaResponseGenerator(client)
    return generator.generate_response(complaint_data)

# Test functions
def test_ollama_integration():
    """Test Ollama integration"""
    print("Testing Ollama integration...")
    
    client = OllamaClient()
    
    # Check if Ollama is running
    if not client.is_available():
        print("❌ Ollama is not running. Please start Ollama first.")
        return False
    
    print("✅ Ollama is running")
    
    # List available models
    try:
        models = client.list_models()
        print(f"📋 Available models: {[m['name'] for m in models]}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return False
    
    # Test email analysis
    test_email = {
        'subject': 'Phàn nàn về chất lượng dịch vụ',
        'content': 'Tôi rất không hài lòng với dịch vụ của quý công ty. Sản phẩm bị lỗi và hỗ trợ rất kém.',
        'sender': 'customer@example.com'
    }
    
    try:
        result = analyze_email_with_ollama(**test_email)
        print(f"✅ Email analysis result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ Error analyzing email: {e}")
        return False
    
    # Test response generation
    try:
        response = generate_response_with_ollama(test_email)
        print(f"✅ Generated response: {response[:200]}...")
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return False
    
    print("🎉 All tests passed!")
    return True

if __name__ == "__main__":
    test_ollama_integration()
