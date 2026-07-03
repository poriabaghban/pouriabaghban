# Generated manually for admin group chat delivery and read receipts.

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('message', '0003_create_admins_group'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='groupmessage',
            name='read_by',
            field=models.ManyToManyField(
                blank=True,
                related_name='read_group_messages',
                to=settings.AUTH_USER_MODEL,
                verbose_name='خوانده شده توسط',
            ),
        ),
        migrations.AddField(
            model_name='groupmessage',
            name='recipients',
            field=models.ManyToManyField(
                blank=True,
                related_name='received_group_messages',
                to=settings.AUTH_USER_MODEL,
                verbose_name='گیرندگان',
            ),
        ),
    ]

