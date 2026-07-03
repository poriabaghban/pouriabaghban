#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pouriabaghban3.settings')
django.setup()

from pages.models import Skill

# حذف مهارت‌های قدیم
Skill.objects.all().delete()

# مهارت‌های جدید
skills_data = [
    {
        'name': 'HTML5',
        'percentage': 95,
        'category': 'Frontend',
        'icon': 'fa-brands fa-html5',
        'order': 1,
    },
    {
        'name': 'CSS3',
        'percentage': 90,
        'category': 'Frontend',
        'icon': 'fa-brands fa-css3-alt',
        'order': 2,
    },
    {
        'name': 'JavaScript',
        'percentage': 92,
        'category': 'Frontend',
        'icon': 'fa-brands fa-js',
        'order': 3,
    },
    {
        'name': 'React',
        'percentage': 85,
        'category': 'Frontend',
        'icon': 'fa-brands fa-react',
        'order': 4,
    },
    {
        'name': 'Python',
        'percentage': 88,
        'category': 'Backend',
        'icon': 'fa-brands fa-python',
        'order': 5,
    },
    {
        'name': 'Django',
        'percentage': 87,
        'category': 'Backend',
        'icon': 'fa-solid fa-code',
        'order': 6,
    },
    {
        'name': 'PostgreSQL',
        'percentage': 83,
        'category': 'Database',
        'icon': 'fa-solid fa-database',
        'order': 7,
    },
    {
        'name': 'Git',
        'percentage': 90,
        'category': 'Tools',
        'icon': 'fa-brands fa-git-alt',
        'order': 8,
    },
    {
        'name': 'Docker',
        'percentage': 80,
        'category': 'DevOps',
        'icon': 'fa-brands fa-docker',
        'order': 9,
    },
    {
        'name': 'Bootstrap',
        'percentage': 92,
        'category': 'Frontend',
        'icon': 'fa-brands fa-bootstrap',
        'order': 10,
    },
]

# اضافه کردن مهارت‌ها
for skill in skills_data:
    Skill.objects.create(**skill)
    print(f'✅ مهارت "{skill["name"]}" اضافه شد')

print('\n✅ تمام مهارت‌ها با موفقیت اضافه شدند!')
