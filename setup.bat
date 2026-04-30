@echo off
REM AI Agentic Workflow with n8n - Setup Script for Windows
REM Script cài đặt cho Quy trình Tác nhân AI với n8n trên Windows

echo 🚀 Bắt đầu cài đặt AI Agentic Workflow với n8n...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker chưa được cài đặt. Vui lòng cài đặt Docker Desktop trước.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose chưa được cài đặt. Vui lòng cài đặt Docker Compose trước.
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Tạo các thư mục cần thiết...
if not exist "n8n\workflows" mkdir n8n\workflows
if not exist "scripts" mkdir scripts
if not exist "docs" mkdir docs
if not exist "examples\sample-emails" mkdir examples\sample-emails
if not exist "examples\test-data" mkdir examples\test-data

REM Copy environment file
if not exist ".env" (
    echo 📝 Tạo file .env từ template...
    copy .env.example .env
    echo ⚠️  Vui lòng chỉnh sửa file .env với thông tin API keys của bạn!
) else (
    echo ✅ File .env đã tồn tại
)

REM Create sample email data
echo 📧 Tạo dữ liệu email mẫu...
echo Subject: Phàn nàn về chất lượng dịch vụ > examples\sample-emails\complaint-sample.txt
echo. >> examples\sample-emails\complaint-sample.txt
echo Kính gửi đội ngũ hỗ trợ, >> examples\sample-emails\complaint-sample.txt
echo. >> examples\sample-emails\complaint-sample.txt
echo Tôi rất không hài lòng với dịch vụ của quý công ty trong tuần vừa qua. >> examples\sample-emails\complaint-sample.txt
echo Sản phẩm tôi nhận được bị lỗi và không hoạt động như quảng cáo. >> examples\sample-emails\complaint-sample.txt
echo. >> examples\sample-emails\complaint-sample.txt
echo Tôi đã liên hệ hỗ trợ 3 lần nhưng vẫn chưa nhận được giải pháp thỏa đáng. >> examples\sample-emails\complaint-sample.txt
echo Thời gian chờ đợi quá lâu và nhân viên hỗ trợ không chuyên nghiệp. >> examples\sample-emails\complaint-sample.txt
echo. >> examples\sample-emails\complaint-sample.txt
echo Mong muốn được giải quyết sớm nhất. >> examples\sample-emails\complaint-sample.txt
echo. >> examples\sample-emails\complaint-sample.txt
echo Trân trọng, >> examples\sample-emails\complaint-sample.txt
echo Nguyễn Văn A >> examples\sample-emails\complaint-sample.txt

echo Subject: Câu hỏi về tính năng sản phẩm > examples\sample-emails\inquiry-sample.txt
echo. >> examples\sample-emails\inquiry-sample.txt
echo Xin chào đội ngũ, >> examples\sample-emails\inquiry-sample.txt
echo. >> examples\sample-emails\inquiry-sample.txt
echo Tôi muốn hỏi thêm về tính năng mới của sản phẩm ABC. >> examples\sample-emails\inquiry-sample.txt
echo Liệu có thể tích hợp với hệ thống hiện tại của chúng tôi không? >> examples\sample-emails\inquiry-sample.txt
echo. >> examples\sample-emails\inquiry-sample.txt
echo Cảm ơn thông tin. >> examples\sample-emails\inquiry-sample.txt

REM Create test data for database
echo 🗄️ Tạo dữ liệu test cho database...
echo [ > examples\test-data\test-complaints.json
echo   { >> examples\test-data\test-complaints.json
echo     "email_id": "test_001", >> examples\test-data\test-complaints.json
echo     "sender_email": "customer1@example.com", >> examples\test-data\test-complaints.json
echo     "subject": "Phàn nàn về giao hàng", >> examples\test-data\test-complaints.json
echo     "content": "Đơn hàng của tôi bị trễ 3 ngày...", >> examples\test-data\test-complaints.json
echo     "is_complaint": true, >> examples\test-data\test-complaints.json
echo     "complaint_category": "shipping", >> examples\test-data\test-complaints.json
echo     "sentiment_score": -0.8 >> examples\test-data\test-complaints.json
echo   }, >> examples\test-data\test-complaints.json
echo   { >> examples\test-data\test-complaints.json
echo     "email_id": "test_002", >> examples\test-data\test-complaints.json
echo     "sender_email": "customer2@example.com", >> examples\test-data\test-complaints.json
echo     "subject": "Cảm ơn dịch vụ tốt", >> examples\test-data\test-complaints.json
echo     "content": "Tôi rất hài lòng với sản phẩm...", >> examples\test-data\test-complaints.json
echo     "is_complaint": false, >> examples\test-data\test-complaints.json
echo     "complaint_category": "feedback", >> examples\test-data\test-complaints.json
echo     "sentiment_score": 0.9 >> examples\test-data\test-complaints.json
echo   } >> examples\test-data\test-complaints.json
echo ] >> examples\test-data\test-complaints.json

REM Start services
echo 🐳 Khởi động dịch vụ Docker...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Chờ dịch vụ khởi động...
timeout /t 30 /nobreak >nul

REM Check if services are running
echo 🔍 Kiểm tra trạng thái dịch vụ...
docker-compose ps

REM Test database connection
echo 🗄️ Kiểm tra kết nối database...
docker-compose exec -T postgres psql -U n8n_user -d n8n_workflow -c "SELECT version();" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Database connection successful
) else (
    echo ❌ Database connection failed
)

REM Test n8n
echo 🔧 Kiểm tra n8n...
curl -s http://localhost:5678/healthz >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ n8n is running
) else (
    echo ⚠️  n8n might still be starting up
)

echo.
echo 🎉 Cài đặt hoàn tất!
echo.
echo 📋 Các bước tiếp theo:
echo 1. Chỉnh sửa file .env với API keys của bạn
echo 2. Truy cập n8n tại: http://localhost:5678
echo 3. Import workflow từ file: n8n\workflows\email-analysis-workflow.json
echo 4. Cấu hình credentials cho Gmail, OpenAI, và Slack
echo 5. Bắt đầu workflow và kiểm tra
echo.
echo 📚 Tài liệu tham khảo:
echo - Hướng dẫn API: docs\api-setup-guide.md
echo - Workflow documentation: docs\workflow-documentation.md
echo - Troubleshooting: docs\troubleshooting.md
echo.
echo 🔧 Commands hữu ích:
echo - Xem logs: docker-compose logs -f [service_name]
echo - Dừng dịch vụ: docker-compose down
echo - Khởi động lại: docker-compose restart
echo - Xóa dữ liệu: docker-compose down -v
echo.
pause
