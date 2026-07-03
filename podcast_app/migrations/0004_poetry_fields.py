from django.db import migrations, models

import podcast_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('podcast_app', '0003_alter_podcast_cover_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='podcast',
            options={'ordering': ['-created_at'], 'verbose_name': '\u0634\u0639\u0631', 'verbose_name_plural': '\u0634\u0639\u0631\u0647\u0627'},
        ),
        migrations.AlterField(
            model_name='podcast',
            name='audio_file',
            field=models.FileField(blank=True, null=True, storage=podcast_app.models.secure_podcast_storage, upload_to='', verbose_name='\u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc \u0627\u062e\u062a\u06cc\u0627\u0631\u06cc'),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='podcast_covers/', verbose_name='\u0639\u06a9\u0633'),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='duration',
            field=models.CharField(blank=True, max_length=20, verbose_name='\u0645\u062f\u062a \u0632\u0645\u0627\u0646 \u0627\u062e\u062a\u06cc\u0627\u0631\u06cc'),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='speaker',
            field=models.CharField(max_length=100, verbose_name='\u0634\u0627\u0639\u0631 / \u0646\u0648\u06cc\u0633\u0646\u062f\u0647'),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='transcript',
            field=models.TextField(blank=True, verbose_name='\u0645\u062a\u0646 \u0634\u0639\u0631'),
        ),
    ]
