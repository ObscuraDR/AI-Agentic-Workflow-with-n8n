#!/usr/bin/env python3
"""
Gmail OAuth2 Setup Script for n8n
Script thiết lập OAuth2 cho Gmail API trong n8n
"""

import os
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

try:
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    import googleapiclient.discovery
except ImportError:
    print("Installing required packages...")
    os.system("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    import googleapiclient.discovery

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if 'code' in params:
            self.server.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html><body>
                <h1>Authentication successful!</h1>
                <p>You can close this window and return to the terminal.</p>
                </body></html>
            """)
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress log messages

def setup_gmail_oauth():
    """Setup Gmail OAuth2 credentials for n8n"""
    
    print("🔧 Gmail OAuth2 Setup for n8n")
    print("=" * 50)
    
    # Check if credentials.json exists
    creds_file = Path("credentials.json")
    if not creds_file.exists():
        print("❌ credentials.json not found!")
        print("\nPlease follow these steps:")
        print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Gmail API")
        print("4. Go to Credentials -> Create Credentials -> OAuth client ID")
        print("5. Select 'Web application'")
        print("6. Add redirect URI: http://localhost:8080/callback")
        print("7. Download the JSON file and save it as 'credentials.json'")
        print("8. Run this script again")
        return
    
    # Load client configuration
    try:
        with open(creds_file, 'r') as f:
            client_config = json.load(f)
    except Exception as e:
        print(f"❌ Error loading credentials.json: {e}")
        return
    
    # Check if token already exists
    token_file = Path("token.json")
    if token_file.exists():
        print("📋 token.json already exists. Checking validity...")
        try:
            creds = Credentials.from_authorized_user_file(str(token_file))
            if creds.valid and creds.expiry and creds.expiry > time.time():
                print("✅ Existing token is valid!")
                print_n8n_config(creds)
                return
            elif creds.expired and creds.refresh_token:
                print("🔄 Token expired, attempting refresh...")
                creds.refresh(Request())
                with open(token_file, 'w') as f:
                    f.write(creds.to_json())
                print("✅ Token refreshed successfully!")
                print_n8n_config(creds)
                return
        except Exception as e:
            print(f"❌ Error checking existing token: {e}")
    
    # Start local server for callback
    server = HTTPServer(('localhost', 8080), CallbackHandler)
    server.auth_code = None
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Create OAuth flow
    flow = Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
    )
    flow.redirect_uri = 'http://localhost:8080/callback'
    
    # Generate authorization URL
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    print("\n🌐 Opening browser for authorization...")
    print(f"📎 If browser doesn't open, visit: {auth_url}")
    
    # Open browser
    try:
        webbrowser.open(auth_url)
    except:
        print("⚠️  Could not open browser automatically. Please visit the URL manually.")
    
    # Wait for authorization
    print("⏳ Waiting for authorization...")
    while server.auth_code is None:
        time.sleep(1)
    
    # Exchange code for credentials
    try:
        flow.fetch_token(code=server.auth_code)
        creds = flow.credentials
        
        # Save credentials
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
        
        print("✅ Authorization successful!")
        print_n8n_config(creds)
        
    except Exception as e:
        print(f"❌ Error during authorization: {e}")
    
    finally:
        server.shutdown()
        server.server_close()

def print_n8n_config(creds):
    """Print n8n configuration"""
    print("\n" + "=" * 50)
    print("📋 n8n Gmail OAuth2 Configuration")
    print("=" * 50)
    
    # Load client config to get client_id and client_secret
    with open("credentials.json", 'r') as f:
        client_config = json.load(f)
    
    print("\n🔧 Add these credentials in n8n:")
    print("1. Go to n8n -> Credentials -> Add Credential")
    print("2. Select 'Gmail OAuth2 API'")
    print("3. Fill in the following:")
    print(f"   - Client ID: {client_config['web']['client_id']}")
    print(f"   - Client Secret: {client_config['web']['client_secret']}")
    print(f"   - Refresh Token: {creds.refresh_token}")
    print(f"   - Access Token: {creds.token}")
    print(f"   - Expires In: {int(creds.expiry.timestamp() - time.time()) if creds.expiry else ''}")
    
    print("\n💾 Save this information for backup:")
    config = {
        "client_id": client_config['web']['client_id'],
        "client_secret": client_config['web']['client_secret'],
        "refresh_token": creds.refresh_token,
        "access_token": creds.token,
        "expires_at": creds.expiry.isoformat() if creds.expiry else None
    }
    
    with open("gmail-n8n-config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    print("   Configuration saved to: gmail-n8n-config.json")
    
    print("\n🧪 Test the setup:")
    print("1. In n8n, create a Gmail trigger node")
    print("2. Select the OAuth2 credential you just created")
    print("3. Test the connection")
    print("4. If successful, the workflow should be able to read emails")

def test_gmail_connection():
    """Test Gmail API connection"""
    token_file = Path("token.json")
    if not token_file.exists():
        print("❌ No token.json found. Please run setup first.")
        return
    
    try:
        creds = Credentials.from_authorized_user_file(str(token_file))
        if not creds.valid:
            print("❌ Token is invalid. Please run setup again.")
            return
        
        service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
        
        # Test API call
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        print(f"✅ Gmail connection successful!")
        print(f"📧 Found {len(labels)} labels in your Gmail account")
        
        # Show some common labels
        common_labels = ['INBOX', 'SENT', 'DRAFTS', 'SPAM', 'TRASH']
        for label in labels:
            if label['id'] in common_labels:
                print(f"   - {label['id']}: {label['name']}")
        
    except Exception as e:
        print(f"❌ Error testing Gmail connection: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_gmail_connection()
    else:
        setup_gmail_oauth()
