# Generated manually for separate portfolio management.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PortfolioCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='\u0646\u0627\u0645 \u062f\u0633\u062a\u0647\u200c\u0628\u0646\u062f\u06cc')),
                ('description', models.TextField(blank=True, verbose_name='\u062a\u0648\u0636\u06cc\u062d\u0627\u062a')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='\u062a\u0627\u0631\u06cc\u062e \u0627\u06cc\u062c\u0627\u062f')),
            ],
            options={
                'verbose_name': '\u062f\u0633\u062a\u0647\u200c\u0628\u0646\u062f\u06cc \u0646\u0645\u0648\u0646\u0647 \u06a9\u0627\u0631',
                'verbose_name_plural': '\u062f\u0633\u062a\u0647\u200c\u0628\u0646\u062f\u06cc \u0647\u0627\u06cc \u0646\u0645\u0648\u0646\u0647 \u06a9\u0627\u0631',
            },
        ),
        migrations.CreateModel(
            name='PortfolioItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='\u0639\u0646\u0648\u0627\u0646')),
                ('image', models.ImageField(upload_to='portfolio/', verbose_name='\u062a\u0635\u0648\u06cc\u0631')),
                ('description', models.TextField(blank=True, verbose_name='\u062a\u0648\u0636\u06cc\u062d\u0627\u062a')),
                ('project_url', models.URLField(blank=True, verbose_name='\u0644\u06cc\u0646\u06a9 \u067e\u0631\u0648\u0698\u0647')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='\u062a\u0627\u0631\u06cc\u062e \u0627\u06cc\u062c\u0627\u062f')),
                ('is_featured', models.BooleanField(default=False, verbose_name='\u0628\u0631\u062c\u0633\u062a\u0647')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gallery.portfoliocategory', verbose_name='\u062f\u0633\u062a\u0647\u200c\u0628\u0646\u062f\u06cc')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='\u0622\u067e\u0644\u0648\u062f \u0634\u062f\u0647 \u062a\u0648\u0633\u0637')),
            ],
            options={
                'verbose_name': '\u0646\u0645\u0648\u0646\u0647 \u06a9\u0627\u0631',
                'verbose_name_plural': '\u0646\u0645\u0648\u0646\u0647 \u06a9\u0627\u0631\u0647\u0627',
                'ordering': ['-created_at'],
            },
        ),
    ]
