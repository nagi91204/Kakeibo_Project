# kakeibo/forms.py
from django import forms
from .models import Transaction, Category


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


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'transaction_type', 'category', 'amount', 'memo']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_transaction_type'}),
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'id_category'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '金額を入力'}),
            'memo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'メモ（任意）'}),
        }
        labels = {
            'date': '日付',
            'transaction_type': '種別',
            'category': 'カテゴリ',
            'amount': '金額（円）',
            'memo': 'メモ',
        }
