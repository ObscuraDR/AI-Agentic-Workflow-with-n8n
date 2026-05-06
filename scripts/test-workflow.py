#!/usr/bin/env python3
"""
Test script for n8n workflow
Script kiểm tra workflow n8n
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
N8N_URL = "http://localhost:5678"
WEBHOOK_ENDPOINT = f"{N8N_URL}/webhook/email-analysis"

def test_workflow():
    """Test the workflow with sample data"""
    print("🧪 Testing n8n workflow...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test data
    test_email = {
        "id": "test_003",
        "from": "angry.customer@example.com",
        "subject": "Phàn nàn về chất lượng dịch vụ rất tệ",
        "snippet": "Tôi rất thất vọng với dịch vụ của quý công ty. Sản phẩm bị lỗi và giao hàng trễ.",
        "body": "Kính gửi đội ngũ hỗ trợ, Tôi đã đặt hàng mã số #12345 vào ngày 1/5/2024 nhưng đến nay vẫn chưa nhận được. Khi tôi liên hệ thì nhân viên hỗ trợ rất thiếu thân thiện. Tôi yêu cầu hoàn tiền ngay lập tức.",
        "date": datetime.now().isoformat()
    }
    
    try:
        print(f"📤 Sending test email to: {WEBHOOK_ENDPOINT}")
        print(f"📧 Email data: {json.dumps(test_email, indent=2, ensure_ascii=False)}")
        
        # Send test request
        response = requests.post(WEBHOOK_ENDPOINT, json=test_email, timeout=30)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Workflow executed successfully!")
            print(f"📄 Response: {response.text}")
        else:
            print(f"❌ Workflow failed with status: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to n8n. Make sure n8n is running at http://localhost:5678")
        print("💡 Run: docker-compose up -d")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout. Workflow may be taking too long to execute.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False
    
    return True

def check_database():
    """Check if data was saved to database"""
    print("\n🔍 Checking database...")
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Database connection
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="n8n_workflow",
            user="n8n_user",
            password="n8n_password"
        )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check email_complaints table
        cursor.execute("SELECT * FROM email_complaints ORDER BY created_at DESC LIMIT 5")
        complaints = cursor.fetchall()
        
        print(f"📊 Found {len(complaints)} recent complaints:")
        for complaint in complaints:
            print(f"  - ID: {complaint['id']}, Email: {complaint['sender_email']}, Subject: {complaint['subject'][:50]}...")
        
        # Check ai_responses table
        cursor.execute("SELECT * FROM ai_responses ORDER BY generated_at DESC LIMIT 5")
        responses = cursor.fetchall()
        
        print(f"\n🤖 Found {len(responses)} recent AI responses:")
        for response in responses:
            print(f"  - ID: {response['id']}, Complaint ID: {response['complaint_id']}, Status: {response['status']}")
        
        cursor.close()
        conn.close()
        
        print("✅ Database check completed!")
        
    except ImportError:
        print("⚠️  psycopg2 not installed. Install with: pip install psycopg2-binary")
    except Exception as e:
        print(f"❌ Database error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting n8n workflow test...")
    print("=" * 50)
    
    # Test workflow
    if test_workflow():
        print("\n" + "=" * 50)
        # Wait a bit for database operations
        time.sleep(2)
        # Check database
        check_database()
    
    print("\n🏁 Test completed!")
