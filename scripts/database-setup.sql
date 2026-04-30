-- Database setup for AI Agentic Workflow with n8n
-- Cơ sở dữ liệu cho quy trình tác nhân AI

-- Table for storing email complaints
-- Bảng lưu trữ khiếu nại email
CREATE TABLE IF NOT EXISTS email_complaints (
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

-- Table for storing AI-generated responses
-- Bảng lưu trữ phản hồi do AI tạo ra
CREATE TABLE IF NOT EXISTS ai_responses (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER REFERENCES email_complaints(id) ON DELETE CASCADE,
    response_content TEXT NOT NULL,
    response_tone VARCHAR(50) DEFAULT 'professional',
    confidence_score FLOAT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'draft' -- draft, approved, sent
);

-- Table for storing notification logs
-- Bảng lưu trữ nhật ký thông báo
CREATE TABLE IF NOT EXISTS notification_logs (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER REFERENCES email_complaints(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- slack, discord
    message_content TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'sent', -- sent, failed
    error_message TEXT
);

-- Table for storing workflow execution logs
-- Bảng lưu trữ nhật ký thực thi workflow
CREATE TABLE IF NOT EXISTS workflow_logs (
    id SERIAL PRIMARY KEY,
    workflow_name VARCHAR(100) NOT NULL,
    execution_id VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL, -- success, error, running
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT
);

-- Create indexes for better performance
-- Tạo indexes để cải thiện hiệu suất
CREATE INDEX IF NOT EXISTS idx_email_complaints_sender ON email_complaints(sender_email);
CREATE INDEX IF NOT EXISTS idx_email_complaints_received_at ON email_complaints(received_at);
CREATE INDEX IF NOT EXISTS idx_email_complaints_is_complaint ON email_complaints(is_complaint);
CREATE INDEX IF NOT EXISTS idx_ai_responses_complaint_id ON ai_responses(complaint_id);
CREATE INDEX IF NOT EXISTS idx_ai_responses_status ON ai_responses(status);
CREATE INDEX IF NOT EXISTS idx_notification_logs_platform ON notification_logs(platform);
CREATE INDEX IF NOT EXISTS idx_notification_logs_sent_at ON notification_logs(sent_at);
CREATE INDEX IF NOT EXISTS idx_workflow_logs_execution_id ON workflow_logs(execution_id);
CREATE INDEX IF NOT EXISTS idx_workflow_logs_status ON workflow_logs(status);

-- Insert sample data for testing (optional)
-- Chèn dữ liệu mẫu để kiểm tra (tùy chọn)
INSERT INTO email_complaints (email_id, sender_email, subject, content, is_complaint, complaint_category, sentiment_score)
VALUES 
    ('test_email_001', 'customer@example.com', 'Phàn nàn về chất lượng dịch vụ', 'Tôi rất không hài lòng với dịch vụ của quý công ty...', true, 'service_quality', -0.7),
    ('test_email_002', 'user@example.com', 'Câu hỏi về sản phẩm', 'Tôi muốn hỏi thêm về tính năng của sản phẩm...', false, 'inquiry', 0.1)
ON CONFLICT (email_id) DO NOTHING;

-- Grant permissions to the n8n user
-- Cấp quyền cho người dùng n8n
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO n8n_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO n8n_user;
