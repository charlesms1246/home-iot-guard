# Email Notification Setup Guide

## Overview

Home IoT Guardian can send email alerts when anomalies are detected. This guide explains how to configure email notifications.

---

## 📧 Gmail Configuration (Recommended)

### Step 1: Create App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security**
3. Enable **2-Step Verification** (if not already enabled)
4. Go to **App passwords** under "Signing in to Google"
5. Create a new app password:
   - Select **Mail** as the app
   - Select **Other** as the device
   - Name it "Home IoT Guardian"
6. Copy the 16-character password (you won't see it again)

### Step 2: Set Environment Variables

**Windows (PowerShell):**
```powershell
# Set for current session
$env:MAIL_USER = "your-email@gmail.com"
$env:MAIL_PASS = "your-16-char-app-password"
$env:ALERT_EMAIL = "recipient@email.com"

# Set permanently (system-wide)
[System.Environment]::SetEnvironmentVariable('MAIL_USER', 'your-email@gmail.com', 'User')
[System.Environment]::SetEnvironmentVariable('MAIL_PASS', 'your-16-char-app-password', 'User')
[System.Environment]::SetEnvironmentVariable('ALERT_EMAIL', 'recipient@email.com', 'User')
```

**Linux/Mac:**
```bash
# Set for current session
export MAIL_USER="your-email@gmail.com"
export MAIL_PASS="your-16-char-app-password"
export ALERT_EMAIL="recipient@email.com"

# Set permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export MAIL_USER="your-email@gmail.com"' >> ~/.bashrc
echo 'export MAIL_PASS="your-16-char-app-password"' >> ~/.bashrc
echo 'export ALERT_EMAIL="recipient@email.com"' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Test Email Configuration

```bash
# Restart your terminal to load environment variables

# Activate virtual environment
.\guardian_env\Scripts\Activate.ps1

# Start the application
python app.py

# Upload a test file with anomalies
# (data/mock_traffic.csv contains malicious traffic)
```

---

## 📬 Email Alert Format

When anomalies are detected, you'll receive an email like this:

```
Subject: Alert: Anomalies Detected!

Home IoT Guardian - Anomaly Detection Alert

SUMMARY:
--------
Total Samples Analyzed: 991
Anomalies Detected: 9
Anomaly Rate: 0.91%

TOP ANOMALIES:
--------------

Anomaly #1:
  - Sequence ID: 9
  - Error Score: 0.222107
  - Severity: High
  - Rows: 9-19

Anomaly #2:
  - Sequence ID: 14
  - Error Score: 0.270114
  - Severity: High
  - Rows: 14-24

...

ACTION REQUIRED:
----------------
Please review the detected anomalies in the Home IoT Guardian dashboard.

Dashboard: http://localhost:5000

---
This is an automated alert from Home IoT Guardian.
```

---

## 🎯 Testing Without Email

If you don't want to configure email for testing, the application will work fine without it:

1. **Skip email setup** - Don't set environment variables
2. **Console alerts** - Alerts will be printed to console instead
3. **Web alerts** - You'll still see alerts in the browser

**Console output when email is not configured:**
```
[WARNING] Email not configured. Skipping email alert.
[ALERT] 9 anomalies detected in 991 samples!
```

---

## 🔒 Security Best Practices

### Do NOT:
- ❌ Hardcode credentials in code
- ❌ Commit credentials to Git
- ❌ Share your app password
- ❌ Use your regular Gmail password

### Do:
- ✅ Use environment variables
- ✅ Use Gmail app passwords
- ✅ Add `.env` to `.gitignore`
- ✅ Rotate passwords regularly

---

## 🐛 Troubleshooting

### Issue: "SMTP Authentication Error"

**Cause**: Wrong credentials or app password not created

**Solution**:
1. Verify your email and app password
2. Make sure you're using the app password, not your regular password
3. Check that 2-Step Verification is enabled
4. Regenerate app password if needed

### Issue: "Connection Refused"

**Cause**: Firewall or network blocking SMTP

**Solution**:
1. Check firewall settings
2. Try port 587 with STARTTLS:
   ```python
   app.config['MAIL_PORT'] = 587
   app.config['MAIL_USE_TLS'] = True
   app.config['MAIL_USE_SSL'] = False
   ```

### Issue: "Email Not Received"

**Cause**: Email in spam or wrong recipient

**Solution**:
1. Check spam/junk folder
2. Verify ALERT_EMAIL is set correctly
3. Check Gmail "Sent" folder
4. Review application logs

### Issue: "Environment Variables Not Found"

**Cause**: Variables not set or terminal not restarted

**Solution**:
1. Restart terminal/PowerShell
2. Verify variables are set:
   ```powershell
   echo $env:MAIL_USER
   echo $env:MAIL_PASS
   ```
3. Re-run the set commands

---

## 📱 In-App Alerts

### Browser Notifications

The web interface shows alerts in two ways:

1. **Alert Banner** (top of page)
   - Green: No anomalies
   - Yellow: Anomalies detected
   - Red: Error

2. **Bootstrap Toast** (top-right corner)
   - Auto-dismisses after 5 seconds
   - Shows anomaly count
   - Links to dashboard

**Example JavaScript:**
```javascript
// Warning toast for anomalies
showToast(
    'Anomalies Detected!',
    'Found 9 potential threats. Check your email for details.',
    'warning'
);
```

---

## 🔧 Customization

### Change Email Server

For other email providers, modify `app.py`:

**Outlook/Office 365:**
```python
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
```

**SendGrid:**
```python
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = 'your-sendgrid-api-key'
```

### Change Alert Threshold

Modify when alerts are sent:

```python
# In detect_anomalies function
if len(anomaly_indices) > 5:  # Only alert if >5 anomalies
    send_email_alert(...)
```

### Customize Email Template

Edit the `send_email_alert` function in `app.py`:

```python
msg.body = f"""
Your custom email template here...

Anomalies: {anomalies_count}
Total: {total_samples}
"""
```

---

## 📊 Testing Checklist

- [ ] Environment variables set correctly
- [ ] Gmail app password created
- [ ] Application restarted with new variables
- [ ] Upload test file (mock_traffic.csv)
- [ ] Check console for "[EMAIL] Alert sent" message
- [ ] Check recipient inbox (and spam folder)
- [ ] Verify web toast notification appears
- [ ] Test without email config (console fallback)

---

## 🎓 Additional Resources

- **Gmail App Passwords**: https://support.google.com/accounts/answer/185833
- **Flask-Mail Documentation**: https://pythonhosted.org/Flask-Mail/
- **SMTP Troubleshooting**: https://support.google.com/mail/answer/7126229

---

## ✅ Quick Setup Summary

1. **Create Gmail app password**
2. **Set environment variables**:
   - `MAIL_USER` - Your Gmail address
   - `MAIL_PASS` - 16-char app password
   - `ALERT_EMAIL` - Recipient email
3. **Restart application**
4. **Upload test file**
5. **Check email and browser alerts**

---

**Status**: Email notifications ready for production use! 📧

