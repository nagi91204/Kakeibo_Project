# kakeibo/forms.py
from django import forms
from .models import Transaction, Category, PaymentMethod, AccountBalance


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['transaction_type', 'name']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'カテゴリ名を入力'
            }),
        }
        labels = {
            'transaction_type': '種別',
            'name': 'カテゴリ名',
        }


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例: 現金、カード、PayPay'
            }),
        }
        labels = {
            'name': '支払い方法',
        }


class AccountBalanceForm(forms.ModelForm):
    class Meta:
        model = AccountBalance
        fields = ['payment_method', 'balance']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '例: 50000',
            }),
        }
        labels = {
            'payment_method': '支払い元',
            'balance': '残高（円）',
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'transaction_type', 'category',
                  'payment_method', 'amount', 'memo']
        widgets = {

            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_transaction_type'}),
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'id_category'}),
            'payment_method': forms.Select(attrs={'id': 'id_payment_method', 'class': 'form-select', 'data-row-id': 'payment-method-row'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '金額を入力'}),
            'memo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'メモ（任意）'}),
        }
        labels = {
            'date': '日付',
            'transaction_type': '種別',
            'category': 'カテゴリ',
            'payment_method': '支払い方法',
            'amount': '金額（円）',
            'memo': 'メモ',
        }
