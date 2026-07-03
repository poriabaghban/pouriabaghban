# 📖 Command Reference Guide

این راهنما شامل تمام دستورات مورد نیاز برای deployment و maintenance است.

---

## 🔧 Setup Commands

### Create Virtual Environment
```bash
# Python 3.10
python3.10 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install from requirements
pip install -r requirements.txt

# Production dependencies only
pip install -r requirements.txt --no-dev
```

### Environment Configuration
```bash
# Copy example
cp .env.example .env

# Edit env
nano .env

# Check env variables (Python)
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.environ.get('SECRET_KEY'))"
```

---

## 🗄️ Database Commands

### Create PostgreSQL User and Database
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# SQL Commands
CREATE DATABASE pouriabaghban3;
CREATE USER appuser WITH PASSWORD 'your-password';
ALTER ROLE appuser SET client_encoding TO 'utf8';
ALTER ROLE appuser SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE pouriabaghban3 TO appuser;
\q
```

### Django Database Commands
```bash
# Check migrations
python manage.py showmigrations

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Specific settings
python manage.py migrate --settings=pouriabaghban3.settings_production

# Create superuser
python manage.py createsuperuser

# Database shell
python manage.py dbshell

# Database dump (backup)
pg_dump -h localhost -U appuser pouriabaghban3 > backup.sql

# Database restore
psql -h localhost -U appuser pouriabaghban3 < backup.sql
```

---

## 🌐 Static and Media Files

### Collect Static Files
```bash
# Development
python manage.py collectstatic

# Production
python manage.py collectstatic --noinput --settings=pouriabaghban3.settings_production

# Clear old and collect
python manage.py collectstatic --clear --noinput --settings=pouriabaghban3.settings_production

# Find specific static files
python manage.py findstatic --verbosity 2

# List collected files
ls -la staticfiles/
```

### File Permissions
```bash
# Change ownership
sudo chown -R www-data:www-data /home/appuser/pouriabaghban3/staticfiles/
sudo chown -R www-data:www-data /home/appuser/pouriabaghban3/media/

# Set permissions
sudo chmod -R 755 /home/appuser/pouriabaghban3/staticfiles/
sudo chmod -R 755 /home/appuser/pouriabaghban3/media/

# Check permissions
ls -la /home/appuser/pouriabaghban3/
```

---

## 🔍 Debugging & Testing

### Django Check
```bash
# General check
python manage.py check

# Production check
python manage.py check --deploy

# Specific app check
python manage.py check blog
```

### Django Shell
```bash
# Interactive shell
python manage.py shell

# Example queries
from blog.models import Post
Post.objects.all()
Post.objects.filter(published=True).count()
```

### Run Server
```bash
# Development
python manage.py runserver

# Production (Gunicorn)
gunicorn --bind 0.0.0.0:8000 --workers 3 pouriabaghban3.wsgi:application

# With settings
gunicorn --bind 0.0.0.0:8000 \
    --workers 3 \
    --env DJANGO_SETTINGS_MODULE=pouriabaghban3.settings_production \
    pouriabaghban3.wsgi:application
```

---

## 🚀 Gunicorn Commands

### Start/Stop/Restart
```bash
# Start service
sudo systemctl start gunicorn

# Stop service
sudo systemctl stop gunicorn

# Restart service
sudo systemctl restart gunicorn

# Check status
sudo systemctl status gunicorn

# Enable on boot
sudo systemctl enable gunicorn

# View logs
journalctl -u gunicorn -n 50 -f

# Detailed logs
journalctl -u gunicorn -n 100 --since "2 hours ago"
```

### Manual Start
```bash
# Simple start
cd /home/appuser/pouriabaghban3
venv/bin/gunicorn pouriabaghban3.wsgi:application

# With options
gunicorn \
    --workers 3 \
    --worker-class sync \
    --max-requests 1000 \
    --timeout 30 \
    --bind unix:gunicorn.sock \
    pouriabaghban3.wsgi:application

