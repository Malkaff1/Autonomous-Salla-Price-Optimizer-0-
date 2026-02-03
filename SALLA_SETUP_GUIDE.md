# 🚀 Salla API Setup Guide

## Step 1: Create Salla Partner Account

1. **Visit**: [https://salla.dev](https://salla.dev)
2. **Click**: "Sign Up" or "Register"
3. **Fill in your details**:
   - Full Name
   - Email Address
   - Phone Number
   - Password
4. **Verify your email** (check inbox/spam)
5. **Login** to your account

## Step 2: Create Your Application

1. **Go to Dashboard**: After login, you'll see the partner dashboard
2. **Click**: "My Apps" or "Applications" in the sidebar
3. **Click**: "Create New App" or "Add New Application"
4. **Fill App Details**:
   ```
   App Name: Price Optimizer
   App Description: Autonomous pricing system for Salla stores
   App Type: Private App (for your own store)
   Category: Business Tools
   ```

## Step 3: Configure App Permissions

**CRITICAL**: Make sure to enable these permissions:
- ✅ `products:read` - Read product information
- ✅ `products:write` - Update product prices  
- ✅ `store:read` - Read store information

## Step 4: Set OAuth Configuration

1. **Redirect URLs**: Add this URL:
   ```
   http://localhost:8000/callback
   ```
2. **Save the configuration**

## Step 5: Get Your Credentials

After creating the app, you'll see:
```
Client ID: abc123def456ghi789
Client Secret: xyz987uvw654rst321
```

**⚠️ IMPORTANT**: 
- Keep Client Secret private!
- Don't share it publicly
- Don't commit it to GitHub

## Step 6: Install App on Your Store

1. **Go to your Salla store admin panel**
2. **Navigate to**: Apps → App Store
3. **Find your app** (it might be in "My Apps" section)
4. **Click**: "Install" or "Add to Store"
5. **Grant permissions** when prompted

## Step 7: Run OAuth Setup Script

```bash
python salla_oauth_setup.py
```

Enter your Client ID and Client Secret when prompted.

## Troubleshooting

### Problem: Can't find "My Apps" section
**Solution**: Make sure you're logged into the **Partner Dashboard**, not the regular Salla store admin.

### Problem: App not showing permissions options
**Solution**: Check that you selected "Private App" type during creation.

### Problem: Redirect URL error
**Solution**: Make sure the redirect URL is exactly: `http://localhost:8000/callback`

### Problem: Client Secret not visible
**Solution**: You might need to click "Show" or "Reveal" button next to the secret.

## Next Steps After Setup

1. **Test API Connection**:
   ```bash
   python test_salla_api.py
   ```

2. **Run Price Optimizer**:
   ```bash
   python run_optimizer.py
   ```

3. **Monitor Logs**: Check the output for any errors

## Support Resources

- **Official Docs**: [https://docs.salla.dev](https://docs.salla.dev)
- **API Reference**: [https://docs.salla.dev/api](https://docs.salla.dev/api)
- **GitHub Examples**: [https://github.com/SallaApp](https://github.com/SallaApp)

---

**Need Help?** If you get stuck at any step, let me know which step you're on and what error you're seeing.