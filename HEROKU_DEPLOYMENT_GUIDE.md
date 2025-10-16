# Home IoT Guardian - Heroku Deployment Guide

**Complete guide for deploying Home IoT Guardian to Heroku**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Heroku Setup](#heroku-setup)
4. [Configuration](#configuration)
5. [Deployment](#deployment)
6. [Testing](#testing)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts

- **Heroku Account**: Sign up at https://signup.heroku.com/
- **Git Account**: For version control
- **Gmail Account**: For email notifications (with 2FA enabled)

### Local Requirements

- Git installed
- Python 3.10+
- Heroku CLI
- Project files ready

---

## Installation

### Step 1: Install Heroku CLI

#### Windows

**Option A: Download Installer**
1. Visit: https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli
2. Download the Windows installer (64-bit)
3. Run the installer
4. Follow the installation wizard

**Option B: Using Chocolatey**
```powershell
choco install heroku-cli
```

**Option C: Using Scoop**
```powershell
scoop install heroku-cli
```

#### macOS

**Using Homebrew**:
```bash
brew tap heroku/brew && brew install heroku
```

#### Linux (Ubuntu/Debian)

```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

### Step 2: Verify Installation

```bash
heroku --version
# Expected output: heroku/8.x.x win32-x64 node-v16.x.x
```

### Step 3: Login to Heroku

```bash
heroku login
# This will open a browser for authentication
# Click "Log in" button
```

**Alternative (CLI only)**:
```bash
heroku login -i
# Enter your email and password
```

---

## Heroku Setup

### Step 1: Initialize Git Repository

```bash
# Navigate to project directory
cd D:\Projects\home-iot-guard

# Initialize Git (if not already done)
git init

# Add all files
git add .

# Check status
git status
```

### Step 2: Create .gitignore

Ensure `.gitignore` includes:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual Environment
guardian_env/
venv/
env/

# Database
*.db
instance/

# Model files (optional - if too large)
# models/*.keras
# models/*.h5

# Environment variables
.env

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

### Step 3: Create Heroku App

```bash
# Create new app
heroku create home-iot-guardian

# Output:
# Creating ⬢ home-iot-guardian... done
# https://home-iot-guardian.herokuapp.com/ | https://git.heroku.com/home-iot-guardian.git
```

**Note**: If name is taken, use a different name:
```bash
heroku create home-iot-guardian-{your-username}
# or let Heroku generate a random name:
heroku create
```

### Step 4: Verify Remote

```bash
# Check Git remotes
git remote -v

# Expected output:
# heroku  https://git.heroku.com/home-iot-guardian.git (fetch)
# heroku  https://git.heroku.com/home-iot-guardian.git (push)
```

---

## Configuration

### Step 1: Set Buildpack

```bash
# Add Python buildpack
heroku buildpacks:set heroku/python

# Verify
heroku buildpacks
# === home-iot-guardian Buildpack URL
# heroku/python
```

### Step 2: Configure Environment Variables

#### Gmail App Password Setup

1. **Enable 2-Factor Authentication**:
   - Go to https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. **Generate App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "App": Mail
   - Select "Device": Other (Custom name)
   - Enter: "Home IoT Guardian"
   - Click "Generate"
   - Copy the 16-character password

#### Set Config Variables

```bash
# Email configuration
heroku config:set MAIL_USER=your_email@gmail.com
heroku config:set MAIL_PASS=your_16_char_app_password
heroku config:set ALERT_EMAIL=recipient@email.com

# Flask configuration
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=0

# Verify configuration
heroku config

# Expected output:
# === home-iot-guardian Config Vars
# ALERT_EMAIL:  recipient@email.com
# FLASK_DEBUG:  0
# FLASK_ENV:    production
# MAIL_PASS:    abcdefghijklmnop
# MAIL_USER:    your_email@gmail.com
```

### Step 3: Verify Required Files

Ensure these files exist in your project:

#### Procfile

```
web: gunicorn app:app
```

#### runtime.txt

```
python-3.10.0
```

**Note**: Use a specific Python version supported by Heroku. Check available versions:
https://devcenter.heroku.com/articles/python-support#supported-runtimes

Update if needed:
```
python-3.10.13
# or
python-3.11.7
```

#### requirements.txt

Verify `gunicorn` is included:
```bash
# Check if gunicorn is in requirements
grep gunicorn requirements.txt

# If not found, add it:
echo "gunicorn==23.0.0" >> requirements.txt
```

---

## Deployment

### Step 1: Commit All Changes

```bash
# Add all changes
git add .

# Commit
git commit -m "Prepare for Heroku deployment"

# Check status
git status
# Expected: nothing to commit, working tree clean
```

### Step 2: Deploy to Heroku

```bash
# Push to Heroku
git push heroku main

# If your branch is 'master', use:
# git push heroku master

# If you get a branch error:
# git push heroku HEAD:main
```

**Deployment Output** (expected):

```
Enumerating objects: 45, done.
Counting objects: 100% (45/45), done.
Delta compression using up to 8 threads
Compressing objects: 100% (38/38), done.
Writing objects: 100% (45/45), 150.23 KiB | 7.51 MiB/s, done.
Total 45 (delta 15), reused 0 (delta 0), pack-reused 0

-----> Building on the Heroku-22 stack
-----> Using buildpack: heroku/python
-----> Python app detected
-----> Using Python version specified in runtime.txt
-----> Installing python-3.10.13
-----> Installing pip 23.x, setuptools 69.x and wheel 0.42.x
-----> Installing SQLite3
-----> Installing requirements with pip
       Collecting absl-py==2.3.1
       Collecting Flask==3.1.2
       Collecting tensorflow==2.20.0
       ...
       Successfully installed [all packages]
-----> Discovering process types
       Procfile declares types -> web
-----> Compressing...
       Done: 234.5M
-----> Launching...
       Released v3
       https://home-iot-guardian.herokuapp.com/ deployed to Heroku
```

### Step 3: Scale Dynos

```bash
# Ensure at least one web dyno is running
heroku ps:scale web=1

# Check dyno status
heroku ps

# Expected output:
# === web (Free): gunicorn app:app (1)
# web.1: up 2025/10/16 10:30:00 +0000 (~ 1m ago)
```

### Step 4: Initialize Database on Heroku

```bash
# Run database initialization
heroku run python init_db.py

# Expected output:
# Running python init_db.py on ⬢ home-iot-guardian... up, run.1234 (Free)
# Database initialized successfully!
# Tables created: scan_result
```

---

## Testing

### Step 1: Open Application

```bash
# Open app in browser
heroku open

# This opens: https://home-iot-guardian.herokuapp.com/
```

### Step 2: Test Basic Functionality

1. **Check Dashboard**:
   - Verify page loads correctly
   - Check Bootstrap styling
   - Verify all sections visible

2. **Test Status Endpoint**:
   ```bash
   curl https://home-iot-guardian.herokuapp.com/status
   ```

   Expected response:
   ```json
   {
     "status": "operational",
     "model_loaded": true,
     "threshold": 0.140134,
     "database": "connected",
     "total_scans": 0
   }
   ```

### Step 3: Test File Upload

#### Using Browser

1. Navigate to https://home-iot-guardian.herokuapp.com/
2. Click "Choose File"
3. Select `mock_traffic.csv`
4. Click "Upload & Scan"
5. Verify results display
6. Check for anomalies

#### Using cURL

```bash
# Download sample file first (if not local)
curl -O https://raw.githubusercontent.com/yourusername/home-iot-guard/main/data/mock_traffic.csv

# Upload to Heroku
curl -F "file=@mock_traffic.csv" https://home-iot-guardian.herokuapp.com/upload
```

Expected response:
```json
{
  "scan_id": 1,
  "anomalies_count": 9,
  "total_samples": 991,
  "percentage": 0.91,
  "threshold": 0.140134,
  "details": [...]
}
```

### Step 4: Test History

```bash
curl https://home-iot-guardian.herokuapp.com/history
```

### Step 5: Test Email Alerts

1. Upload file with anomalies
2. Check recipient email
3. Verify alert received
4. Check logs: `heroku logs --tail`

---

## Monitoring

### View Logs

```bash
# View real-time logs
heroku logs --tail

# View recent logs
heroku logs -n 200

# View logs for specific dyno
heroku logs --dyno web.1

# Search logs
heroku logs --tail | grep ERROR
```

### Common Log Messages

**Successful Startup**:
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:5000
[INFO] Using worker: sync
[INFO] Booting worker with pid: 4
Model loaded successfully!
Threshold: 0.140134
```

**File Upload**:
```
[INFO] File uploaded: temp_file.csv
[INFO] Processing 1001 rows...
[INFO] Created 991 sequences
[INFO] Detected 9 anomalies
[EMAIL] Alert sent to recipient@email.com
```

**Errors**:
```
[ERROR] Failed to load model: [error details]
[ERROR] Database error: [error details]
[ERROR] SMTP error: [error details]
```

### Check App Metrics

```bash
# View app info
heroku apps:info

# Check dyno usage
heroku ps

# View database info (if using Postgres)
heroku addons

# Check app size
heroku repo:purge_cache
```

### Performance Monitoring

```bash
# Open Heroku dashboard
heroku dashboard

# View metrics in browser
# Navigate to: https://dashboard.heroku.com/apps/home-iot-guardian/metrics
```

---

## Troubleshooting

### Issue 1: Application Error (H10)

**Error**:
```
Error H10 (App crashed)
```

**Solutions**:

1. Check logs:
   ```bash
   heroku logs --tail
   ```

2. Verify Procfile:
   ```bash
   cat Procfile
   # Should be: web: gunicorn app:app
   ```

3. Check if gunicorn is installed:
   ```bash
   grep gunicorn requirements.txt
   ```

4. Restart dyno:
   ```bash
   heroku restart
   ```

### Issue 2: Module Not Found

**Error**:
```
ModuleNotFoundError: No module named 'tensorflow'
```

**Solutions**:

1. Verify requirements.txt is complete
2. Rebuild app:
   ```bash
   heroku repo:purge_cache
   git commit --allow-empty -m "Rebuild"
   git push heroku main
   ```

### Issue 3: Model File Not Found

**Error**:
```
FileNotFoundError: models/lstm_model.keras
```

**Solutions**:

1. Ensure model file is committed:
   ```bash
   git add models/lstm_model.keras models/threshold.txt
   git commit -m "Add model files"
   git push heroku main
   ```

2. Or retrain model on Heroku:
   ```bash
   heroku run python models/train_model.py
   ```

### Issue 4: Slug Size Too Large

**Error**:
```
Compiled slug size: 550M exceeds limit (500M)
```

**Solutions**:

1. Remove unnecessary files from Git
2. Use `.slugignore`:
   ```bash
   # Create .slugignore
   echo "*.md" > .slugignore
   echo "tests/" >> .slugignore
   echo "docs/" >> .slugignore
   ```

3. Optimize dependencies:
   - Remove unused packages
   - Use lighter alternatives

### Issue 5: Database Not Initialized

**Error**:
```
sqlite3.OperationalError: no such table: scan_result
```

**Solution**:
```bash
heroku run python init_db.py
```

### Issue 6: Email Not Sending

**Error**:
```
SMTPAuthenticationError: Username and Password not accepted
```

**Solutions**:

1. Verify config vars:
   ```bash
   heroku config:get MAIL_USER
   heroku config:get MAIL_PASS
   ```

2. Use App Password (not regular password)

3. Test email configuration:
   ```bash
   heroku run python -c "import os; print(os.environ.get('MAIL_USER'))"
   ```

### Issue 7: Timeout Errors

**Error**:
```
H12 - Request timeout
```

**Solutions**:

1. Increase timeout (not recommended for Heroku free tier)
2. Optimize processing:
   - Reduce batch size
   - Process data in chunks

3. Use worker dyno for long tasks

### Issue 8: Memory Exceeded

**Error**:
```
R14 - Memory quota exceeded
R15 - Memory quota vastly exceeded
```

**Solutions**:

1. Upgrade dyno type:
   ```bash
   heroku dyno:type hobby
   ```

2. Optimize memory usage:
   - Reduce model size
   - Process smaller batches
   - Clear variables after use

---

## Updating the App

### Deploy Updates

```bash
# Make changes to code
# ...

# Commit changes
git add .
git commit -m "Update: [description]"

# Deploy
git push heroku main

# Verify deployment
heroku logs --tail
```

### Rollback Deployment

```bash
# View releases
heroku releases

# Rollback to previous version
heroku rollback v2

# Or specify version
heroku releases:rollback v1
```

### Update Config Variables

```bash
# Update variable
heroku config:set MAIL_USER=new_email@gmail.com

# Remove variable
heroku config:unset OLD_VAR

# View all variables
heroku config
```

---

## Heroku Add-ons (Optional)

### PostgreSQL Database

For production, consider PostgreSQL instead of SQLite:

```bash
# Add Postgres
heroku addons:create heroku-postgresql:mini

# Get database URL
heroku config:get DATABASE_URL

# Update app.py to use Postgres
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
```

### Papertrail (Logging)

```bash
# Add Papertrail for better logging
heroku addons:create papertrail:choklad

# Open logs
heroku addons:open papertrail
```

### New Relic (Monitoring)

```bash
# Add New Relic for performance monitoring
heroku addons:create newrelic:wayne

# Configure
heroku config:set NEW_RELIC_APP_NAME="Home IoT Guardian"
```

---

## Best Practices

### Security

1. **Never commit sensitive data**:
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Use strong passwords**:
   - Gmail App Passwords
   - Heroku account

3. **Enable 2FA**:
   - Heroku account
   - Gmail account

### Performance

1. **Use CDN for static files**
2. **Enable compression**
3. **Cache responses**
4. **Optimize database queries**

### Monitoring

1. **Set up logging**
2. **Monitor dyno metrics**
3. **Set up alerts**
4. **Regular backups**

---

## Cost Considerations

### Heroku Pricing (as of 2025)

- **Free Tier**: Discontinued (check current pricing)
- **Hobby**: $7/month per dyno
- **Standard**: $25-50/month per dyno
- **Performance**: $250+/month per dyno

### Optimization Tips

1. Use eco dynos for development
2. Scale down when not in use
3. Optimize slug size
4. Use caching

---

## Useful Commands

### App Management

```bash
# App info
heroku apps:info

# Rename app
heroku apps:rename new-name

# Delete app
heroku apps:destroy --app home-iot-guardian

# Transfer app
heroku apps:transfer new-owner@email.com
```

### Dyno Management

```bash
# Scale dynos
heroku ps:scale web=1

# Restart dynos
heroku restart

# Stop dynos
heroku ps:stop web.1

# Type info
heroku ps:type
```

### Database Management

```bash
# Database console
heroku run python

# Run migrations
heroku run python init_db.py

# Backup database
heroku pg:backups:capture

# Download backup
heroku pg:backups:download
```

---

## Quick Reference

### Essential Commands

| Command | Description |
|---------|-------------|
| `heroku login` | Login to Heroku |
| `heroku create` | Create new app |
| `heroku config:set VAR=value` | Set config variable |
| `git push heroku main` | Deploy app |
| `heroku logs --tail` | View logs |
| `heroku open` | Open app in browser |
| `heroku restart` | Restart dynos |
| `heroku ps` | Check dyno status |

### URLs

- **Dashboard**: https://dashboard.heroku.com/
- **CLI Docs**: https://devcenter.heroku.com/articles/heroku-cli
- **Python Docs**: https://devcenter.heroku.com/articles/getting-started-with-python
- **App URL**: https://home-iot-guardian.herokuapp.com/

---

## Deployment Checklist

- [ ] Heroku CLI installed
- [ ] Heroku account created
- [ ] Git repository initialized
- [ ] All files committed
- [ ] Procfile created
- [ ] runtime.txt created
- [ ] requirements.txt includes gunicorn
- [ ] .gitignore configured
- [ ] Heroku app created
- [ ] Buildpack set (heroku/python)
- [ ] Config vars set (MAIL_USER, MAIL_PASS, ALERT_EMAIL)
- [ ] Code pushed to Heroku
- [ ] Database initialized
- [ ] App tested in browser
- [ ] File upload tested
- [ ] Email alerts tested
- [ ] Logs monitored

---

## Support

If you encounter issues:

1. Check logs: `heroku logs --tail`
2. Search Heroku DevCenter: https://devcenter.heroku.com/
3. Check Heroku Status: https://status.heroku.com/
4. Contact Heroku Support: https://help.heroku.com/

---

## Conclusion

Your Home IoT Guardian application is now deployed on Heroku! 🚀

**App URL**: https://home-iot-guardian.herokuapp.com/

**Next Steps**:
1. Monitor logs regularly
2. Set up alerts
3. Consider upgrading dyno for production
4. Add custom domain (optional)
5. Set up CI/CD pipeline

---

**Last Updated**: October 16, 2025  
**Heroku Stack**: heroku-22  
**Python Version**: 3.10.13  
**Status**: Production Ready ✅

---

⭐ **Your app is live on Heroku!**

