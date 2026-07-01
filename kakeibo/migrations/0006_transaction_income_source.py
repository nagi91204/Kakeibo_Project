# Generated manually to add an income source field.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0005_accountbalance'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='income_source',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='income_transactions',
                to='kakeibo.paymentmethod',
            ),
        ),
    ]