# Background
nohup gunicorn ... > gunicorn.log 2>&1 &
```

---

## 🌐 Nginx Commands

### Start/Stop/Restart
```bash
# Test configuration
sudo nginx -t

# Start service
sudo systemctl start nginx

# Stop service
sudo systemctl stop nginx

# Restart service
sudo systemctl restart nginx

# Reload (graceful)
sudo systemctl reload nginx

# Status
sudo systemctl status nginx

# Enable on boot
sudo systemctl enable nginx
```

### Nginx Logs
```bash
# View access log
tail -f /var/log/nginx/pouriabaghban3_access.log

# View error log
tail -f /var/log/nginx/pouriabaghban3_error.log

# Search logs
grep "ERROR" /var/log/nginx/pouriabaghban3_error.log

# Count requests
wc -l /var/log/nginx/pouriabaghban3_access.log

# IP addresses
awk '{print $1}' /var/log/nginx/pouriabaghban3_access.log | sort | uniq -c | sort -rn
```

### Nginx Configuration
```bash
# Edit configuration
sudo nano /etc/nginx/sites-available/pouriabaghban3

# Enable site
sudo ln -s /etc/nginx/sites-available/pouriabaghban3 /etc/nginx/sites-enabled/

# Disable site
sudo rm /etc/nginx/sites-enabled/pouriabaghban3

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

---

## 🔐 SSL/HTTPS Commands

### Let's Encrypt with Certbot
```bash
# Get certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Manual verification
sudo certbot certonly --manual -d yourdomain.com

# List certificates
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Force renewal
sudo certbot renew --force-renewal

# Renewal test
sudo certbot renew --dry-run

# Auto-renewal status
sudo systemctl status certbot.timer
sudo systemctl enable certbot.timer
```

### Certificate Files
```bash
# Certificate location
ls -la /etc/letsencrypt/live/yourdomain.com/

# View certificate
sudo openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -text -noout

# Check expiration
sudo certbot certificates

# Certificate info
openssl s_client -connect yourdomain.com:443 -showcerts
```

---

## 📦 Backup & Restore

### Database Backup
```bash
# Backup
pg_dump -h localhost -U appuser pouriabaghban3 > backup.sql

# Compressed backup
pg_dump -h localhost -U appuser pouriabaghban3 | gzip > backup.sql.gz

# With custom format
pg_dump -h localhost -U appuser -F c pouriabaghban3 > backup.dump

# Remote backup
pg_dump -h remote-host -U appuser pouriabaghban3 > backup.sql
```

### Database Restore
```bash
# Restore from SQL
psql -h localhost -U appuser pouriabaghban3 < backup.sql

# Restore from compressed
gunzip -c backup.sql.gz | psql -h localhost -U appuser pouriabaghban3

# Restore from dump
pg_restore -h localhost -U appuser -d pouriabaghban3 backup.dump
```

### File Backups
```bash
# Backup media files
tar -czf media_backup.tar.gz media/

# Backup static files
tar -czf static_backup.tar.gz staticfiles/

# Backup everything
tar -czf full_backup.tar.gz --exclude=.git --exclude=venv --exclude=.env .

# Restore files
tar -xzf media_backup.tar.gz
```

### Automated Backup Script
```bash
# Make executable
chmod +x backup.sh
chmod +x restore.sh

# Run backup
bash backup.sh

# Restore
bash restore.sh 20240101_120000
```

### Cron Job Setup
```bash
# Edit crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /home/appuser/backup.sh >> /var/log/backup.log 2>&1

# Weekly backup
0 3 * * 0 /home/appuser/backup.sh

# List cron jobs
crontab -l

# Remove cron job
crontab -r
```

---

## 📊 Monitoring Commands

