#!/usr/bin/env python3
"""
Salla OAuth Bridge Server
A lightweight Flask server to handle Salla OAuth2 authorization flow.
"""

import os
import requests
import webbrowser
import threading
import time
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv, set_key
from urllib.parse import urlencode

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
SALLA_CLIENT_ID = "30d2c6a1-3cde-45e0-8fca-5319670daf91"
SALLA_CLIENT_SECRET = "96cbee3aa77d0b5570bf261f6a52e101ea5e7abc821dee7072bc5b456aa9381c"
CALLBACK_URL = "http://localhost:8000/callback"
TOKEN_URL = "https://accounts.salla.sa/oauth2/token"
AUTH_URL = "https://accounts.salla.sa/oauth2/auth"

# Global variable to track authorization status
auth_status = {"completed": False, "success": False, "message": "", "token": None}

# HTML templates
SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Salla OAuth - Success</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px; 
            background: #f0f8ff; 
        }
        .success { 
            background: #d4edda; 
            color: #155724; 
            padding: 20px; 
            border-radius: 10px; 
            margin: 20px auto; 
            max-width: 600px; 
        }
        .token { 
            background: #fff3cd; 
            color: #856404; 
            padding: 15px; 
            border-radius: 5px; 
            margin: 20px auto; 
            max-width: 800px; 
            word-break: break-all; 
            font-family: monospace; 
        }
        .btn { 
            background: #007bff; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            margin: 10px; 
        }
    </style>
</head>
<body>
    <h1>🎉 Authorization Successful!</h1>
    <div class="success">
        <h2>Your Salla API is now connected!</h2>
        <p>Access token has been obtained and saved to your .env file.</p>
        <p><strong>Store:</strong> {{ store_name }}</p>
        <p><strong>Token expires in:</strong> {{ expires_in }} seconds ({{ hours }} hours)</p>
    </div>
    
    <div class="token">
        <h3>Access Token:</h3>
        <p>{{ access_token }}</p>
    </div>
    
    <p>You can now close this window and return to your terminal.</p>
    <button class="btn" onclick="window.close()">Close Window</button>
    
    <script>
        // Auto-close after 10 seconds
        setTimeout(function() {
            window.close();
        }, 10000);
    </script>
</body>
</html>
"""

ERROR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Salla OAuth - Error</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px; 
            background: #ffe6e6; 
        }
        .error { 
            background: #f8d7da; 
            color: #721c24; 
            padding: 20px; 
            border-radius: 10px; 
            margin: 20px auto; 
            max-width: 600px; 
        }
        .btn { 
            background: #dc3545; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            margin: 10px; 
        }
    </style>
</head>
<body>
    <h1>❌ Authorization Failed</h1>
    <div class="error">
        <h2>Something went wrong</h2>
        <p><strong>Error:</strong> {{ error_message }}</p>
        <p>Please check your app configuration and try again.</p>
    </div>
    
    <button class="btn" onclick="window.close()">Close Window</button>
</body>
</html>
"""

@app.route('/')
def index():
    """Start the OAuth flow."""
    # Build authorization URL
    params = {
        'response_type': 'code',
        'client_id': SALLA_CLIENT_ID,
        'redirect_uri': CALLBACK_URL,
        'scope': 'products:read products:write store:read',
        'state': 'oauth_state_123'
    }
    
    auth_url = f"{AUTH_URL}?{urlencode(params)}"
    
    print(f"🌐 Opening authorization URL: {auth_url}")
    
    # Redirect to Salla authorization
    return f'''
    <html>
    <head>
        <title>Salla OAuth Authorization</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
            .btn {{ background: #28a745; color: white; padding: 15px 30px; 
                    border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h1>🔐 Salla API Authorization</h1>
        <p>Click the button below to authorize your app:</p>
        <a href="{auth_url}" class="btn">Authorize Salla App</a>
        <p><small>This will redirect you to Salla to grant permissions.</small></p>
        
        <script>
            // Auto-redirect after 3 seconds
            setTimeout(function() {{
                window.location.href = "{auth_url}";
            }}, 3000);
        </script>
    </body>
    </html>
    '''

