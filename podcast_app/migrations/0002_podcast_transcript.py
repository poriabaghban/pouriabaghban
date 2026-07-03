from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcast_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='podcast',
            name='transcript',
            field=models.TextField(blank=True, verbose_name='\u0645\u062a\u0646 \u067e\u0627\u062f\u06a9\u0633\u062a'),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='description',
            field=models.TextField(verbose_name='\u062a\u0648\u0636\u06cc\u062d\u0627\u062a \u06a9\u0648\u062a\u0627\u0647'),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='duration',
            field=models.CharField(blank=True, max_length=20, verbose_name='\u0645\u062f\u062a \u0632\u0645\u0627\u0646'),
        ),
    ]
