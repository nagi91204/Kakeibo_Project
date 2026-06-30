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


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('income', '収入'),
        ('expense', '支出'),
    ]

    date = models.DateField()
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()
    memo = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        payment_method = self.payment_method or '未設定'
        return f"{self.date} {self.category} {payment_method} {self.amount}円"