### System Resources
```bash
# Disk usage
df -h

# Directory size
du -sh /home/appuser/pouriabaghban3

# Memory usage
free -m

# CPU usage
top

# Load average
uptime

# Network statistics
netstat -an | grep ESTABLISHED | wc -l

# Open ports
sudo netstat -tlnp | grep LISTEN
sudo ss -tlnp | grep LISTEN
```

### Process Management
```bash
# List processes
ps aux | grep gunicorn
ps aux | grep nginx

# Kill process
kill -9 <PID>

# Background jobs
jobs

# Foreground/background
fg, bg
```

### Log Management
```bash
# View logs
tail -f /home/appuser/pouriabaghban3/logs/django.log

# Search logs
grep "ERROR" /home/appuser/pouriabaghban3/logs/django.log

# Log rotation status
logrotate -d /etc/logrotate.d/pouriabaghban3

# Compress old logs
gzip /var/log/nginx/*.log.1
```

---

## 🔧 Troubleshooting Commands

### Check Everything
```bash
# Django check
python manage.py check --deploy

# Nginx syntax
sudo nginx -t

# Database connection
python manage.py dbshell

# Python version
python --version

# Pip list
pip list | grep -E "Django|gunicorn|psycopg2"
```

### Clear Cache
```bash
# Redis flush
redis-cli FLUSHALL

# Django cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Session cleanup
python manage.py clearsessions
```

### Reset Database
```bash
# WARNING: This deletes all data!

# Drop database
dropdb -h localhost -U appuser pouriabaghban3

# Recreate database
createdb -h localhost -U appuser pouriabaghban3

# Run migrations
python manage.py migrate --settings=pouriabaghban3.settings_production

# Create superuser
python manage.py createsuperuser --settings=pouriabaghban3.settings_production
```

---

## 🚀 Deployment Sequence

```bash
# 1. SSH to server
ssh appuser@yourdomain.com

# 2. Navigate to project
cd /home/appuser/pouriabaghban3

# 3. Update code
git pull origin master

# 4. Activate environment
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Collect static
python manage.py collectstatic --noinput --settings=pouriabaghban3.settings_production

# 7. Run migrations
python manage.py migrate --settings=pouriabaghban3.settings_production

# 8. Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 9. Check status
sudo systemctl status gunicorn
sudo systemctl status nginx

# 10. View logs
tail -f /var/log/nginx/pouriabaghban3_error.log
```

---

## 📱 Common Patterns

### Watch File Changes
```bash
# Watch logs
watch -n 1 'tail -20 /var/log/nginx/pouriabaghban3_error.log'

# Watch disk usage
watch -n 5 'du -sh /home/appuser/pouriabaghban3'

# Watch process
watch -n 1 'ps aux | grep gunicorn'
```

### Find & Replace
```bash
# Find files
find . -name "*.py" -type f

# Find large files
find . -size +10M

# Find recently modified
find . -mtime -7

# Delete files
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### Secure Commands
```bash
# Generate secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Hash password
python -c "from django.contrib.auth.hashers import make_password; print(make_password('password'))"

# Check file permissions
stat -c '%A %U:%G %n' /home/appuser/pouriabaghban3/.env
```

---

## 🎯 Quick Command Lookup

| Task | Command |
|------|---------|
| Test config | `python manage.py check --deploy` |
| Restart web | `sudo systemctl restart gunicorn nginx` |
| View logs | `tail -f /var/log/nginx/pouriabaghban3_error.log` |
| Backup database | `bash backup.sh` |
| Restore database | `bash restore.sh 20240101_120000` |
| Collect static | `python manage.py collectstatic --noinput` |
| Database shell | `python manage.py dbshell` |
| Create user | `python manage.py createsuperuser` |
| Clear cache | `redis-cli FLUSHALL` |
| Update code | `git pull && pip install -r requirements.txt && python manage.py migrate` |

---

**یادداشت**: همیشه قبل از اجرای دستورات خطرناک (`DROP DATABASE`، `DELETE`) یک backup بگیرید!

**آخرین بروزرسانی**: December 4, 2024
