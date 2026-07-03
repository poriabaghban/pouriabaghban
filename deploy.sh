#!/bin/bash
# Deployment script for pouriabaghban3 Django project
# This script automates the deployment process on Ubuntu/Debian servers

set -e  # Exit on error

echo "🚀 Starting deployment process..."
echo "=================================="

# Configuration
DOMAIN="yourdomain.com"
APP_USER="appuser"
PROJECT_PATH="/home/$APP_USER/pouriabaghban3"
VENV_PATH="$PROJECT_PATH/venv"
GUNICORN_SOCK="$PROJECT_PATH/gunicorn.sock"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# 1. Update System
echo -e "\n${YELLOW}Step 1: Updating system packages...${NC}"
sudo apt update
sudo apt upgrade -y
print_status "System packages updated"

# 2. Install Dependencies
echo -e "\n${YELLOW}Step 2: Installing dependencies...${NC}"
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    supervisor \
    redis-server \
    curl \
    certbot \
    python3-certbot-nginx
print_status "Dependencies installed"

# 3. Create App User
echo -e "\n${YELLOW}Step 3: Creating application user...${NC}"
if id "$APP_USER" &>/dev/null; then
    print_warning "User $APP_USER already exists"
else
    sudo useradd -m -s /bin/bash "$APP_USER"
    print_status "User $APP_USER created"
fi

# 4. Clone or update repository
echo -e "\n${YELLOW}Step 4: Cloning/updating repository...${NC}"
if [ -d "$PROJECT_PATH" ]; then
    cd "$PROJECT_PATH"
    sudo -u "$APP_USER" git pull origin master
    print_status "Repository updated"
else
    sudo -u "$APP_USER" git clone https://github.com/poriabaghban/pouriabaghban3.git "$PROJECT_PATH"
    print_status "Repository cloned"
fi

# 5. Create Virtual Environment
echo -e "\n${YELLOW}Step 5: Creating Python virtual environment...${NC}"
if [ ! -d "$VENV_PATH" ]; then
    sudo -u "$APP_USER" python3.10 -m venv "$VENV_PATH"
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# 6. Install Python Dependencies
echo -e "\n${YELLOW}Step 6: Installing Python dependencies...${NC}"
sudo -u "$APP_USER" "$VENV_PATH/bin/pip" install --upgrade pip setuptools wheel
sudo -u "$APP_USER" "$VENV_PATH/bin/pip" install -r "$PROJECT_PATH/requirements.txt"
print_status "Python dependencies installed"

# 7. Create .env file
echo -e "\n${YELLOW}Step 7: Setting up environment variables...${NC}"
if [ ! -f "$PROJECT_PATH/.env" ]; then
    print_warning "Please configure .env file manually"
    print_warning "Copy .env.example and update with your settings"
    print_warning "Location: $PROJECT_PATH/.env"
else
    print_status ".env file found"
fi

# 8. Create log directory
echo -e "\n${YELLOW}Step 8: Creating log directory...${NC}"
sudo mkdir -p "$PROJECT_PATH/logs"
sudo chown "$APP_USER:$APP_USER" "$PROJECT_PATH/logs"
print_status "Log directory created"

# 9. Collect Static Files
echo -e "\n${YELLOW}Step 9: Collecting static files...${NC}"
cd "$PROJECT_PATH"
sudo -u "$APP_USER" "$VENV_PATH/bin/python" manage.py collectstatic --noinput --settings=pouriabaghban3.settings_production
print_status "Static files collected"

# 10. Run Migrations
echo -e "\n${YELLOW}Step 10: Running database migrations...${NC}"
sudo -u "$APP_USER" "$VENV_PATH/bin/python" manage.py migrate --settings=pouriabaghban3.settings_production
print_status "Database migrations completed"

# 11. Create Gunicorn Systemd Service
echo -e "\n${YELLOW}Step 11: Setting up Gunicorn service...${NC}"
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=Gunicorn application server for pouriabaghban3
After=network.target

[Service]
User=$APP_USER
WorkingDirectory=$PROJECT_PATH
Environment="PATH=$VENV_PATH/bin"
Environment="DJANGO_SETTINGS_MODULE=pouriabaghban3.settings_production"
ExecStart=$VENV_PATH/bin/gunicorn \
    --workers 3 \
    --worker-class sync \
    --max-requests 1000 \
    --timeout 30 \
    --bind unix:$GUNICORN_SOCK \
    pouriabaghban3.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable gunicorn
print_status "Gunicorn service configured"

# 12. Set proper permissions
echo -e "\n${YELLOW}Step 12: Setting file permissions...${NC}"
sudo chown -R "$APP_USER:$APP_USER" "$PROJECT_PATH"
sudo chmod +x "$PROJECT_PATH/manage.py"
print_status "Permissions set"

echo -e "\n${GREEN}=================================="
echo "✅ Deployment preparation complete!"
echo "=================================="
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit .env file: nano $PROJECT_PATH/.env"
echo "2. Create database and user in PostgreSQL"
echo "3. Configure Nginx: sudo nano /etc/nginx/sites-available/pouriabaghban3"
echo "4. Enable Nginx site: sudo ln -s /etc/nginx/sites-available/pouriabaghban3 /etc/nginx/sites-enabled/"
echo "5. Test Nginx: sudo nginx -t && sudo systemctl restart nginx"
echo "6. Get SSL certificate: sudo certbot certonly --nginx -d $DOMAIN"
echo "7. Start Gunicorn: sudo systemctl start gunicorn"
echo ""
echo "For help: Check PRODUCTION_DEPLOYMENT.md"
