# Generated manually to seed a Render login user when environment variables are present.

import os

from django.contrib.auth import get_user_model
from django.db import migrations


def create_default_superuser(apps, schema_editor):
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

    if not username or not password:
        return

    User = get_user_model()

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username, email=email, password=password)


class Migration(migrations.Migration):

    dependencies = [
        ("kakeibo", "0002_category_alter_transaction_category"),
    ]

    operations = [
        migrations.RunPython(create_default_superuser,
                             migrations.RunPython.noop),
    ]
