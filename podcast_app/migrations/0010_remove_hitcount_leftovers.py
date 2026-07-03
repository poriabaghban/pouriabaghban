from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("podcast_app", "0009_podcast_views"),
    ]

    operations = [
        migrations.RunSQL(
            sql="DELETE FROM django_migrations WHERE app = 'hitcount'",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS hitcount_hit_count",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS hitcount_blacklist_ip",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS hitcount_blacklist_user_agent",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
