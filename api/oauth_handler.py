"""
FastAPI OAuth2 Handler for Salla Multi-Tenant Integration
Handles the complete OAuth flow and store onboarding
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from urllib.parse import urlencode
import requests
import os
from dotenv import load_dotenv

from database.db import get_db_session, DatabaseManager
from database.models import Store, ActivityLog

load_dotenv()

app = FastAPI(title="Salla Price Optimizer OAuth Handler")

# OAuth Configuration
SALLA_AUTH_URL = "https://accounts.salla.sa/oauth2/auth"
SALLA_TOKEN_URL = "https://accounts.salla.sa/oauth2/token"
SALLA_USER_INFO_URL = "https://accounts.salla.sa/oauth2/user/info"
CALLBACK_URL = os.getenv("OAUTH_CALLBACK_URL", "http://localhost:8000/oauth/callback")


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "Salla Price Optimizer OAuth Handler",
        "status": "running",
        "endpoints": {
            "authorize": "/oauth/authorize",
            "callback": "/oauth/callback",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/oauth/authorize")
async def authorize(client_id: str = None, client_secret: str = None):
    """
    Step 1: Redirect user to Salla authorization page
    
    Usage:
        /oauth/authorize?client_id=YOUR_CLIENT_ID&client_secret=YOUR_SECRET
    
    Or set SALLA_CLIENT_ID and SALLA_CLIENT_SECRET in .env
    """
    
    # Get credentials from query params or environment
    client_id = client_id or os.getenv("SALLA_CLIENT_ID")
    client_secret = client_secret or os.getenv("SALLA_CLIENT_SECRET")
    
    if not client_id:
        raise HTTPException(
            status_code=400,
            detail="Missing client_id. Provide via query param or SALLA_CLIENT_ID env variable"
        )
    
    # Store client_secret temporarily (in production, use secure session storage)
    # For now, we'll pass it via state parameter (NOT RECOMMENDED for production)
    
    # Build authorization URL
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': CALLBACK_URL,
        'scope': 'offline_access',  # Required for refresh token
        'state': f"{client_id}:{client_secret}" if client_secret else client_id
    }
    
    auth_url = f"{SALLA_AUTH_URL}?{urlencode(params)}"
    
    # Return HTML page with auto-redirect
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Salla Authorization</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 500px;
            }}
            h1 {{ color: #333; }}
            p {{ color: #666; margin: 20px 0; }}
            .btn {{
                background: #667eea;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
            }}
            .btn:hover {{ background: #5568d3; }}
            .spinner {{
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛍️ Salla Price Optimizer</h1>
            <p>Redirecting you to Salla for authorization...</p>
            <div class="spinner"></div>
            <p><small>If not redirected automatically, click below:</small></p>
            <a href="{auth_url}" class="btn">Authorize App</a>
        </div>
        <script>
            setTimeout(function() {{
                window.location.href = "{auth_url}";
            }}, 2000);
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@app.get("/oauth/callback")
async def oauth_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    error_description: str = None,
    db: Session = Depends(get_db_session)
):
    """
    Step 2: Handle OAuth callback from Salla
    Exchange authorization code for access token and create store record
    """
    
    # Handle OAuth errors
    if error:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Authorization Failed</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #dc3545;">❌ Authorization Failed</h1>
            <p><strong>Error:</strong> {error}</p>
            <p><strong>Description:</strong> {error_description}</p>
            <a href="/oauth/authorize" style="color: #667eea;">Try Again</a>
        </body>
        </html>
        """, status_code=400)
    
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    # Extract client credentials from state
    if ':' in state:
        client_id, client_secret = state.split(':', 1)
    else:
        client_id = state
        client_secret = os.getenv("SALLA_CLIENT_SECRET")
    
    if not client_secret:
        raise HTTPException(status_code=400, detail="Missing client_secret")
    
    try:
        # Step 2a: Exchange code for tokens
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': CALLBACK_URL
        }
        
        token_response = requests.post(SALLA_TOKEN_URL, data=token_data, timeout=30)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        expires_in = tokens.get('expires_in', 1209600)  # Default 14 days
        
        if not access_token:
            raise HTTPException(status_code=500, detail="Failed to obtain access token")
        
        # Step 2b: Get merchant/store information
        user_response = requests.get(
            SALLA_USER_INFO_URL,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=30
        )
        user_response.raise_for_status()
        user_data = user_response.json()
        
        # Extract store details
        merchant = user_data.get('merchant', {})
        store_id = str(merchant.get('id'))
        store_name = merchant.get('name', 'Unknown Store')
        store_domain = merchant.get('domain', '')
        owner_email = user_data.get('email', '')
        owner_name = user_data.get('name', '')
        
        # Step 2c: Check if store already exists
        existing_store = db.query(Store).filter(Store.store_id == store_id).first()
        
        token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        if existing_store:
            # Update existing store
            existing_store.access_token = access_token
            existing_store.refresh_token = refresh_token
            existing_store.token_expires_at = token_expires_at
            existing_store.store_name = store_name
            existing_store.store_domain = store_domain
            existing_store.owner_email = owner_email
            existing_store.owner_name = owner_name
            existing_store.is_active = True
            existing_store.updated_at = datetime.utcnow()
            
            db.commit()
            
            # Log activity
            activity = ActivityLog(
                store_id=store_id,
                activity_type='reauthorization',
                description='Store reauthorized the app',
                metadata={'client_id': client_id}
            )
            db.add(activity)
            db.commit()
            
            action = "reconnected"
        else:
            # Create new store
            new_store = Store(
                store_id=store_id,
                store_name=store_name,
                store_domain=store_domain,
                owner_email=owner_email,
                owner_name=owner_name,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=token_expires_at,
                client_id=client_id,
                client_secret=client_secret,
                is_active=True,
                automation_mode='manual',  # Start with manual mode
                min_profit_margin=10.00,
                update_frequency_hours=12
            )
            
            db.add(new_store)
            db.commit()
            
            # Log activity
            activity = ActivityLog(
                store_id=store_id,
                activity_type='onboarding',
                description='New store onboarded',
                metadata={'client_id': client_id}
            )
            db.add(activity)
            db.commit()
            
            action = "onboarded"
        
        # Success page
        dashboard_url = f"/dashboard?store_id={store_id}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authorization Successful</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 600px;
                }}
                h1 {{ color: #28a745; }}
                .info {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .info p {{ margin: 10px 0; text-align: left; }}
                .btn {{
                    background: #667eea;
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                    margin: 10px;
                }}
                .btn:hover {{ background: #5568d3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 Authorization Successful!</h1>
                <p>Your store has been successfully {action}.</p>
                
                <div class="info">
                    <p><strong>Store:</strong> {store_name}</p>
                    <p><strong>Store ID:</strong> {store_id}</p>
                    <p><strong>Owner:</strong> {owner_name}</p>
                    <p><strong>Email:</strong> {owner_email}</p>
                    <p><strong>Domain:</strong> {store_domain}</p>
                </div>
                
                <p>Your price optimizer is now ready to use!</p>
                
                <a href="{dashboard_url}" class="btn">Go to Dashboard</a>
                <a href="/" class="btn" style="background: #6c757d;">Home</a>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except requests.exceptions.RequestException as e:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>API Error</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #dc3545;">❌ API Error</h1>
            <p>Failed to communicate with Salla API</p>
            <p><strong>Error:</strong> {str(e)}</p>
            <a href="/oauth/authorize" style="color: #667eea;">Try Again</a>
        </body>
        </html>
        """, status_code=500)
    
    except Exception as e:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Unexpected Error</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1 style="color: #dc3545;">❌ Unexpected Error</h1>
            <p>{str(e)}</p>
            <a href="/oauth/authorize" style="color: #667eea;">Try Again</a>
        </body>
        </html>
        """, status_code=500)


@app.get("/stores")
async def list_stores(db: Session = Depends(get_db_session)):
    """List all registered stores (for admin/debugging)"""
    stores = db.query(Store).all()
    return {
        "total": len(stores),
        "stores": [
            {
                "store_id": store.store_id,
                "store_name": store.store_name,
                "is_active": store.is_active,
                "automation_mode": store.automation_mode,
                "last_run": store.last_optimization_run.isoformat() if store.last_optimization_run else None
            }
            for store in stores
        ]
    }


@app.get("/stores/{store_id}")
async def get_store(store_id: str, db: Session = Depends(get_db_session)):
    """Get specific store details"""
    store = db.query(Store).filter(Store.store_id == store_id).first()
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    return {
        "store_id": store.store_id,
        "store_name": store.store_name,
        "store_domain": store.store_domain,
        "owner_name": store.owner_name,
        "owner_email": store.owner_email,
        "is_active": store.is_active,
        "automation_mode": store.automation_mode,
        "min_profit_margin": float(store.min_profit_margin),
        "update_frequency_hours": store.update_frequency_hours,
        "last_optimization_run": store.last_optimization_run.isoformat() if store.last_optimization_run else None,
        "created_at": store.created_at.isoformat(),
        "token_expired": store.is_token_expired()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
