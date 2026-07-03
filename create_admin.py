import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pouriabaghban3.settings')
django.setup()

from django.contrib.auth.models import User

username = 'poriabaghban'
password = 'poriabaghban'
email = 'poriab426@gmail.com'

user, created = User.objects.get_or_create(username=username, defaults={'email': email})
user.email = email
user.set_password(password)
user.is_superuser = True
user.is_staff = True
user.is_active = True
user.save()

print(f"Admin user '{username}' {'created' if created else 'updated'} successfully.")
