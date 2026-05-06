#!/bin/bash

# AI Agentic Workflow with n8n - Setup Script
# Script cài đặt cho Quy trình Tác nhân AI với n8n

echo "🚀 Bắt đầu cài đặt AI Agentic Workflow với n8n..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker chưa được cài đặt. Vui lòng cài đặt Docker trước."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose chưa được cài đặt. Vui lòng cài đặt Docker Compose trước."
    exit 1
fi

# Create necessary directories
echo "📁 Tạo các thư mục cần thiết..."
mkdir -p n8n/workflows
mkdir -p scripts
mkdir -p docs
mkdir -p examples/sample-emails
mkdir -p examples/test-data

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Tạo file .env từ template..."
    cp .env.example .env
    echo "⚠️  Vui lòng chỉnh sửa file .env với thông tin API keys của bạn!"
else
    echo "✅ File .env đã tồn tại"
fi

# Set permissions
echo "🔐 Thiết lập permissions..."
chmod +x setup.sh
chmod 600 .env

# Create sample email data
echo "📧 Tạo dữ liệu email mẫu..."
cat > examples/sample-emails/complaint-sample.txt << 'EOF'
Subject: Phàn nàn về chất lượng dịch vụ

Kính gửi đội ngũ hỗ trợ,

Tôi rất không hài lòng với dịch vụ của quý công ty trong tuần vừa qua. 
Sản phẩm tôi nhận được bị lỗi và không hoạt động như quảng cáo.

Tôi đã liên hệ hỗ trợ 3 lần nhưng vẫn chưa nhận được giải pháp thỏa đáng.
Thời gian chờ đợi quá lâu và nhân viên hỗ trợ không chuyên nghiệp.

Mong muốn được giải quyết sớm nhất.

Trân trọng,
Nguyễn Văn A
EOF

cat > examples/sample-emails/inquiry-sample.txt << 'EOF'
Subject: Câu hỏi về tính năng sản phẩm

Xin chào đội ngũ,

Tôi muốn hỏi thêm về tính năng mới của sản phẩm ABC.
Liệu có thể tích hợp với hệ thống hiện tại của chúng tôi không?

Cảm ơn thông tin.
EOF

# Create test data for database
echo "🗄️ Tạo dữ liệu test cho database..."
cat > examples/test-data/test-complaints.json << 'EOF'
[
  {
    "email_id": "test_001",
    "sender_email": "customer1@example.com",
    "subject": "Phàn nàn về giao hàng",
    "content": "Đơn hàng của tôi bị trễ 3 ngày...",
    "is_complaint": true,
    "complaint_category": "shipping",
    "sentiment_score": -0.8
  },
  {
    "email_id": "test_002",
    "sender_email": "customer2@example.com",
    "subject": "Cảm ơn dịch vụ tốt",
    "content": "Tôi rất hài lòng với sản phẩm...",
    "is_complaint": false,
    "complaint_category": "feedback",
    "sentiment_score": 0.9
  }
]
EOF

# Start services
echo "🐳 Khởi động dịch vụ Docker..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Chờ dịch vụ khởi động..."
sleep 30

# Check if services are running
echo "🔍 Kiểm tra trạng thái dịch vụ..."
docker-compose ps

# Test database connection
echo "🗄️ Kiểm tra kết nối database..."
docker-compose exec -T postgres psql -U n8n_user -d n8n_workflow -c "SELECT version();" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
fi

# Test n8n
echo "🔧 Kiểm tra n8n..."
curl -s http://localhost:5678/healthz > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ n8n is running"
else
    echo "⚠️  n8n might still be starting up"
fi

echo ""
echo "🎉 Cài đặt hoàn tất!"
echo ""
echo "📋 Các bước tiếp theo:"
echo "1. Chỉnh sửa file .env với API keys của bạn"
echo "2. Truy cập n8n tại: http://localhost:5678"
echo "3. Import workflow từ file: n8n/workflows/email-analysis-workflow.json"
echo "4. Cấu hình credentials cho Gmail, OpenAI, và Slack"
echo "5. Bắt đầu workflow và kiểm tra"
echo ""
echo "📚 Tài liệu tham khảo:"
echo "- Hướng dẫn API: docs/api-setup-guide.md"
echo "- Workflow documentation: docs/workflow-documentation.md"
echo "- Troubleshooting: docs/troubleshooting.md"
echo ""
echo "🔧 Commands hữu ích:"
echo "- Xem logs: docker-compose logs -f [service_name]"
echo "- Dừng dịch vụ: docker-compose down"
echo "- Khởi động lại: docker-compose restart"
echo "- Xóa dữ liệu: docker-compose down -v"
