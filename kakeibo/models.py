# kakeibo/models.py
from django.db import models


class Category(models.Model):
    TYPE_CHOICES = [
        ('income', '収入'),
        ('expense', '支出'),
    ]
    name = models.CharField(max_length=50)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class AccountBalance(models.Model):
    payment_method = models.OneToOneField(
        PaymentMethod, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.payment_method} {self.balance}円'


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('income', '収入'),
        ('expense', '支出'),
    ]

    date = models.DateField()
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)
    income_source = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='income_transactions',
    )
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()
    memo = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    @property
    def effective_payment_method(self):
        if self.transaction_type == 'income':
            return self.income_source
        return self.payment_method

    @property
    def effective_payment_method_name(self):
        payment_method = self.effective_payment_method
        return payment_method.name if payment_method else ''

    def __str__(self):
        payment_method_name = self.effective_payment_method_name
        if payment_method_name:
            return f"{self.date} {self.category} {payment_method_name} {self.amount}円"
        return f"{self.date} {self.category} {self.amount}円"
