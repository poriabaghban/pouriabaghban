from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("podcast_app", "0006_podcast_audio_file_sha256"),
    ]

    operations = [
        migrations.AddField(
            model_name="podcast",
            name="content_type",
            field=models.CharField(
                choices=[
                    ("regular", "\u067e\u0627\u062f\u06a9\u0633\u062a"),
                    ("special", "\u0634\u0639\u0631 \u0648\u06cc\u0698\u0647"),
                ],
                db_index=True,
                default="regular",
                max_length=20,
                verbose_name="\u0646\u0648\u0639 \u0645\u062d\u062a\u0648\u0627",
            ),
        ),
        migrations.CreateModel(
            name="SpecialPoem",
            fields=[],
            options={
                "verbose_name": "\u0634\u0639\u0631 \u0648\u06cc\u0698\u0647",
                "verbose_name_plural": "\u0634\u0639\u0631 \u0648\u06cc\u0698\u0647",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("podcast_app.podcast",),
        ),
    ]
