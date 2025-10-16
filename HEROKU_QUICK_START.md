# Heroku Deployment - Quick Start 🚀

**Deploy Home IoT Guardian to Heroku in 5 minutes!**

---

## Option 1: Automated (Easiest) ⚡

### Windows:
```powershell
.\deploy.ps1
```

### Linux/macOS:
```bash
chmod +x deploy.sh && ./deploy.sh
```

**Done!** The script handles everything automatically.

---

## Option 2: Manual (10 Commands) 📝

### 1. Install Heroku CLI

**Windows**: Download from https://cli-assets.heroku.com/heroku-x64.exe

**macOS**: `brew install heroku/brew/heroku`

**Linux**: `curl https://cli-assets.heroku.com/install.sh | sh`

### 2. Deploy

```bash
# Login
heroku login

# Create app
heroku create home-iot-guardian

# Set buildpack
heroku buildpacks:set heroku/python

# Configure email (replace with your values)
heroku config:set MAIL_USER=your_email@gmail.com
heroku config:set MAIL_PASS=your_app_password
heroku config:set ALERT_EMAIL=recipient@email.com

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Initialize database
heroku run python init_db.py

# Open app
heroku open
```

---

## Gmail App Password Setup

1. Enable 2FA: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Copy the 16-character password
4. Use it as `MAIL_PASS`

---

## Test Your Deployment

```bash
# Check status
heroku ps

# View logs
heroku logs --tail

# Test upload (in browser)
# Navigate to: https://your-app.herokuapp.com/
# Upload: data/mock_traffic.csv
```

---

## Common Issues

**Heroku CLI not found?**
→ Install from link above, restart terminal

**App name taken?**
→ Use: `heroku create home-iot-guardian-yourname`

**Email not working?**
→ Use Gmail App Password, not regular password

**Deployment failed?**
→ Check: `heroku logs --tail`

---

## Useful Commands

```bash
heroku logs --tail          # View logs
heroku restart              # Restart app
heroku ps                   # Check status
heroku config               # View variables
heroku open                 # Open in browser
```

---

## Files Included ✅

- `Procfile` - Heroku process configuration
- `runtime.txt` - Python version (3.11.7)
- `requirements.txt` - Dependencies (includes gunicorn)
- `.slugignore` - Exclude unnecessary files
- `deploy.sh` - Automated deployment (Linux/macOS)
- `deploy.ps1` - Automated deployment (Windows)

---

## Time to Deploy

- **Automated**: ~5 minutes
- **Manual**: ~10 minutes
- **First-time setup**: +5 minutes (Heroku CLI install)

---

## Cost

- **Free Tier**: Check Heroku pricing (may have changed)
- **Hobby Tier**: $7/month (recommended for production)

---

## Need More Help?

- **Full Guide**: See `HEROKU_DEPLOYMENT_GUIDE.md` (40+ pages)
- **Step-by-Step**: See `DEPLOYMENT_INSTRUCTIONS.md`
- **Heroku Docs**: https://devcenter.heroku.com/

---

**Ready to deploy?** Use automated script or follow manual steps above! 🎉

---

**App will be live at**: https://home-iot-guardian.herokuapp.com/

