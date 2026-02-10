# 🚀 Create New Salla App with Correct Permissions

## Step 1: Go to Salla Partner Dashboard
1. Visit: https://salla.dev
2. Login to your account
3. Click "My Apps" or "Applications"

## Step 2: Create New App
1. Click "Create New App" or "Add Application"
2. Fill in the details:

### Basic Information:
- **App Name**: `Price Optimizer`
- **App Description**: `Autonomous pricing system for Salla stores`
- **App Type**: `Private App` (for your own store)
- **Category**: `Business Tools` or `Productivity`

### OAuth Configuration:
- **Redirect URLs**: `http://localhost:8000/callback`
- **Webhook URLs**: (leave empty for now)

### Permissions (CRITICAL):
Make sure to enable these scopes:
- ✅ `products:read` - Read product information
- ✅ `products:write` - Update product prices  
- ✅ `store:read` - Read store information

## Step 3: Save and Get Credentials
1. Click "Save" or "Create App"
2. Copy your new credentials:
   - **Client ID**: (new one will be generated)
   - **Client Secret**: (new one will be generated)

## Step 4: Install App on Your Store
1. Go to your Salla store admin panel
2. Navigate to Apps → App Store
3. Find your app (might be in "My Apps" section)
4. Click "Install" or "Add to Store"
5. Grant the requested permissions

## Step 5: Test with New Credentials
Run the auth script again with your new Client ID and Client Secret.