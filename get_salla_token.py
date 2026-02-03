#!/usr/bin/env python3
"""
Simple Salla OAuth2 Token Generator
This script helps you get a valid access token using your Client ID and Client Secret.
"""

import requests
import urllib.parse
import webbrowser
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            self.server.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Authorization Successful!</h1><p>You can close this window and return to your terminal.</p></body></html>')
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Authorization Failed</h1>')
    
    def log_message(self, format, *args):
        pass  # Suppress logs

def get_access_token():
    print("🔐 Salla OAuth2 Token Generator")
    print("=" * 50)
    
    # Get credentials
    print("You need your Salla App credentials from https://salla.dev")
    print("Go to: My Apps → Your App → View Details")
    print()
    
    client_id = input("Enter your Client ID: ").strip()
    if not client_id:
        print("❌ Client ID is required!")
        return
    
    client_secret = input("Enter your Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret is required!")
        return
    
    # OAuth2 flow
    redirect_uri = "http://localhost:8000/callback"
    scope = "products:read products:write store:read"
    
    auth_url = (
        f"https://accounts.salla.sa/oauth2/auth?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"scope={urllib.parse.quote(scope)}&"
        f"state=oauth_state"
    )
    
    print(f"\n🌐 Step 1: Opening browser for authorization...")
    print(f"URL: {auth_url}")
    
    # Start callback server
    server = HTTPServer(('localhost', 8000), CallbackHandler)
    server.auth_code = None
    
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Open browser
    webbrowser.open(auth_url)
    
    print(f"\n⏳ Waiting for authorization (timeout: 5 minutes)...")
    print(f"Please authorize the app in your browser.")
    
    # Wait for code
    timeout = 300
    start_time = time.time()
    
    while server.auth_code is None and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    server.shutdown()
    
    if server.auth_code is None:
        print("❌ Authorization timed out!")
        return
    
    print(f"✅ Authorization code received!")
    
    # Exchange code for token
    print(f"\n🔄 Step 2: Getting access token...")
    
    token_url = "https://accounts.salla.sa/oauth2/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': server.auth_code,
        'redirect_uri': redirect_uri
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        
        token_info = response.json()
        
        if 'access_token' in token_info:
            access_token = token_info['access_token']
            refresh_token = token_info.get('refresh_token', '')
            expires_in = token_info.get('expires_in', 3600)
            
            print(f"🎉 SUCCESS! Access token obtained!")
            print(f"=" * 50)
            print(f"Access Token: {access_token}")
            print(f"Refresh Token: {refresh_token}")
            print(f"Expires In: {expires_in} seconds ({expires_in//3600} hours)")
            
            # Test the token
            print(f"\n🧪 Testing the token...")
            test_response = requests.get(
                'https://api.salla.dev/admin/v2/store/info',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if test_response.status_code == 200:
                store_data = test_response.json()
                print(f"✅ Token works! Store: {store_data.get('data', {}).get('name', 'Unknown')}")
                
                # Update .env file
                try:
                    with open('.env', 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    updated_lines = []
                    token_updated = False
                    
                    for line in lines:
                        if line.startswith('SALLA_ACCESS_TOKEN='):
                            updated_lines.append(f'SALLA_ACCESS_TOKEN={access_token}\n')
                            token_updated = True
                        else:
                            updated_lines.append(line)
                    
                    if not token_updated:
                        updated_lines.append(f'SALLA_ACCESS_TOKEN={access_token}\n')
                    
                    with open('.env', 'w', encoding='utf-8') as f:
                        f.writelines(updated_lines)
                    
                    print(f"✅ .env file updated!")
                    
                except Exception as e:
                    print(f"⚠️  Could not update .env: {e}")
                    print(f"Please manually update SALLA_ACCESS_TOKEN in .env file")
                
                return access_token
            else:
                print(f"❌ Token test failed: {test_response.status_code}")
                print(f"Response: {test_response.text}")
        else:
            print(f"❌ No access token in response: {token_info}")
            
    except Exception as e:
        print(f"❌ Token exchange failed: {e}")

if __name__ == "__main__":
    print("This script will help you get a valid Salla access token.")
    print("You need:")
    print("1. Salla Partner account (https://salla.dev)")
    print("2. Created app with proper permissions")
    print("3. Your Client ID and Client Secret")
    print()
    
    get_access_token()