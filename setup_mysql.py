import os
import django
import mysql.connector
from mysql.connector import Error

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pouriabaghban3.settings')
django.setup()

# اطلاعات اتصال MySQL
try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password=''
    )
    
    cursor = connection.cursor()
    
    # ایجاد دیتابیس
    cursor.execute("""
        CREATE DATABASE IF NOT EXISTS pouriabaghban3_db 
        DEFAULT CHARACTER SET utf8mb4 
        COLLATE utf8mb4_unicode_ci;
    """)
    
    print("✅ دیتابیس 'pouriabaghban3_db' با موفقیت ایجاد شد!")
    
    cursor.close()
    connection.close()
    
except Error as err:
    if err.errno == 2003:
        print("❌ خطا: MySQL Server در حال اجرا نیست")
        print("لطفاً MySQL را شروع کنید")
    else:
        print(f"❌ خطا: {err}")