@app.route('/callback')
def callback():
    """Handle the OAuth callback."""
    global auth_status
    
    # Get authorization code
    code = request.args.get('code')
    error = request.args.get('error')
    state = request.args.get('state')
    
    if error:
        print(f"❌ Authorization error: {error}")
        auth_status = {
            "completed": True, 
            "success": False, 
            "message": f"Authorization error: {error}"
        }
        return render_template_string(ERROR_TEMPLATE, error_message=error)
    
    if not code:
        print("❌ No authorization code received")
        auth_status = {
            "completed": True, 
            "success": False, 
            "message": "No authorization code received"
        }
        return render_template_string(ERROR_TEMPLATE, error_message="No authorization code received")
    
    print(f"✅ Authorization code received: {code[:20]}...")
    
    # Exchange code for access token
    try:
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': SALLA_CLIENT_ID,
            'client_secret': SALLA_CLIENT_SECRET,
            'code': code,
            'redirect_uri': CALLBACK_URL
        }
        
        print("🔄 Exchanging code for access token...")
        response = requests.post(TOKEN_URL, data=token_data, timeout=30)
        response.raise_for_status()
        
        token_info = response.json()
        print(f"📋 Token response: {token_info}")
        
        if 'access_token' not in token_info:
            raise Exception(f"No access token in response: {token_info}")
        
        access_token = token_info['access_token']
        refresh_token = token_info.get('refresh_token', '')
        expires_in = token_info.get('expires_in', 3600)
        
        print(f"🎉 Access token obtained: {access_token[:20]}...")
        
        # Test the token by getting store info
        test_response = requests.get(
            'https://api.salla.dev/admin/v2/store/info',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=30
        )
        
        store_name = "Unknown"
        if test_response.status_code == 200:
            store_data = test_response.json()
            store_name = store_data.get('data', {}).get('name', 'Unknown')
            print(f"✅ Token verified! Store: {store_name}")
        else:
            print(f"⚠️  Token test failed: {test_response.status_code}")
        
        # Update .env file
        try:
            set_key('.env', 'SALLA_ACCESS_TOKEN', access_token)
            if refresh_token:
                set_key('.env', 'SALLA_REFRESH_TOKEN', refresh_token)
            print("✅ .env file updated with new token")
        except Exception as e:
            print(f"⚠️  Could not update .env file: {e}")
        
        # Update global status
        auth_status = {
            "completed": True,
            "success": True,
            "message": "Authorization successful",
            "token": access_token,
            "store_name": store_name,
            "expires_in": expires_in
        }
        
        # Return success page
        return render_template_string(
            SUCCESS_TEMPLATE,
            access_token=access_token,
            store_name=store_name,
            expires_in=expires_in,
            hours=expires_in // 3600
        )
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Token exchange failed: {str(e)}"
        print(f"❌ {error_msg}")
        auth_status = {
            "completed": True,
            "success": False,
            "message": error_msg
        }
        return render_template_string(ERROR_TEMPLATE, error_message=error_msg)
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ {error_msg}")
        auth_status = {
            "completed": True,
            "success": False,
            "message": error_msg
        }
        return render_template_string(ERROR_TEMPLATE, error_message=error_msg)

@app.route('/status')
def status():
    """Check authorization status."""
    return jsonify(auth_status)

def start_auth_flow():
    """Start the OAuth authorization flow."""
    global auth_status
    
    print("🚀 Starting Salla OAuth2 Authorization Flow")
    print("=" * 60)
    print(f"Client ID: {SALLA_CLIENT_ID}")
    print(f"Callback URL: {CALLBACK_URL}")
    print(f"Scopes: products:read products:write store:read")
    print()
    
    # Reset status
    auth_status = {"completed": False, "success": False, "message": "Starting..."}
    
    # Start Flask server in background
    def run_server():
        app.run(host='localhost', port=8000, debug=False, use_reloader=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Open browser
    auth_url = "http://localhost:8000"
    print(f"🌐 Opening browser: {auth_url}")
    webbrowser.open(auth_url)
    
    print("⏳ Waiting for authorization (timeout: 5 minutes)...")
    print("Please complete the authorization in your browser.")
    
    # Wait for completion
    timeout = 300  # 5 minutes
    start_time = time.time()
    
    while not auth_status["completed"] and (time.time() - start_time) < timeout:
        time.sleep(1)
    
    if not auth_status["completed"]:
        print("❌ Authorization timed out!")
        return False
    
    if auth_status["success"]:
        print("🎉 Authorization completed successfully!")
        print(f"✅ Access token saved to .env file")
        return True
    else:
        print(f"❌ Authorization failed: {auth_status['message']}")
        return False

if __name__ == "__main__":
    print("🔐 Salla OAuth2 Authorization Server")
    print("This will help you get a valid access token for your Salla store.")
    print()
    
    # Check if Flask is installed
    try:
        import flask
    except ImportError:
        print("❌ Flask is not installed. Installing...")
        os.system("pip install flask")
        import flask
    
    # Start the authorization flow
    success = start_auth_flow()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Test your connection: python test_new_token.py")
        print("2. Run your price optimizer: python run_optimizer.py")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Check your Client ID and Client Secret")
        print("2. Verify your app is properly configured in Salla Partner Dashboard")
        print("3. Make sure your app has the required permissions")
        print("4. Ensure your store has installed the app")