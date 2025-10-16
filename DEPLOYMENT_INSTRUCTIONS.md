# Quick Heroku Deployment Instructions

**Choose your method based on your preference:**

---

## Method 1: Automated Deployment (Recommended)

### For Windows (PowerShell):
```powershell
# Run deployment script
.\deploy.ps1
```

### For Linux/macOS (Bash):
```bash
# Make script executable
chmod +x deploy.sh

# Run deployment script
./deploy.sh
```

The script will:
1. ✓ Check if Heroku CLI is installed
2. ✓ Login to Heroku (if needed)
3. ✓ Create/verify Heroku app
4. ✓ Set buildpack
5. ✓ Configure environment variables (will prompt you)
6. ✓ Commit changes to Git
7. ✓ Deploy to Heroku
8. ✓ Scale dynos
9. ✓ Initialize database
10. ✓ Open app in browser

---

## Method 2: Manual Deployment (Step-by-Step)

### Prerequisites

1. **Install Heroku CLI**:
   - Windows: https://cli-assets.heroku.com/heroku-x64.exe
   - macOS: `brew tap heroku/brew && brew install heroku`
   - Linux: `curl https://cli-assets.heroku.com/install.sh | sh`

2. **Verify installation**:
   ```bash
   heroku --version
   ```

### Step 1: Login to Heroku

```bash
heroku login
# Browser will open for authentication
```

### Step 2: Create Heroku App

```bash
# Create app with your desired name
heroku create home-iot-guardian

# Or use a different name if taken:
heroku create home-iot-guardian-yourname

# Or let Heroku generate a name:
heroku create
```

### Step 3: Set Buildpack

```bash
heroku buildpacks:set heroku/python
```

### Step 4: Configure Environment Variables

**Important**: Use Gmail App Password (not regular password)

1. Enable 2FA: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Set config vars:

```bash
heroku config:set MAIL_USER=your_email@gmail.com
heroku config:set MAIL_PASS=your_16_char_app_password
heroku config:set ALERT_EMAIL=recipient@email.com
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=0
```

### Step 5: Commit All Files

```bash
# Add all files
git add .

# Commit
git commit -m "Prepare for Heroku deployment"
```

### Step 6: Deploy to Heroku

```bash
# Push to Heroku
git push heroku main

# If your branch is 'master':
# git push heroku master
```

**Wait for deployment** (3-5 minutes):
- Heroku will install all dependencies
- Build the application
- Start the web dyno

### Step 7: Scale Dynos

```bash
heroku ps:scale web=1
```

### Step 8: Initialize Database

```bash
heroku run python init_db.py
```

### Step 9: Open Application

```bash
heroku open
```

---

## Testing Your Deployment

### 1. Check Status

```bash
# Check dyno status
heroku ps

# View logs
heroku logs --tail
```

### 2. Test Status Endpoint

```bash
curl https://your-app-name.herokuapp.com/status
```

Expected response:
```json
{
  "status": "operational",
  "model_loaded": true,
  "threshold": 0.140134
}
```

### 3. Test File Upload

**Using Browser**:
1. Navigate to your app URL
2. Upload `mock_traffic.csv` from `data/` folder
3. Verify results display

**Using cURL**:
```bash
curl -F "file=@data/mock_traffic.csv" https://your-app-name.herokuapp.com/upload
```

### 4. Check Email Alert

If anomalies are detected, check recipient email for alert.

---

## Monitoring

### View Real-time Logs

```bash
heroku logs --tail
```

### Check App Info

```bash
heroku apps:info
```

### View Config Variables

```bash
heroku config
```

---

## Common Issues & Solutions

### Issue: Heroku CLI not found

**Solution**: Install Heroku CLI
- Windows: Download from https://cli-assets.heroku.com/heroku-x64.exe
- After installation, restart terminal/PowerShell

### Issue: App name already taken

**Solution**: Choose a different name
```bash
heroku create home-iot-guardian-yourname
```

### Issue: Authentication failed

**Solution**: Login again
```bash
heroku login
```

### Issue: Deployment failed

**Solution**: Check logs
```bash
heroku logs --tail
```

Common causes:
- Missing `gunicorn` in requirements.txt (✓ Already included)
- Wrong Python version in runtime.txt (✓ Updated to 3.11.7)
- Missing Procfile (✓ Already present)

### Issue: Model not found

**Solution**: Ensure model files are committed
```bash
git add models/lstm_model.keras models/threshold.txt
git commit -m "Add model files"
git push heroku main
```

### Issue: Database table doesn't exist

**Solution**: Initialize database
```bash
heroku run python init_db.py
```

### Issue: Email not sending

**Solution**: Verify config vars
```bash
heroku config:get MAIL_USER
heroku config:get MAIL_PASS
```

Make sure you're using Gmail App Password, not regular password.

---

## Updating Your App

```bash
# Make changes to code
# ...

# Commit changes
git add .
git commit -m "Update: description of changes"

# Deploy update
git push heroku main

# Restart if needed
heroku restart
```

---

## Useful Commands

| Command | Description |
|---------|-------------|
| `heroku apps:info` | View app details |
| `heroku ps` | Check dyno status |
| `heroku logs --tail` | View real-time logs |
| `heroku restart` | Restart app |
| `heroku open` | Open app in browser |
| `heroku config` | View config variables |
| `heroku run bash` | SSH into dyno |

---

## Getting Help

- **Heroku DevCenter**: https://devcenter.heroku.com/
- **Heroku Status**: https://status.heroku.com/
- **Full Guide**: See HEROKU_DEPLOYMENT_GUIDE.md

---

## Deployment Checklist

- [ ] Heroku CLI installed
- [ ] Logged in to Heroku
- [ ] App created
- [ ] Buildpack set
- [ ] Config vars configured (MAIL_USER, MAIL_PASS, ALERT_EMAIL)
- [ ] All files committed to Git
- [ ] Pushed to Heroku
- [ ] Dynos scaled
- [ ] Database initialized
- [ ] App tested in browser
- [ ] Email alerts tested

---

**Your app URL**: https://home-iot-guardian.herokuapp.com/

**Time to deploy**: ~10-15 minutes (manual) or ~5 minutes (automated script)

---

✅ **Ready to deploy!** Choose Method 1 (automated) or Method 2 (manual) above.

