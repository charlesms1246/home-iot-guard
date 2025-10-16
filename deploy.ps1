# Home IoT Guardian - Heroku Deployment Script (Windows PowerShell)

# Colors
$Green = [System.ConsoleColor]::Green
$Red = [System.ConsoleColor]::Red
$Yellow = [System.ConsoleColor]::Yellow
$White = [System.ConsoleColor]::White

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Check-Success {
    param($message)
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput $Green "✓ $message"
    } else {
        Write-ColorOutput $Red "✗ $message failed"
        exit 1
    }
}

Write-Host "======================================"
Write-Host "Home IoT Guardian - Heroku Deployment"
Write-Host "======================================"
Write-Host ""

# Step 1: Check Heroku CLI
Write-Host "Step 1: Checking Heroku CLI..."
try {
    $herokuVersion = heroku --version 2>&1
    if ($herokuVersion -match "heroku") {
        Write-ColorOutput $Green "✓ Heroku CLI installed: $herokuVersion"
    } else {
        throw "Heroku CLI not found"
    }
} catch {
    Write-ColorOutput $Red "✗ Heroku CLI not found!"
    Write-Host "Install from: https://devcenter.heroku.com/articles/heroku-cli"
    Write-Host "Download: https://cli-assets.heroku.com/heroku-x64.exe"
    Write-Host ""
    Write-Host "After installation, restart PowerShell and run this script again."
    exit 1
}
Write-Host ""

# Step 2: Check Heroku Login
Write-Host "Step 2: Checking Heroku authentication..."
try {
    $user = heroku auth:whoami 2>&1
    if ($user -match "@") {
        Write-ColorOutput $Green "✓ Logged in as: $user"
    } else {
        Write-ColorOutput $Yellow "! Not logged in. Opening login..."
        heroku login
        Check-Success "Heroku login"
    }
} catch {
    Write-ColorOutput $Yellow "! Not logged in. Opening login..."
    heroku login
    Check-Success "Heroku login"
}
Write-Host ""

# Step 3: Check/Create Heroku App
Write-Host "Step 3: Setting up Heroku app..."
$appName = Read-Host "Enter Heroku app name (or press Enter for 'home-iot-guardian')"
if ([string]::IsNullOrWhiteSpace($appName)) {
    $appName = "home-iot-guardian"
}

try {
    $appInfo = heroku apps:info --app $appName 2>&1
    if ($appInfo -match "===") {
        Write-ColorOutput $Green "✓ App '$appName' already exists"
    } else {
        throw "App doesn't exist"
    }
} catch {
    Write-Host "Creating new app '$appName'..."
    heroku create $appName
    Check-Success "App creation"
}
Write-Host ""

# Step 4: Set Buildpack
Write-Host "Step 4: Setting buildpack..."
heroku buildpacks:set heroku/python --app $appName
Check-Success "Buildpack set"
Write-Host ""

# Step 5: Configure Environment Variables
Write-Host "Step 5: Configuring environment variables..."
Write-ColorOutput $Yellow "Please enter your configuration:"

$mailUser = Read-Host "Gmail address (MAIL_USER)"
$mailPassSecure = Read-Host "Gmail app password (MAIL_PASS)" -AsSecureString
$mailPass = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($mailPassSecure)
)
$alertEmail = Read-Host "Alert recipient email (ALERT_EMAIL)"

heroku config:set MAIL_USER=$mailUser --app $appName
heroku config:set MAIL_PASS=$mailPass --app $appName
heroku config:set ALERT_EMAIL=$alertEmail --app $appName
heroku config:set FLASK_ENV=production --app $appName
heroku config:set FLASK_DEBUG=0 --app $appName

Check-Success "Environment variables configured"
Write-Host ""

# Step 6: Commit Changes
Write-Host "Step 6: Committing changes to Git..."
git add .
git commit -m "Prepare for Heroku deployment" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "No changes to commit"
}
Write-Host ""

# Step 7: Deploy to Heroku
Write-Host "Step 7: Deploying to Heroku..."
Write-ColorOutput $Yellow "This may take several minutes..."

# Try main branch first, then master
git push heroku main 2>$null
if ($LASTEXITCODE -ne 0) {
    git push heroku master
}
Check-Success "Deployment"
Write-Host ""

# Step 8: Scale Dynos
Write-Host "Step 8: Scaling dynos..."
heroku ps:scale web=1 --app $appName
Check-Success "Dyno scaling"
Write-Host ""

# Step 9: Initialize Database
Write-Host "Step 9: Initializing database..."
heroku run python init_db.py --app $appName
Check-Success "Database initialization"
Write-Host ""

# Step 10: Open App
Write-Host "Step 10: Opening app..."
heroku open --app $appName
Write-Host ""

# Display Status
Write-Host "======================================"
Write-ColorOutput $Green "Deployment Complete! 🚀"
Write-Host "======================================"
Write-Host ""
Write-Host "App URL: https://$appName.herokuapp.com/"
Write-Host ""
Write-Host "Useful commands:"
Write-Host "  View logs:    heroku logs --tail --app $appName"
Write-Host "  Check status: heroku ps --app $appName"
Write-Host "  Restart:      heroku restart --app $appName"
Write-Host ""
Write-Host "View your app now in the browser!"
Write-Host ""

