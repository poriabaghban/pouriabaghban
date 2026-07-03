# 📦 راهنمای استقرار در Production (سرور)

این راهنما نحوه آماده کردن و استقرار پروژه Django بر روی سرور تولید را توضیح می‌دهد.

---

## 📋 فهرست مطالب

1. [الزامات سرور](#الزامات-سرور)
2. [کاف‌های امنیتی](#کاف‌های-امنیتی)
3. [نصب و تنظیم](#نصب-و-تنظیم)
4. [پیکربندی Web Server](#پیکربندی-web-server)
5. [پایگاه‌داده](#پایگاه‌داده)
6. [Static و Media Files](#static-و-media-files)
7. [SSL/HTTPS](#ssلhttps)
8. [Monitoring و Backup](#monitoring-و-backup)
9. [بازآمدن از مشکل](#بازآمدن-از-مشکل)
10. [لیست‌های کنترلی](#لیست‌های-کنترلی)

---

## ⚙️ الزامات سرور

### سیستم عامل
- **Ubuntu 20.04+** یا **Debian 10+** (توصیه شده)
- یا **CentOS 8+**

### نرم‌افزار مورد نیاز
```bash
# Ubuntu/Debian
sudo apt update
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
    wget \
    certbot \
    python3-certbot-nginx
```

### منابع سرور (بدترین حالت)
- **CPU**: 2 vCPU
- **RAM**: 2 GB (حداقل)
- **Storage**: 20 GB (برای شروع)
- **Bandwidth**: بدون محدودیت

---

## 🔒 کاف‌های امنیتی

### 1️⃣ تغییر `SECRET_KEY`
```bash
# تولید SECRET_KEY جدید
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# نتیجه را در `.env` ذخیره کنید
SECRET_KEY=your-new-generated-key-here
```

### 2️⃣ تنظیم `ALLOWED_HOSTS`
```env
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,ip-address
```

### 3️⃣ غیرفعال کردن `DEBUG`
```env
DEBUG=False
```

### 4️⃣ استفاده از `HTTPS`
- تمام اتصالات باید از `HTTPS` باشند
- استفاده از `Let's Encrypt` برای گواهی رایگان

### 5️⃣ Firewall تنظیم کنید
```bash
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
```

### 6️⃣ SSH Key Authentication
```bash
# غیرفعال کردن ورود Password
sudo nano /etc/ssh/sshd_config
# تغییر: PasswordAuthentication yes → no
sudo systemctl restart ssh
```

---

## 📦 نصب و تنظیم

### مرحله 1: آماده کردن سرور
```bash
# ایجاد کاربر جدید (بجای root)
sudo useradd -m -s /bin/bash appuser
sudo usermod -aG sudo appuser

# جابجایی به پوشه خانگی
cd /home/appuser
```

### مرحله 2: کلون کردن پروژه
```bash
git clone <repository-url>
cd pouriabaghban3
```

### مرحله 3: محیط مجازی Python
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

### مرحله 4: نصب وابستگی‌ها
```bash
pip install -r requirements.txt
pip install gunicorn psycopg2-binary redis whitenoise
```

### مرحله 5: تنظیم متغیرهای محیط
```bash
# کپی کردن فایل نمونه
cp .env.example .env

# ویرایش .env
nano .env
```

**تنظیمات ضروری در `.env`:**
```env
DEBUG=False
SECRET_KEY=your-generated-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/pouriabaghban3
EMAIL_HOST_PASSWORD=your-app-password
```

### مرحله 6: مهاجرت پایگاه‌داده
```bash
python manage.py migrate --settings=pouriabaghban3.settings_production
```

### مرحله 7: جمع‌آوری Static Files
```bash
python manage.py collectstatic --noinput --settings=pouriabaghban3.settings_production
```

### مرحله 8: ایجاد Superuser
```bash
python manage.py createsuperuser --settings=pouriabaghban3.settings_production
```

---

## 🌐 پیکربندی Web Server

### استفاده از Gunicorn + Nginx

#### گام 1: پیکربندی Gunicorn
```bash
# ایجاد فایل سرویس
sudo nano /etc/systemd/system/gunicorn.service
```

**محتوای فایل:**
```ini
[Unit]
Description=Gunicorn application server for pouriabaghban3
After=network.target

[Service]
User=appuser
WorkingDirectory=/home/appuser/pouriabaghban3
Environment="PATH=/home/appuser/pouriabaghban3/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=pouriabaghban3.settings_production"
ExecStart=/home/appuser/pouriabaghban3/venv/bin/gunicorn \
    --workers 3 \
    --worker-class sync \
    --worker-tmp-dir /dev/shm \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --timeout 30 \
    --bind unix:/home/appuser/pouriabaghban3/gunicorn.sock \
    pouriabaghban3.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# فعال کردن سرویس
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

#### گام 2: پیکربندی Nginx
```bash
# ایجاد فایل پیکربندی Nginx
sudo nano /etc/nginx/sites-available/pouriabaghban3
```

**محتوای فایل:**
```nginx
upstream gunicorn {
    server unix:/home/appuser/pouriabaghban3/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    client_max_body_size 5M;

    # بازگردانی به HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    client_max_body_size 5M;

    # گواهی SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # تنظیمات SSL بهترین عملکرد
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    access_log /var/log/nginx/pouriabaghban3_access.log;
    error_log /var/log/nginx/pouriabaghban3_error.log;

    location /static/ {
        alias /home/appuser/pouriabaghban3/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/appuser/pouriabaghban3/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
        proxy_request_buffering off;
    }
}
```

```bash
# فعال کردن سایت
sudo ln -s /etc/nginx/sites-available/pouriabaghban3 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🗄️ پایگاه‌داده

### تبدیل از SQLite به PostgreSQL

#### گام 1: نصب PostgreSQL
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### گام 2: ایجاد Database و User
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE pouriabaghban3;
CREATE USER appuser WITH PASSWORD 'your-strong-password';
ALTER ROLE appuser SET client_encoding TO 'utf8';
ALTER ROLE appuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE appuser SET default_transaction_deferrable TO on;
ALTER ROLE appuser SET default_transaction_read_committed TO off;
GRANT ALL PRIVILEGES ON DATABASE pouriabaghban3 TO appuser;
\q
```

#### گام 3: تنظیم در `.env`
```env
DATABASE_URL=postgresql://appuser:your-password@localhost:5432/pouriabaghban3
```

#### گام 4: نصب درایور PostgreSQL
```bash
pip install psycopg2-binary
```

---

## 📁 Static و Media Files

### تنظیم صحیح Static Files

```bash
# جمع‌آوری static files
python manage.py collectstatic --noinput --settings=pouriabaghban3.settings_production

# صاحب‌خانه تغییر دهید
sudo chown -R www-data:www-data /home/appuser/pouriabaghban3/staticfiles
sudo chown -R www-data:www-data /home/appuser/pouriabaghban3/media
```

### Compression
```bash
# نصب
pip install django-compressor

# مکمل کردن settings
echo "INSTALLED_APPS += ['compressor']" >> pouriabaghban3/settings_production.py
```

---

## 🔐 SSL/HTTPS

### استفاده از Let's Encrypt

```bash
# دریافت گواهی رایگان
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# تجدید خودکار
sudo certbot renew --dry-run
```

---

## 📊 Monitoring و Backup

### Backup خودکار

```bash
#!/bin/bash
# /home/appuser/backup.sh

BACKUP_DIR="/home/appuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup پایگاه‌داده
pg_dump -h localhost -U appuser -d pouriabaghban3 > $BACKUP_DIR/db_$DATE.sql

# Backup Media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/appuser/pouriabaghban3/media/

# حذف backup های قدیمی (30 روز)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed at $(date)" >> /var/log/backup.log
```

```bash
# اجازه اجرا
chmod +x /home/appuser/backup.sh

# زمان‌بندی با Cron
crontab -e
# اضافه کنید: 0 2 * * * /home/appuser/backup.sh
```

### Logs Monitoring
```bash
# مشاهده Nginx logs
tail -f /var/log/nginx/pouriabaghban3_error.log

# مشاهده Django logs
tail -f /home/appuser/pouriabaghban3/logs/django.log
```

---

## 🔧 بازآمدن از مشکل

### Gunicorn نمی‌رود
```bash
# بررسی وضعیت
systemctl status gunicorn

# مشاهده logs
journalctl -u gunicorn -n 50 -f

# راه‌اندازی دوباره
systemctl restart gunicorn
```

### Nginx خطا می‌دهد
```bash
# بررسی فایل‌های پیکربندی
sudo nginx -t

# مشاهده logs
tail -f /var/log/nginx/error.log

# راه‌اندازی دوباره
sudo systemctl restart nginx
```

### مشکل Static Files
```bash
# مجددی جمع‌آوری
python manage.py collectstatic --clear --noinput --settings=pouriabaghban3.settings_production

# صاحب‌خانه بررسی کنید
ls -la /home/appuser/pouriabaghban3/staticfiles/
```

---

## ✅ لیست‌های کنترلی

### قبل از راه‌اندازی

- [ ] `SECRET_KEY` تغییر کرده‌ام
- [ ] `DEBUG = False` تنظیم کرده‌ام
- [ ] `ALLOWED_HOSTS` تنظیم کرده‌ام
- [ ] Email Settings صحیح است
- [ ] Database پیکربندی شده‌است
- [ ] Static Files جمع‌آوری شده‌اند
- [ ] Superuser ایجاد شده‌است
- [ ] SSL/HTTPS فعال است
- [ ] Firewall تنظیم شده‌است
- [ ] Backup سیستم تنظیم شده‌است

### بعد از راه‌اندازی

- [ ] وب‌سایت بر روی HTTPS کار می‌کند
- [ ] Static Files بارگیری می‌شوند
- [ ] Admin Panel در دسترس است
- [ ] Email فرستادن کار می‌کند
- [ ] Database بک‌آپ تنظیم شده‌است
- [ ] Monitoring تنظیم شده‌است
- [ ] Security Headers صحیح است
- [ ] Page Load Time مناسب است

---

## 📞 نکات اضافی

### Performance Optimization
- استفاده از Redis برای Caching
- استفاده از CDN برای Static Files
- Image Optimization
- Database Indexing

### Monitoring Tools
- **Sentry**: Error Tracking
- **New Relic**: Performance Monitoring
- **Datadog**: Infrastructure Monitoring

### لاگینگ
- Log Rotation تنظیم کنید
- بررسی منظم لاگ‌ها
- Alert سیستم تنظیم کنید

---

## 🎯 خلاصه

✅ پروژه اکنون برای production آماده است!

**نکات مهم:**
1. همیشه از HTTPS استفاده کنید
2. Backup منظم بگیرید
3. Updates منظم انجام دهید
4. Monitoring فعال نگه دارید
5. Security بررسی کنید

**اگر سؤالی داشتید:**
- 📧 ایمیل: poriab426@gmail.com
- 📱 تلفن: +98 905 548 3031

---

**آخرین بروزرسانی:** 1403/09/12
