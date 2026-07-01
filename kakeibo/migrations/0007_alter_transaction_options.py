# Generated manually to sync Transaction model options.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0006_transaction_income_source'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['-date', '-created_at']},
        ),
    ]
