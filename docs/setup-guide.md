# Complete Setup Guide
# Hướng dẫn cài đặt đầy đủ

## API Configuration

### 1. OpenAI API Setup

#### Bước 1: Tạo tài khoản OpenAI
1. Truy cập [https://platform.openai.com/](https://platform.openai.com/)
2. Đăng ký hoặc đăng nhập tài khoản
3. Xác minh email và số điện thoại

#### Bước 2: Tạo API Key
1. Vào Dashboard → API Keys
2. Click "Create new secret key"
3. Đặt tên cho API key (ví dụ: "n8n-workflow")
4. Copy và lưu trữ API key một cách an toàn

#### Bước 3: Cấu hình trong n8n
1. Trong n8n, tạo credential "OpenAI"
2. Dán API key vào trường "API Key"
3. Chọn model (gpt-4 hoặc gpt-3.5-turbo)

### 2. Gmail API Setup

#### Bước 1: Tạo Google Cloud Project
1. Truy cập [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project hiện có
3. Kích hoạt Gmail API

#### Bước 2: Tạo OAuth 2.0 Credentials
1. Vào "Credentials" → "Create Credentials" → "OAuth client ID"
2. Chọn "Web application"
3. Thêm redirect URI: `http://localhost:5678/oauth2/callback`
4. Tải xuống file JSON và lưu trữ an toàn

#### Bước 3: Lấy Refresh Token
1. Sử dụng OAuth 2.0 Playground để lấy refresh token
2. Hoặc sử dụng script Python/Node.js để authorization

#### Bước 4: Cấu hình trong n8n
1. Tạo credential "Gmail OAuth2"
2. Điền Client ID, Client Secret, và Refresh Token

### 3. Slack API Setup

#### Bước 1: Tạo Slack App
1. Truy cập [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Đặt tên app và chọn workspace

#### Bước 2: Cấu hình Permissions
1. Vào "OAuth & Permissions"
2. Thêm các Bot Token Scopes:
   - `chat:write`
   - `chat:write.public`
   - `channels:read`
   - `users:read`

#### Bước 3: Cài đặt vào Workspace
1. Click "Install to Workspace"
2. Copy Bot User OAuth Token (bắt đầu với `xoxb-`)

#### Bước 4: Tạo Webhook (tùy chọn)
1. Vào "Incoming Webhooks"
2. Activate "Incoming Webhooks"
3. Add new webhook to channel
4. Copy Webhook URL

#### Bước 5: Cấu hình trong n8n
1. Tạo credential "Slack"
2. Điền Bot Token hoặc Webhook URL

### 4. Discord API Setup

#### Bước 1: Tạo Discord Application
1. Truy cập [https://discord.com/developers/applications](https://discord.com/developers/applications)
2. Click "New Application"
3. Đặt tên và tạo application

#### Bước 2: Tạo Bot
1. Vào "Bot" → "Add Bot"
2. Copy Bot Token
3. Kích hoạt các privileges:
   - Send Messages
   - Read Message History
   - Embed Links

#### Bước 3: Mời Bot vào Server
1. Vào "OAuth2" → "URL Generator"
2. Chọn scopes: `bot`
3. Chọn permissions: `Send Messages`, `Read Messages`
4. Copy URL và mời bot vào server

#### Bước 4: Lấy Channel ID
1. Bật Developer Mode trong Discord settings
2. Right-click channel → "Copy Channel ID"

#### Bước 5: Cấu hình trong n8n
1. Tạo credential "Discord"
2. Điền Bot Token và Channel ID

## Environment Variables

### Tạo file .env
```bash
cp .env.example .env
```

### Điền thông tin API
```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-key-here

# Gmail
GMAIL_CLIENT_ID=your-gmail-client-id
GMAIL_CLIENT_SECRET=your-gmail-client-secret
GMAIL_REFRESH_TOKEN=your-gmail-refresh-token

# Slack
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Discord
DISCORD_BOT_TOKEN=your-discord-bot-token
DISCORD_CHANNEL_ID=123456789012345678
```

## Workflow Documentation

### Email Analysis Workflow

#### Tổng quan
Workflow này tự động phân tích email đến, xác định khiếu nại, soạn thảo phản hồi và gửi thông báo.

#### Các bước hoạt động

##### 1. Gmail Trigger
- **Loại**: Email Trigger
- **Tần suất**: Mỗi phút
- **Chức năng**: Lắng nghe email mới trong Gmail
- **Cấu hình cần thiết**: Gmail OAuth2 credentials

##### 2. Email Processor
- **Loại**: Code Node (JavaScript)
- **Chức năng**: 
  - Trích xuất nội dung email
  - Xác định sender email
  - Kiểm tra keywords khiếu nại
- **Output**: Email đã được xử lý với metadata

##### 3. AI Email Analysis
- **Loại**: OpenAI Node hoặc Ollama Code Node
- **Model**: GPT-4 hoặc Llama 3.2
- **Chức năng**:
  - Phân tích nội dung email
  - Xác định loại khiếu nại
  - Tính điểm sentiment
  - Xác định mức độ khẩn cấp
- **Output**: JSON với kết quả phân tích

##### 4. Is Complaint? (IF Node)
- **Loại**: Condition Node
- **Điều kiện**: `is_complaint == true`
- **Chức năng**: Phân luồng email dựa trên kết quả phân tích

##### 5A. Save to Database (Luồng khiếu nại)
- **Loại**: PostgreSQL Node
- **Bảng**: `email_complaints`
- **Chức năng**: Lưu thông tin khiếu nại vào database

##### 5B. Log Non-Complaint (Luồng không khiếu nại)
- **Loại**: Code Node
- **Chức năng**: Ghi nhật ký email không phải khiếu nại

##### 6. Draft AI Response
- **Loại**: OpenAI Node hoặc Ollama Code Node
- **Model**: GPT-4 hoặc Llama 3.2
- **Chức năng**: Soạn thảo phản hồi chuyên nghiệp
- **Ngôn ngữ**: Tiếng Việt
- **Tone**: Chuyên nghiệp, đồng cảm

##### 7. Save Response to DB
- **Loại**: PostgreSQL Node
- **Bảng**: `ai_responses`
- **Chức năng**: Lưu phản hồi do AI tạo ra

##### 8. Send Slack Notification
- **Loại**: Slack Node
- **Chức năng**: Gửi thông báo đến kênh Slack
- **Nội dung**: Thông tin khiếu nại và trạng thái xử lý

##### 9. Log Notification
- **Loại**: PostgreSQL Node
- **Bảng**: `notification_logs`
- **Chức năng**: Ghi nhật ký thông báo đã gửi

### Database Schema

#### email_complaints
```sql
CREATE TABLE email_complaints (
    id SERIAL PRIMARY KEY,
    email_id VARCHAR(255) UNIQUE NOT NULL,
    sender_email VARCHAR(255) NOT NULL,
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_complaint BOOLEAN DEFAULT FALSE,
    complaint_category VARCHAR(100),
    sentiment_score FLOAT,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### ai_responses
```sql
CREATE TABLE ai_responses (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER REFERENCES email_complaints(id),
    response_content TEXT NOT NULL,
    response_tone VARCHAR(50) DEFAULT 'professional',
    confidence_score FLOAT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'draft'
);
```

#### notification_logs
```sql
CREATE TABLE notification_logs (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER REFERENCES email_complaints(id),
    platform VARCHAR(50) NOT NULL,
    message_content TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'sent',
    error_message TEXT
);
```

### Testing APIs

#### Test OpenAI API
```bash
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello, world!"}]
  }'
```

#### Test Gmail API
```bash
curl -X GET "https://www.googleapis.com/gmail/v1/users/me/messages" \
  -H "Authorization: Bearer $GMAIL_ACCESS_TOKEN"
```

#### Test Slack API
```bash
curl -X POST -H 'Authorization: Bearer $SLACK_BOT_TOKEN' \
  -H 'Content-type: application/json' \
  --data '{"channel":"#general","text":"Hello from n8n!"}' \
  https://slack.com/api/chat.postMessage
```

#### Test Discord API
```bash
curl -X POST -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello from n8n!"}' \
  https://discord.com/api/channels/$DISCORD_CHANNEL_ID/messages
```

### Security Best Practices

#### Luôn luôn:
- Sử dụng environment variables thay vì hardcode API keys
- Giới hạn permissions của API keys
- Sử dụng HTTPS cho tất cả requests
- Thường xuyên rotation API keys
- Backup credentials một cách an toàn

#### Không bao giờ:
- Commit API keys vào git
- Chia sẻ API keys public
- Sử dụng API keys trong client-side code
- Bỏ qua rate limits

### Testing và Validation

#### Test Cases
1. **Email khiếu nại**: Verify phân tích và lưu database
2. **Email thông thường**: Verify không lưu vào complaint table
3. **Email spam**: Verify filter và ignore
4. **AI Response**: Verify quality và tone của phản hồi
5. **Notifications**: Verify Slack notifications được gửi

#### Monitoring Metrics
- Số lượng email processed per hour
- Tỷ lệ email được xác định là khiếu nại
- Thời gian xử lý trung bình
- Số lượng notifications thành công/thất bại
- AI response quality scores

### Troubleshooting

#### Common Issues
1. **Gmail API rate limit**: Implement exponential backoff
2. **OpenAI API timeout**: Increase timeout settings
3. **Database connection failed**: Check credentials and network
4. **Slack webhook failed**: Verify token and channel permissions

#### Error Handling
- Implement retry logic cho API calls
- Log errors với sufficient detail
- Send alert notifications cho critical failures
- Fallback mechanisms cho service outages

### Performance Optimization

#### Database Optimization
- Indexes cho frequently queried columns
- Connection pooling
- Regular maintenance and cleanup

#### API Optimization
- Batch processing cho multiple emails
- Caching cho repeated requests
- Rate limiting để avoid API limits

#### Workflow Optimization
- Parallel processing khi có thể
- Conditional execution để skip unnecessary steps
- Resource management cho memory-intensive operations

### Security Considerations

#### Data Protection
- Encrypt sensitive email content
- Implement access controls cho database
- Regular backup và recovery procedures

#### API Security
- Secure storage của API keys
- Implement rate limiting
- Monitor for unusual activity

#### Compliance
- GDPR compliance cho email data
- Data retention policies
- Audit trails cho all operations
