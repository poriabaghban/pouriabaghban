@echo off
REM یادآوری روزانه اطلاعات ورود
REM این فایل هر روز ساعت 8 صبح اجرا می‌شود

cd /d E:\Desktop\pouriabaghban3
python manage.py send_daily_credentials

REM اگر خطایی رخ داد
if errorlevel 1 (
    echo خطا در ارسال ایمیل یادآوری
    exit /b 1
)

echo ایمیل یادآوری با موفقیت ارسال شد
exit /b 0
