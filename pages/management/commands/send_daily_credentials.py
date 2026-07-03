from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.contrib.auth.models import User
from datetime import datetime


class Command(BaseCommand):
    help = 'ارسال یادآوری روزانه اطلاعات ورود به ایمیل'

    def handle(self, *args, **options):
        # دریافت تمام کاربران
        users = User.objects.all()

        # ساخت متن ایمیل
        email_content = "🔐 یادآوری اطلاعات ورود\n"
        email_content += "=" * 50 + "\n"
        email_content += f"تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

        email_content += "تمام کاربران سیستم:\n"
        email_content += "-" * 50 + "\n"

        for user in users:
            email_content += f"نام کاربری: {user.username}\n"
            email_content += f"ایمیل: {user.email}\n"
            email_content += f"نوع: {'مدیر' if user.is_superuser else 'کاربر عادی'}\n"
            email_content += "-" * 50 + "\n"

        email_content += "\n⚠️ توجه: این پیام حاوی اطلاعات حساس است!\n"
        email_content += "لطفاً این ایمیل را محفوظ نگه دارید.\n"

        # ارسال ایمیل
        try:
            send_mail(
                subject='🔐 یادآوری روزانه - اطلاعات ورود',
                message=email_content,
                from_email='poriab426@gmail.com',
                recipient_list=['poriab426@gmail.com'],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('✅ ایمیل یادآوری با موفقیت ارسال شد!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ خطا در ارسال ایمیل: {str(e)}'))
