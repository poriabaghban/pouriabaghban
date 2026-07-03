#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pouriabaghban3.settings')
django.setup()

from pages.models import Testimonial

count = Testimonial.objects.count()
published = Testimonial.objects.filter(is_published=True).count()

print(f'تعداد کل نظرات: {count}')
print(f'نظرات منتشر شده: {published}')
print('\nفهرست نظرات منتشر شده:')
for t in Testimonial.objects.filter(is_published=True).order_by('order'):
    print(f'  - ID {t.id}: {t.name} | {t.message[:50]}...')
