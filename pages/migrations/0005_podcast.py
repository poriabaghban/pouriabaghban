# Generated manually for podcast URL management

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_skill_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Podcast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(verbose_name='آدرس پادکست')),
            ],
            options={
                'verbose_name': 'پادکست',
                'verbose_name_plural': 'پادکست‌ها',
            },
        ),
    ]