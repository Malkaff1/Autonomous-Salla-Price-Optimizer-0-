import requests
import webbrowser

# 1. Configuration from your Salla Partners Portal
CLIENT_ID = "7237bbdb-4609-4655-8f2b-32ceeb71c08a"
# Ensure this is the latest Secret Key after your "Rolling" action
CLIENT_SECRET = "385e20435589082d82d4fba5e1a9468d2332a03765442171856063f69eaa9976" 
REDIRECT_URI = "https://oauth.pstmn.io/v1/browser-callback"

# 2. Scopes formatting based on Salla documentation
# Use dots for actions and spaces to separate scopes.
SCOPES = "products.read_write"

def get_auth_url():
    """Generates the Authorization URL to get the 'code'"""
    auth_base_url = "https://accounts.salla.sa/oauth2/auth"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "state": "saas_dev_mode"
    }
    # Prepare the URL with parameters
    request_url = requests.Request('GET', auth_base_url, params=params).prepare().url
    return request_url

def exchange_code_for_token(auth_code):
    """Exchanges the authorization code for an Access Token"""
    token_url = "https://accounts.salla.sa/oauth2/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES
    }
    
    print("\n⏳ Exchanging code for token...")
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}

if __name__ == "__main__":
    print("🚀 Opening Salla Authorization page in your browser...")
    url = get_auth_url()
    print(f"🔗 URL: {url}")
    webbrowser.open(url)
    
    print("\n💡 STEP 1: Log in to your Salla store and authorize the app.")
    print("💡 STEP 2: You will be redirected. Copy the 'code' from the URL (e.g., ...code=xyz).")
    
    auth_code = input("\n⌨️ Paste the 'code' here: ").strip()

    if auth_code:
        result = exchange_code_for_token(auth_code)
        
        if "access_token" in result:
            print("\n✅ SUCCESS! Tokens retrieved:")
            print(f"🔑 Access Token: {result.get('access_token')[:30]}...")
            print(f"🔄 Refresh Token: {result.get('refresh_token')}")
            print(f"📅 Expires In: {result.get('expires')} seconds")
            print("\n📝 You can now add these to your .env file.")
        else:
            print(f"\n❌ ERROR from Salla: {result.get('error')}")
            print("Check if 'products.read_write' is updated in Salla Partners Portal.")