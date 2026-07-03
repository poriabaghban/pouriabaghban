# 🚀 لیست کنترلی استقرار Django

این فایل یک لیست کنترلی جامع برای استقرار پروژه Django بر روی سرور تولید فراهم می‌کند.

## ✅ قبل از استقرار (Pre-Deployment)

### تنظیمات امنیتی
- [ ] `SECRET_KEY` را تولید کرده و تغییر کرده‌ام
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- [ ] `DEBUG = False` تنظیم شده‌است
- [ ] `ALLOWED_HOSTS` به درستی تنظیم شده‌است
- [ ] `SECURE_SSL_REDIRECT = True` فعال است
- [ ] `SESSION_COOKIE_SECURE = True` فعال است
- [ ] `CSRF_COOKIE_SECURE = True` فعال است
- [ ] `SECURE_HSTS_SECONDS` تنظیم شده‌است

### پایگاه‌داده
- [ ] از SQLite به PostgreSQL منتقل شده‌ام
- [ ] اتصال پایگاه‌داده آزمایش شده‌است
- [ ] Migration‌ها اجرا شده‌اند
- [ ] Backup سیستم تنظیم شده‌است
- [ ] داده‌های Sensitive حذف شده‌اند (email passwords, etc.)

### Static و Media Files
- [ ] `python manage.py collectstatic` اجرا شده‌است
- [ ] مسیرهای Static و Media صحیح تنظیم شده‌اند
- [ ] `STATICFILES_DIRS` و `STATIC_ROOT` متفاوت است
- [ ] Nginx/Apache برای سرو Static Files تنظیم شده‌است

### Email
- [ ] Email Settings صحیح تنظیم شده‌اند
- [ ] App Password (برای Gmail) تنظیم شده‌است
- [ ] ارسال Test Email موفق بوده‌است

### Requirements
- [ ] `requirements.txt` به روز است
- [ ] تمام وابستگی‌ها نصب شده‌اند
- [ ] Python version منطبق است

### تست‌های محلی
- [ ] `python manage.py runserver` بدون خطا کار می‌کند
- [ ] `python manage.py test` تمام تست‌ها می‌رد
- [ ] `python manage.py check --deploy` بدون خطا است
- [ ] Admin Panel بدرستی کار می‌کند

---

## 🖥️ هنگام استقرار (During Deployment)

### سرور تنظیم
- [ ] Ubuntu/Debian نصب شده‌است
- [ ] Python 3.10+ نصب شده‌است
- [ ] PostgreSQL نصب و فعال شده‌است
- [ ] Nginx نصب شده‌است
- [ ] Redis نصب شده‌است (اختیاری اما توصیه شده)
- [ ] Supervisor نصب شده‌است

### Python Environment
- [ ] Virtual Environment ایجاد شده‌است
  ```bash
  python3.10 -m venv venv
  ```
- [ ] Virtual Environment فعال شده‌است
  ```bash
  source venv/bin/activate
  ```
- [ ] Requirements نصب شده‌اند
  ```bash
  pip install -r requirements.txt
  ```

### پروژه Setup
- [ ] پروژه از Git کلون شده‌است
- [ ] `.env` فایل ایجاد شده‌است
- [ ] تمام متغیرهای `ENV` تنظیم شده‌اند
- [ ] `manage.py` اجرایی است

### Database Setup
- [ ] PostgreSQL User ایجاد شده‌است
- [ ] Database ایجاد شده‌است
- [ ] Migrations اجرا شده‌اند
  ```bash
  python manage.py migrate --settings=pouriabaghban3.settings_production
  ```

### Static Files
- [ ] Static Files جمع‌آوری شده‌اند
  ```bash
  python manage.py collectstatic --noinput --settings=pouriabaghban3.settings_production
  ```

### Gunicorn Setup
- [ ] Gunicorn نصب شده‌است
- [ ] Service File ایجاد شده‌است
- [ ] Service فعال شده‌است
  ```bash
  sudo systemctl enable gunicorn
  sudo systemctl start gunicorn
  ```

### Nginx Setup
- [ ] Nginx Config ایجاد شده‌است
- [ ] Site فعال شده‌است
  ```bash
  sudo ln -s /etc/nginx/sites-available/pouriabaghban3 /etc/nginx/sites-enabled/
  ```
- [ ] Nginx restart شده‌است
  ```bash
  sudo systemctl restart nginx
  ```

### SSL/HTTPS
- [ ] Let's Encrypt Certificate درخواست شده‌است
  ```bash
  sudo certbot certonly --nginx -d yourdomain.com
  ```
- [ ] Certificate Renewal تنظیم شده‌است
- [ ] HTTPS بدرستی کار می‌کند

### Firewall
- [ ] SSH (22) باز است
- [ ] HTTP (80) باز است
- [ ] HTTPS (443) باز است
- [ ] بقیه پورت‌ها بسته‌اند

---

## ✨ بعد از استقرار (Post-Deployment)

### تست‌های اولیه
- [ ] وب‌سایت روی `https://yourdomain.com` بارگیری می‌شود
- [ ] Admin Panel در `/admin/` در دسترس است
- [ ] Static Files (CSS, JS) بارگیری می‌شوند
- [ ] Media Files نمایش می‌دهند
- [ ] Dashboard بدرستی کار می‌کند

### فعالیت
- [ ] تمام صفحات بدرستی بارگیری می‌شوند
- [ ] Forms بدرستی کار می‌کنند
- [ ] Email فرستادن کار می‌کند
- [ ] Blog Posts منتشر می‌شوند
- [ ] Gallery تصاویر بارگیری می‌شود

### Security
- [ ] SSL Grade A است
- [ ] Security Headers موجود هستند
  ```bash
  curl -I https://yourdomain.com
  ```
- [ ] No Mixed Content Errors
- [ ] CSRF Protection فعال است

### Performance
- [ ] Page Load Time < 3 seconds
- [ ] Database Queries optimized است
- [ ] Static Files cached می‌شوند
- [ ] Compression فعال است

### Monitoring
- [ ] Error Logs مشاهده شده‌اند
- [ ] Access Logs بررسی شده‌اند
- [ ] Backup Script تست شده‌است
- [ ] Monitoring Tools تنظیم شده‌اند

### Backup & Recovery
- [ ] Database Backup کار می‌کند
- [ ] Media Files Backup کار می‌کند
- [ ] Backup Script زمان‌بندی شده‌است (cron)
- [ ] Restore Procedure تست شده‌است

---

## 📊 تست‌های اضافی

### Django Check
```bash
python manage.py check --deploy
```

### Health Check
```bash
curl -I https://yourdomain.com/health/
```

### Database Connection
```bash
python manage.py dbshell
```

### Static Files
```bash
python manage.py findstatic --verbosity 2
```

---

## 🔒 نکات امنیتی آخر

- [ ] Database Password تغییر شده‌است
- [ ] SSH Key Authentication فعال است
- [ ] Weak Passwords حذف شده‌اند
- [ ] Test Users حذف شده‌اند
- [ ] Debug Information پنهان شده‌است
- [ ] Error Pages Custom است
- [ ] Logs در جای محفوظ ذخیره می‌شوند

---

## 📞 اطلاعات تماس

اگر مشکل داشتید:
- 📧 ایمیل: poriab426@gmail.com
- 📱 تلفن: +98 905 548 3031

---

## 🎯 نکته نهایی

اگر تمام مواردی که باید انجام دهید را تکمیل کردید، پروژه شما آماده استقرار بر روی سرور تولید است!

✅ **Success!**
