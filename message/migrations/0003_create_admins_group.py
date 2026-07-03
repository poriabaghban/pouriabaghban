from django.db import migrations


ADMINS_GROUP_NAME = '\u0645\u062f\u06cc\u0631\u0627\u0646'


def create_admins_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name=ADMINS_GROUP_NAME)


def remove_admins_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name=ADMINS_GROUP_NAME).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('message', '0002_groupmessage_message_type'),
    ]

    operations = [
        migrations.RunPython(create_admins_group, remove_admins_group),
    ]