# Quick Gmail OAuth2 Setup Guide
# Hướng dẫn nhanh thiết lập Gmail OAuth2

## 🚀 Bước 1: Tạo Google Cloud Project

### 1.1 Truy cập Google Cloud Console
1. Mở: https://console.cloud.google.com/
2. Đăng nhập bằng tài khoản Google của bạn
3. Click vào project selector (góc trên cùng)

### 1.2 Tạo project mới
1. Click **"NEW PROJECT"**
2. Đặt tên: "Email Analysis Workflow"
3. Click **"CREATE"**

## 🔧 Bước 2: Bật Gmail API

### 2.1 Tìm Gmail API
1. Trong project mới, click **"APIs & Services"** → **"Library"**
2. Tìm kiếm: **"Gmail API"**
3. Click vào **"Gmail API"** từ kết quả

### 2.2 Bật API
1. Click **"ENABLE"**
2. Chờ vài giây để API được bật

## 🔑 Bước 3: Tạo OAuth2 Credentials

### 3.1 Vào OAuth consent screen
1. Click **"APIs & Services"** → **"OAuth consent screen"**
2. Chọn **"External"** → Click **"CREATE"**

### 3.2 Cấu hình OAuth consent screen
1. **App name**: "Email Analysis Workflow"
2. **User support email**: email của bạn
3. **Developer contact information**: email của bạn
4. Click **"SAVE AND CONTINUE"**

### 3.3 Scopes (Bỏ qua)
1. Click **"SAVE AND CONTINUE"** (không cần thêm scopes)

### 3.4 Test users
1. Click **"+ ADD USERS"**
2. Thêm email của bạn vào
3. Click **"SAVE AND CONTINUE"**

### 3.5 Xem lại và Publish
1. Kiểm tra lại thông tin
2. Click **"BACK TO DASHBOARD"**

## 🎯 Bước 4: Tạo Credentials

### 4.1 Vào Credentials
1. Click **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"**
3. Chọn **"OAuth client ID"**

### 4.2 Cấu hình OAuth client
1. **Application type**: Chọn **"Web application"**
2. **Name**: "n8n Gmail Integration"
3. **Authorized redirect URIs**: Click **"+ ADD URI"**
   - Điền: `http://localhost:5678/rest/oauth2-credential/callback`

### 4.3 Tạo credentials
1. Click **"CREATE"**
2. **SAVE Client ID và Client Secret** (cần cho n8n)

## 🔗 Bước 5: Lấy Refresh Token

### 5.1 Sử dụng script của chúng tôi
Chạy script đã có trong project:
```bash
cd "w:/AI Agentic Workflow with n8n"
py scripts/gmail-oauth-setup.py
```

### 5.2 Hoặc làm thủ công
1. Mở trình duyệt với URL:
   ```
   https://accounts.google.com/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:5678/rest/oauth2-credential/callback&scope=https://www.googleapis.com/auth/gmail.readonly&response_type=code&access_type=offline
   ```
2. Đăng nhập và cho phép
3. Copy authorization code
4. Sử dụng code để lấy refresh token

## 📋 Bước 6: Cấu hình trong n8n

### 6.1 Thêm credential
1. Trong n8n: **Settings** → **Credentials**
2. Click **"+ Add credential"**
3. Chọn **"Gmail OAuth2 API"**

### 6.2 Điền thông tin
- **Name**: "Gmail OAuth2"
- **Client ID**: Paste từ step 4.3
- **Client Secret**: Paste từ step 4.3
- **Refresh Token**: Paste từ step 5

### 6.3 Lưu và test
1. Click **"Save"**
2. Test credential bằng cách click **"Test"**

## ⚡ Quick Alternative: Use App Password

Nếu OAuth2 quá phức tạp, có thể dùng App Password:

### 1. Bật 2-Step Verification
1. Vào: https://myaccount.google.com/security
2. Bật **2-Step Verification**

### 2. Tạo App Password
1. Vào: https://myaccount.google.com/apppasswords
2. Select app: **"Mail"**
3. Select device: **"Other (Custom name)"**
4. Đặt tên: "n8n"
5. Copy password (16 ký tự)

### 3. Dùng trong n8n
1. Thêm credential: **"Gmail"** (không phải OAuth2)
2. Điền email và App Password

## ✅ Kiểm tra
Sau khi cấu hình:
1. Test credential trong n8n
2. Test Gmail trigger node
3. Kiểm tra workflow có thể đọc email

## 🚨 Lưu ý quan trọng
- **Client ID/Secret**: Bảo mật, không chia sẻ
- **Refresh Token**: Cần refresh định kỳ
- **App Password**: Dễ hơn nhưng kém an toàn hơn OAuth2

Chọn phương pháp phù hợp với nhu cầu của bạn!
