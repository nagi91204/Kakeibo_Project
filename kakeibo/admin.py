from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'transaction_type', 'category', 'amount', 'memo']
    list_filter = ['transaction_type', 'category']

    # admin@admin.com
    # admin@admin
