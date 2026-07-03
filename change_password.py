import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pouriabaghban3.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'poriabaghban'
password = 'poriabaghban'
user, _ = User.objects.get_or_create(username=username, defaults={'email': 'poriab426@gmail.com'})
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.save()
print('Admin credentials updated successfully!')
