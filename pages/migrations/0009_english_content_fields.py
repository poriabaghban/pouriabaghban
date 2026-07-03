from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0008_bilingual_content_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="footersettings",
            name="copyright_text_en",
            field=models.CharField(blank=True, max_length=200, verbose_name="Copyright text (English)"),
        ),
        migrations.AddField(
            model_name="footersettings",
            name="description_en",
            field=models.TextField(blank=True, verbose_name="Footer description (English)"),
        ),
        migrations.AddField(
            model_name="navbaritem",
            name="title_en",
            field=models.CharField(blank=True, max_length=80, verbose_name="Title (English)"),
        ),
        migrations.AddField(
            model_name="pagecontent",
            name="content_en",
            field=models.TextField(blank=True, verbose_name="Page content (English)"),
        ),
        migrations.AddField(
            model_name="pagecontent",
            name="title_en",
            field=models.CharField(blank=True, max_length=200, verbose_name="Page title (English)"),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="button_text_en",
            field=models.CharField(blank=True, max_length=100, verbose_name="Button text (English)"),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="description_en",
            field=models.TextField(blank=True, verbose_name="Description (English)"),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="text_field_1_en",
            field=models.TextField(blank=True, verbose_name="Text 1 (English)"),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="title_en",
            field=models.CharField(blank=True, max_length=200, verbose_name="Title (English)"),
        ),
    ]
