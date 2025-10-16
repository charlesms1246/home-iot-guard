#!/bin/bash

# Home IoT Guardian - Heroku Deployment Script (Linux/macOS)

echo "======================================"
echo "Home IoT Guardian - Heroku Deployment"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        exit 1
    fi
}

# Step 1: Check Heroku CLI
echo "Step 1: Checking Heroku CLI..."
if command -v heroku &> /dev/null; then
    heroku_version=$(heroku --version)
    echo -e "${GREEN}✓ Heroku CLI installed: $heroku_version${NC}"
else
    echo -e "${RED}✗ Heroku CLI not found!${NC}"
    echo "Install from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi
echo ""

# Step 2: Check Heroku Login
echo "Step 2: Checking Heroku authentication..."
if heroku auth:whoami &> /dev/null; then
    user=$(heroku auth:whoami)
    echo -e "${GREEN}✓ Logged in as: $user${NC}"
else
    echo -e "${YELLOW}! Not logged in. Opening login...${NC}"
    heroku login
    check_success "Heroku login"
fi
echo ""

# Step 3: Check/Create Heroku App
echo "Step 3: Setting up Heroku app..."
read -p "Enter Heroku app name (or press Enter for 'home-iot-guardian'): " app_name
app_name=${app_name:-home-iot-guardian}

if heroku apps:info --app $app_name &> /dev/null; then
    echo -e "${GREEN}✓ App '$app_name' already exists${NC}"
else
    echo "Creating new app '$app_name'..."
    heroku create $app_name
    check_success "App creation"
fi
echo ""

# Step 4: Set Buildpack
echo "Step 4: Setting buildpack..."
heroku buildpacks:set heroku/python --app $app_name
check_success "Buildpack set"
echo ""

# Step 5: Configure Environment Variables
echo "Step 5: Configuring environment variables..."
echo -e "${YELLOW}Please enter your configuration:${NC}"

read -p "Gmail address (MAIL_USER): " mail_user
read -sp "Gmail app password (MAIL_PASS): " mail_pass
echo ""
read -p "Alert recipient email (ALERT_EMAIL): " alert_email

heroku config:set MAIL_USER=$mail_user --app $app_name
heroku config:set MAIL_PASS=$mail_pass --app $app_name
heroku config:set ALERT_EMAIL=$alert_email --app $app_name
heroku config:set FLASK_ENV=production --app $app_name
heroku config:set FLASK_DEBUG=0 --app $app_name

check_success "Environment variables configured"
echo ""

# Step 6: Commit Changes
echo "Step 6: Committing changes to Git..."
git add .
git commit -m "Prepare for Heroku deployment" 2>/dev/null || echo "No changes to commit"
check_success "Git commit"
echo ""

# Step 7: Deploy to Heroku
echo "Step 7: Deploying to Heroku..."
echo -e "${YELLOW}This may take several minutes...${NC}"
git push heroku main || git push heroku master
check_success "Deployment"
echo ""

# Step 8: Scale Dynos
echo "Step 8: Scaling dynos..."
heroku ps:scale web=1 --app $app_name
check_success "Dyno scaling"
echo ""

# Step 9: Initialize Database
echo "Step 9: Initializing database..."
heroku run python init_db.py --app $app_name
check_success "Database initialization"
echo ""

# Step 10: Open App
echo "Step 10: Opening app..."
heroku open --app $app_name
echo ""

# Display Status
echo "======================================"
echo "Deployment Complete! 🚀"
echo "======================================"
echo ""
echo "App URL: https://$app_name.herokuapp.com/"
echo ""
echo "Useful commands:"
echo "  View logs:    heroku logs --tail --app $app_name"
echo "  Check status: heroku ps --app $app_name"
echo "  Restart:      heroku restart --app $app_name"
echo ""
echo "View your app now in the browser!"
echo ""

