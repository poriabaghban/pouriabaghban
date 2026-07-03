import hashlib
from pathlib import Path

from django.conf import settings
from django.db import migrations, models


def hash_existing_audio_files(apps, schema_editor):
    Podcast = apps.get_model("podcast_app", "Podcast")
    protected_podcast_dir = Path(settings.BASE_DIR) / "protected_media" / "podcasts"

    for podcast in Podcast.objects.exclude(audio_file=""):
        if not podcast.audio_file:
            continue

        file_path = protected_podcast_dir / str(podcast.audio_file)
        if not file_path.exists() or not file_path.is_file():
            continue

        digest = hashlib.sha256()
        with file_path.open("rb") as audio_file:
            for chunk in iter(lambda: audio_file.read(1024 * 1024), b""):
                digest.update(chunk)

        Podcast.objects.filter(pk=podcast.pk).update(audio_file_sha256=digest.hexdigest())


def clear_audio_hashes(apps, schema_editor):
    Podcast = apps.get_model("podcast_app", "Podcast")
    Podcast.objects.update(audio_file_sha256="")


class Migration(migrations.Migration):

    dependencies = [
        ("podcast_app", "0005_alter_podcast_options_alter_podcast_audio_file_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="podcast",
            name="audio_file_sha256",
            field=models.CharField(
                blank=True,
                db_index=True,
                editable=False,
                max_length=64,
                verbose_name="\u0627\u062b\u0631 \u0627\u0646\u06af\u0634\u062a \u0641\u0627\u06cc\u0644 \u0635\u0648\u062a\u06cc",
            ),
        ),
        migrations.RunPython(hash_existing_audio_files, clear_audio_hashes),
    ]

