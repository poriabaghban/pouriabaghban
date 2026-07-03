from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0003_bilingual_content_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="content_en",
            field=models.TextField(blank=True, verbose_name="Content (English)"),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="excerpt_en",
            field=models.TextField(blank=True, max_length=500, verbose_name="Excerpt (English)"),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="title_en",
            field=models.CharField(blank=True, max_length=200, verbose_name="Title (English)"),
        ),
    ]
