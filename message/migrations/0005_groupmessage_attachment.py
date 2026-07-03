from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('message', '0004_groupmessage_recipients_read_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmessage',
            name='content',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='groupmessage',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='chat_attachments/%Y/%m/', verbose_name='پیوست'),
        ),
        migrations.AlterField(
            model_name='groupmessage',
            name='message_type',
            field=models.CharField(choices=[('text', 'متن'), ('sticker', 'استیکر'), ('file', 'فایل')], default='text', max_length=20),
        ),
    ]
