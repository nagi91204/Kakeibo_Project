from django.contrib import admin
from .models import Transaction, Category, PaymentMethod


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'transaction_type']
    list_filter = ['transaction_type']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'transaction_type',
                    'category', 'payment_method', 'amount', 'memo']
    list_filter = ['transaction_type', 'category', 'payment_method']
