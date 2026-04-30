#!/usr/bin/env python3
"""
Environment Setup Script for AI Agentic Workflow
Script thiết lập môi trường cho Quy trình Tác nhân AI
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} compatible")
    return True

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python packages...")
    
    requirements_file = Path("scripts/requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Python packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def setup_environment_file():
    """Setup .env file with user input"""
    print("🔧 Setting up environment variables...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/N): ").lower()
        if overwrite != 'y':
            print("📋 Skipping environment setup")
            return True
    
    # Load example file
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    with open(env_example, 'r') as f:
        env_content = f.read()
    
    print("\n📝 Please enter your API keys and configuration:")
    print("(Press Enter to skip optional items)")
    
    # Get user input for required fields
    configs = {
        'OPENAI_API_KEY': input("OpenAI API Key: ").strip(),
        'GMAIL_CLIENT_ID': input("Gmail Client ID: ").strip(),
        'GMAIL_CLIENT_SECRET': input("Gmail Client Secret: ").strip(),
        'SLACK_BOT_TOKEN': input("Slack Bot Token (optional): ").strip(),
        'SLACK_WEBHOOK_URL': input("Slack Webhook URL (optional): ").strip(),
        'DISCORD_BOT_TOKEN': input("Discord Bot Token (optional): ").strip(),
        'DISCORD_CHANNEL_ID': input("Discord Channel ID (optional): ").strip(),
    }
    
    # Replace placeholders in env content
    for key, value in configs.items():
        placeholder = f"your_{key.lower()}_here"
        if value:
            env_content = env_content.replace(placeholder, value)
        elif key in ['OPENAI_API_KEY', 'GMAIL_CLIENT_ID', 'GMAIL_CLIENT_SECRET']:
            print(f"⚠️  {key} is required but not provided")
            return False
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully")
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "n8n/workflows",
        "scripts",
        "docs", 
        "examples/sample-emails",
        "examples/test-data",
        "logs"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {directory}")
    
    return True

def create_sample_data():
    """Create sample data for testing"""
    print("📧 Creating sample email data...")
    
    # Sample complaint email
    complaint_email = """Subject: Phàn nàn về chất lượng dịch vụ

Kính gửi đội ngũ hỗ trợ,

Tôi rất không hài lòng với dịch vụ của quý công ty trong tuần vừa qua. 
Sản phẩm tôi nhận được bị lỗi và không hoạt động như quảng cáo.

Tôi đã liên hệ hỗ trợ 3 lần nhưng vẫn chưa nhận được giải pháp thỏa đáng.
Thời gian chờ đợi quá lâu và nhân viên hỗ trợ không chuyên nghiệp.

Mong muốn được giải quyết sớm nhất.

Trân trọng,
Nguyễn Văn A"""
    
    # Sample inquiry email  
    inquiry_email = """Subject: Câu hỏi về tính năng sản phẩm

Xin chào đội ngũ,

Tôi muốn hỏi thêm về tính năng mới của sản phẩm ABC.
Liệu có thể tích hợp với hệ thống hiện tại của chúng tôi không?

Cảm ơn thông tin."""
    
    # Write sample files
    sample_dir = Path("examples/sample-emails")
    
    with open(sample_dir / "complaint-sample.txt", 'w', encoding='utf-8') as f:
        f.write(complaint_email)
    
    with open(sample_dir / "inquiry-sample.txt", 'w', encoding='utf-8') as f:
        f.write(inquiry_email)
    
    # Create test data JSON
    test_data = [
        {
            "email_id": "test_001",
            "sender_email": "customer1@example.com",
            "subject": "Phàn nàn về giao hàng",
            "content": "Đơn hàng của tôi bị trễ 3 ngày...",
            "is_complaint": True,
            "complaint_category": "shipping",
            "sentiment_score": -0.8
        },
        {
            "email_id": "test_002", 
            "sender_email": "customer2@example.com",
            "subject": "Cảm ơn dịch vụ tốt",
            "content": "Tôi rất hài lòng với sản phẩm...",
            "is_complaint": False,
            "complaint_category": "feedback",
            "sentiment_score": 0.9
        }
    ]
    
    with open(sample_dir.parent / "test-data" / "test-complaints.json", 'w') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Sample data created")
    return True

def check_docker():
    """Check if Docker is installed and running"""
    print("🐳 Checking Docker...")
    
    try:
        # Check Docker installation
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
        else:
            print("❌ Docker not found")
            return False
        
        # Check if Docker is running
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Docker daemon is running")
        else:
            print("❌ Docker daemon is not running")
            print("   Please start Docker Desktop or Docker service")
            return False
        
        return True
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Docker not available")
        return False

def main():
    """Main setup function"""
    print("🚀 AI Agentic Workflow - Environment Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_docker():
        print("\n⚠️  Docker is required but not available")
        print("Please install Docker Desktop and try again")
        sys.exit(1)
    
    print()
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Failed to install Python packages")
        sys.exit(1)
    
    print()
    
    # Create directories
    if not create_directories():
        print("\n❌ Failed to create directories")
        sys.exit(1)
    
    print()
    
    # Create sample data
    if not create_sample_data():
        print("\n❌ Failed to create sample data")
        sys.exit(1)
    
    print()
    
    # Setup environment
    if not setup_environment_file():
        print("\n❌ Failed to setup environment")
        sys.exit(1)
    
    print()
    print("=" * 50)
    print("🎉 Environment setup completed successfully!")
    print("=" * 50)
    
    print("\n📋 Next steps:")
    print("1. Run Gmail OAuth setup: python scripts/gmail-oauth-setup.py")
    print("2. Test all APIs: python scripts/test-apis.py")
    print("3. Start services: docker-compose up -d")
    print("4. Access n8n: http://localhost:5678")
    print("5. Import workflow and configure credentials")
    
    print("\n📚 Documentation:")
    print("- API Setup Guide: docs/api-setup-guide.md")
    print("- Workflow Documentation: docs/workflow-documentation.md")
    print("- Troubleshooting: docs/troubleshooting.md")

if __name__ == "__main__":
    main()
