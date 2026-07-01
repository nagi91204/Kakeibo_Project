# Generated manually to store account balances.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0004_paymentmethod_transaction_payment_method'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.IntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('payment_method', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE, to='kakeibo.paymentmethod')),
            ],
        ),
    ]
