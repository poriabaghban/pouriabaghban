# تست ارسال ایمیل لاگ‌ها (mail_admins)

این سند کوتاه به زبان فارسی توضیح می‌دهد چگونه پیکربندی لاگینگ که در `settings.py` قرار داده شده را در محیط توسعه یا تولید تست کنید تا خطاها به ایمیل `ADMINS` ارسال شوند.

نکته مهم: Django فقط زمانی به `mail_admins` ایمیل می‌فرستد که `DEBUG=False` باشد (فیلتر `RequireDebugFalse`). هنگام توسعه می‌توانید از `console` backend برای مشاهده محتوای ایمیل در کنسول استفاده کنید.

---

## پیش‌نیازها
- تنظیمات ایمیل در `settings.py` یا از طریق متغیرهای محیطی (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`) باید مقداردهی شود.
- مقدار `ADMINS` باید شامل ایمیل دریافت‌کنندگان باشد. ما از متغیر محیطی `ADMIN_EMAIL` استفاده می‌کنیم.

## روش 1 — تست سریع محلی (نمایش ایمیل در کنسول)
1. در PowerShell پوشه پروژه را باز کنید و مقادیر محیطی را قرار دهید (مثال):

```powershell
cd E:\Desktop\pouriabaghban3
$env:DEBUG = 'False'
$env:ADMIN_EMAIL = 'admin@example.com'
$env:DEFAULT_FROM_EMAIL = 'server@example.com'
$env:EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# اگر از virtualenv استفاده می‌کنید، فعالش کنید (اختیاری):
# .\env\Scripts\Activate.ps1
```

2. سرور را اجرا کنید (یا نیازی به آن نیست اگر از shell استفاده می‌کنید):

```powershell
python manage.py runserver
```

3. برای فراخوانی handler می‌توانید از یک خط فرمان پایتون استفاده کنید که لاگی با سطح ERROR تولید کند (در همان پوشه پروژه):

```powershell
python manage.py shell -c "import django, logging; django.setup(); logging.getLogger('django.request').error('Test error to trigger mail_admins handler')"
```

با `console` backend محتوای ایمیل (subject، body) در کنسول چاپ می‌شود و می‌توانید تأیید کنید pipeline لاگینگ کار می‌کند.

## روش 2 — تست واقعی با SMTP
1. مقداردهی متغیرهای ایمیل را انجام دهید:

```powershell
$env:DEBUG = 'False'
$env:ADMIN_EMAIL = 'admin@example.com'
$env:DEFAULT_FROM_EMAIL = 'server@example.com'
$env:EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
$env:EMAIL_HOST = 'smtp.gmail.com'
$env:EMAIL_PORT = '587'
$env:EMAIL_USE_TLS = 'True'
$env:EMAIL_HOST_USER = 'you@gmail.com'
$env:EMAIL_HOST_PASSWORD = 'your-app-password'
```

2. سپس همان دستور shell بالا را اجرا کنید تا لاگ ERROR تولید شود و بررسی کنید ایمیل ارسال شده و به آدرس‌های داخل `ADMINS` رسیده است.

نکته: برای Gmail معمولاً باید یک app-password بسازید یا تنظیمات امنیتی را در اکانت تغییر دهید.

## روش 3 — تولید یک 500 از طریق View (موقتی)
می‌توانید یک view موقت بسازید که خطا پرتاب کند و آن را در آدرس‌دهی قرار دهید، سپس در مرورگر آن آدرس را باز کنید. پس از تست فراموش نکنید آن route/view را حذف کنید.

## نکات عیب‌یابی
- اگر ایمیل ارسال نشد، این‌ها را بررسی کنید:
  - `DEBUG` واقعاً `'False'` است (رشته یا بولین از env)، فیلتر `RequireDebugFalse` نباید اجازه ارسال را در حالت توسعه بدهد.
  - مقدار `ADMINS` شامل ایمیل درست است.
  - اطلاعات SMTP (نام کاربری، گذرواژه، پورت، TLS) درست است.
  - فایروال یا provider ایمیل ارسال را بلاک نکرده باشد.

- برای بررسی لاگ‌ها در فایل، می‌توانید یک handler دیگر مثل `RotatingFileHandler` اضافه کنید تا لاگ‌ها persistent شوند.

## پیشنهادات عملیاتی
- در محیط تولید: حتما `SECURE_SSL_REDIRECT=True` و `SECURE_HSTS_SECONDS` را پس از اطمینان از TLS فعال کنید.
- برای دریافت بهتر خطاها و تشریح stacktrace، در کنار mail_admins از سرویس‌هایی مثل Sentry استفاده کنید.

---

اگر مایل باشید می‌توانم یک فایل تست کوچک (`manage.py` command یا view) بسازم که با یک کلیک خطا تولید کند یا یک handler فایل لاگ چرخان اضافه کنم و تنظیمات `LOGGING` را برای ثبت در فایل نیز اضافه کنم.