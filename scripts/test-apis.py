#!/usr/bin/env python3
"""
API Testing Script for AI Agentic Workflow
Script kiểm tra các API cần thiết cho hệ thống
"""

import os
import json
import requests
import time
from pathlib import Path

def load_env():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    env_vars = {}
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"\'')
    
    return env_vars

def test_openai_api(api_key):
    """Test OpenAI API connection"""
    print("🧠 Testing OpenAI API...")
    
    if not api_key:
        print("❌ OpenAI API key not found in .env")
        return False
    
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello, this is a test message."}],
            "max_tokens": 10
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            print("✅ OpenAI API connection successful")
            result = response.json()
            print(f"   Model: {result['model']}")
            print(f"   Response: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ OpenAI API error: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def test_gmail_api():
    """Test Gmail API connection using stored credentials"""
    print("📧 Testing Gmail API...")
    
    token_file = Path("token.json")
    if not token_file.exists():
        print("❌ No Gmail credentials found. Please run gmail-oauth-setup.py first")
        return False
    
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        import googleapiclient.discovery
        
        creds = Credentials.from_authorized_user_file(str(token_file))
        
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                print("🔄 Refreshing Gmail token...")
                creds.refresh(Request())
                with open(token_file, 'w') as f:
                    f.write(creds.to_json())
            else:
                print("❌ Gmail credentials invalid. Please run gmail-oauth-setup.py again")
                return False
        
        service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
        
        # Test API call
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        print("✅ Gmail API connection successful")
        print(f"   Found {len(labels)} labels")
        
        # Test reading emails
        try:
            results = service.users().messages().list(userId='me', maxResults=1).execute()
            messages = results.get('messages', [])
            if messages:
                print(f"   Recent emails: {len(messages)} found")
            else:
                print("   No emails found (or empty inbox)")
        except:
            print("   Could not test email reading (permissions issue)")
        
        return True
        
    except ImportError:
        print("❌ Google libraries not installed. Run: pip install google-auth google-auth-oauthlib google-api-python-client")
        return False
    except Exception as e:
        print(f"❌ Gmail API test failed: {e}")
        return False

def test_slack_api(bot_token, webhook_url):
    """Test Slack API connection"""
    print("💬 Testing Slack API...")
    
    success = False
    
    # Test Bot Token
    if bot_token:
        try:
            url = "https://slack.com/api/auth.test"
            headers = {
                "Authorization": f"Bearer {bot_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print("✅ Slack Bot Token valid")
                    print(f"   Team: {result.get('team')}")
                    print(f"   User: {result.get('user')}")
                    success = True
                else:
                    print(f"❌ Slack Bot Token error: {result.get('error')}")
            else:
                print(f"❌ Slack API error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Slack Bot Token test failed: {e}")
    
    # Test Webhook URL
    if webhook_url:
        try:
            data = {
                "text": "🧪 Test message from AI Agentic Workflow"
            }
            
            response = requests.post(webhook_url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok') or response.text == 'ok':
                    print("✅ Slack Webhook URL valid")
                    success = True
                else:
                    print(f"❌ Slack Webhook error: {result}")
            else:
                print(f"❌ Slack Webhook error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Slack Webhook test failed: {e}")
    
    if not bot_token and not webhook_url:
        print("⚠️  No Slack credentials found in .env")
        return False
    
    return success

def test_discord_api(bot_token, channel_id):
    """Test Discord API connection"""
    print("🎮 Testing Discord API...")
    
    if not bot_token:
        print("❌ Discord Bot Token not found in .env")
        return False
    
    try:
        # Test bot validity
        url = "https://discord.com/api/users/@me"
        headers = {
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            print("✅ Discord Bot Token valid")
            print(f"   Bot: {bot_info.get('username')}#{bot_info.get('discriminator')}")
            
            # Test channel access if channel_id provided
            if channel_id:
                channel_url = f"https://discord.com/api/channels/{channel_id}"
                channel_response = requests.get(channel_url, headers=headers, timeout=10)
                
                if channel_response.status_code == 200:
                    channel_info = channel_response.json()
                    print(f"   Channel: #{channel_info.get('name')}")
                    print("✅ Discord Channel access confirmed")
                else:
                    print(f"⚠️  Cannot access channel: {channel_response.status_code}")
            
            return True
        else:
            print(f"❌ Discord Bot Token error: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Discord API test failed: {e}")
        return False

def test_database_connection():
    """Test PostgreSQL database connection"""
    print("🗄️ Testing PostgreSQL Database...")
    
    try:
        import psycopg2
        from psycopg2 import OperationalError
        
        # Load database config from environment
        env_vars = load_env()
        
        db_config = {
            'host': 'localhost',
            'port': env_vars.get('POSTGRES_PORT', '5432'),
            'database': env_vars.get('POSTGRES_DB', 'n8n_workflow'),
            'user': env_vars.get('POSTGRES_USER', 'n8n_user'),
            'password': env_vars.get('POSTGRES_PASSWORD', 'n8n_password')
        }
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print("✅ Database connection successful")
        print(f"   PostgreSQL: {version[0]}")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"   Found {len(tables)} tables:")
            for table in tables:
                print(f"     - {table[0]}")
        else:
            print("   No tables found (database needs setup)")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
        return False
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure PostgreSQL is running and credentials are correct")
        return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_n8n_connection():
    """Test n8n service connection"""
    print("🔧 Testing n8n Service...")
    
    try:
        response = requests.get("http://localhost:5678/healthz", timeout=10)
        
        if response.status_code == 200:
            print("✅ n8n service is running")
            print(f"   Health check: {response.text}")
            return True
        else:
            print(f"❌ n8n health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to n8n service")
        print("   Make sure n8n is running: docker-compose up -d")
        return False
    except Exception as e:
        print(f"❌ n8n test failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 AI Agentic Workflow - API Testing Suite")
    print("=" * 50)
    
    # Load environment variables
    env_vars = load_env()
    
    results = {}
    
    # Test n8n service
    results['n8n'] = test_n8n_connection()
    print()
    
    # Test database
    results['database'] = test_database_connection()
    print()
    
    # Test OpenAI
    results['openai'] = test_openai_api(env_vars.get('OPENAI_API_KEY'))
    print()
    
    # Test Gmail
    results['gmail'] = test_gmail_api()
    print()
    
    # Test Slack
    results['slack'] = test_slack_api(
        env_vars.get('SLACK_BOT_TOKEN'),
        env_vars.get('SLACK_WEBHOOK_URL')
    )
    print()
    
    # Test Discord
    results['discord'] = test_discord_api(
        env_vars.get('DISCORD_BOT_TOKEN'),
        env_vars.get('DISCORD_CHANNEL_ID')
    )
    print()
    
    # Summary
    print("=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    for service, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{service.ljust(10)}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All systems ready! You can start using the workflow.")
    else:
        print("⚠️  Some systems need configuration. Check the errors above.")
    
    print("\n📋 Next steps:")
    print("1. Fix any failed configurations")
    print("2. Import workflow into n8n: http://localhost:5678")
    print("3. Configure credentials in n8n")
    print("4. Test the workflow")

if __name__ == "__main__":
    main()
