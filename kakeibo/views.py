import matplotlib

matplotlib.use("Agg")  # noqa: E402

from matplotlib import pyplot as plt
from matplotlib import font_manager
from collections import defaultdict
import json

from django.contrib.auth.decorators import login_required
import io
import base64
import pandas as pd
from django import forms
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .forms import TransactionForm, CategoryForm, PaymentMethodForm, AccountBalanceForm
from .models import Transaction, Category, PaymentMethod, AccountBalance


def get_keyword_balance(recorded_balances, keywords):
    matched_balances = [
        item.balance
        for item in recorded_balances
        if any(keyword in item.payment_method.name for keyword in keywords)
    ]
    if matched_balances:
        return sum(matched_balances)
    return None


def build_transaction_filter_context(request):
    transactions = Transaction.objects.select_related(
        'category', 'payment_method', 'income_source')

    selected_month = request.GET.get('month', '')
    selected_type = request.GET.get('transaction_type', '')
    selected_category = request.GET.get('category', '')
    selected_payment_method = request.GET.get('payment_method', '')

    if selected_month:
        transactions = transactions.filter(
            date__year=selected_month[:4], date__month=selected_month[5:])
    if selected_type:
        transactions = transactions.filter(transaction_type=selected_type)
    if selected_category and selected_category.isdigit():
        transactions = transactions.filter(category_id=selected_category)
    if selected_payment_method and selected_payment_method.isdigit():
        transactions = transactions.filter(
            Q(payment_method_id=selected_payment_method) |
            Q(income_source_id=selected_payment_method)
        )

    all_months = Transaction.objects.dates('date', 'month', order='DESC')
    months = [m.strftime('%Y-%m') for m in all_months]
    months_with_flag = [
        {'value': m, 'selected': m == selected_month} for m in months]

    if selected_type in ['income', 'expense']:
        categories = Category.objects.filter(transaction_type=selected_type)
    else:
        categories = Category.objects.all()

    categories_with_flag = [{'id': cat.id, 'name': cat.name, 'selected': str(
        cat.id) == selected_category} for cat in categories]

    payment_methods = PaymentMethod.objects.all()
    payment_methods_with_flag = [{
        'id': method.id,
        'name': method.name,
        'selected': str(method.id) == selected_payment_method,
    } for method in payment_methods]

    types_with_flag = [
        {'value': 'income', 'label': '収入', 'selected': selected_type == 'income'},
        {'value': 'expense', 'label': '支出', 'selected': selected_type == 'expense'},
    ]

    return {
        'transactions': transactions,
        'months': months_with_flag,
        'selected_month': selected_month,
        'selected_type': selected_type,
        'selected_category': selected_category,
        'selected_payment_method': selected_payment_method,
        'categories': categories_with_flag,
        'payment_methods': payment_methods_with_flag,
        'types': types_with_flag,
    }


@login_required
def add_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kakeibo:list')
    else:
        form = TransactionForm()

    return render(request, 'kakeibo/add.html', {'form': form})


@login_required
def list_view(request):
    context = build_transaction_filter_context(request)
    transactions = context['transactions']

    total_income = sum(
        t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(
        t.amount for t in transactions if t.transaction_type == 'expense')
    balance = total_income - total_expense

    payment_balance_map = defaultdict(int)
    for transaction in transactions:
        payment_method_name = transaction.effective_payment_method_name
        signed_amount = transaction.amount if transaction.transaction_type == 'income' else -transaction.amount
        payment_balance_map[payment_method_name] += signed_amount

    def balance_for_keywords(keywords):
        return sum(
            amount
            for name, amount in payment_balance_map.items()
            if any(keyword in name for keyword in keywords)
        )

    cash_balance = balance_for_keywords(['現金'])
    bank_balance = balance_for_keywords(['口座', '銀行'])
    paypay_balance = balance_for_keywords(['PayPay', 'paypay', 'ペイペイ'])

    recorded_balances = AccountBalance.objects.select_related('payment_method')
    recorded_cash = get_keyword_balance(recorded_balances, ['現金'])
    recorded_bank = get_keyword_balance(recorded_balances, ['口座', '銀行'])
    recorded_paypay = get_keyword_balance(
        recorded_balances, ['PayPay', 'paypay', 'ペイペイ'])

    if recorded_cash is not None:
        cash_balance = recorded_cash
    if recorded_bank is not None:
        bank_balance = recorded_bank
    if recorded_paypay is not None:
        paypay_balance = recorded_paypay

    for t in transactions:
        t.amount_formatted = f'{t.amount:,}'

    return render(request, 'kakeibo/list.html', {
        'transactions': transactions,
        'total_income': f'{total_income:,}',
        'total_expense': f'{total_expense:,}',
        'balance': f'{balance:,}',
        'balance_sign': balance >= 0,
        'cash_balance': f'{cash_balance:,}',
        'bank_balance': f'{bank_balance:,}',
        'paypay_balance': f'{paypay_balance:,}',
        'types': context['types'],
        'months': context['months'],
        'selected_month': context['selected_month'],
        'selected_type': context['selected_type'],
        'selected_category': context['selected_category'],
        'selected_payment_method': context['selected_payment_method'],
        'categories': context['categories'],
        'payment_methods': context['payment_methods'],

    })


@login_required
def filter_view(request):
    context = build_transaction_filter_context(request)
    transactions = context['transactions']

    for t in transactions:
        t.amount_formatted = f'{t.amount:,}'

    return render(request, 'kakeibo/filter.html', {
        'transactions': transactions,
        'months': context['months'],
        'selected_month': context['selected_month'],
        'selected_type': context['selected_type'],
        'selected_category': context['selected_category'],
        'selected_payment_method': context['selected_payment_method'],
        'categories': context['categories'],
        'payment_methods': context['payment_methods'],
        'types': context['types'],
    })


@login_required
def edit_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('kakeibo:list')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'kakeibo/edit.html', {'form': form, 'transaction': transaction})


@login_required
def delete_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        return redirect('kakeibo:list')
    return render(request, 'kakeibo/delete.html', {'transaction': transaction})


@login_required
def chart_view(request):
    transactions = Transaction.objects.all()

    if not transactions:
        return render(request, 'kakeibo/chart.html', {'error': 'データがありません'})

    monthly_income = defaultdict(int)
    monthly_expense = defaultdict(int)
    expense_category = defaultdict(int)
    payment_method_count = defaultdict(int)
    payment_method_amount = defaultdict(int)

    for transaction in transactions.select_related('category', 'payment_method', 'income_source'):
        month_key = transaction.date.strftime('%Y-%m')
        payment_method_name = transaction.effective_payment_method_name

        if transaction.transaction_type == 'income':
            monthly_income[month_key] += transaction.amount
        else:
            monthly_expense[month_key] += transaction.amount
            category_name = transaction.category.name if transaction.category else '未設定'
            expense_category[category_name] += transaction.amount

        payment_method_count[payment_method_name] += 1
        payment_method_amount[payment_method_name] += transaction.amount

    month_labels = sorted(set(monthly_income.keys()) |
                          set(monthly_expense.keys()))
    category_labels = [name for name, _ in sorted(
        expense_category.items(), key=lambda item: item[1], reverse=True)]
    payment_method_labels = [name for name, _ in sorted(
        payment_method_count.items(), key=lambda item: item[1], reverse=True)]

    payment_balances = []
    for payment_method in PaymentMethod.objects.all():
        method_transactions = transactions.filter(
            Q(payment_method=payment_method) | Q(income_source=payment_method))
        income_total = sum(
            item.amount for item in method_transactions if item.transaction_type == 'income')
        expense_total = sum(
            item.amount for item in method_transactions if item.transaction_type == 'expense')
        payment_balances.append({
            'name': payment_method.name,
            'balance': income_total - expense_total,
        })

    cash_balance = sum(item['balance']
                       for item in payment_balances if '現金' in item['name'])
    bank_balance = sum(item['balance'] for item in payment_balances if any(
        keyword in item['name'] for keyword in ['口座', '銀行']))
    paypay_balance = sum(item['balance'] for item in payment_balances if any(
        keyword in item['name'] for keyword in ['PayPay', 'paypay', 'ペイペイ']))

    recorded_balances = AccountBalance.objects.select_related('payment_method')
    recorded_cash = get_keyword_balance(recorded_balances, ['現金'])
    recorded_bank = get_keyword_balance(recorded_balances, ['口座', '銀行'])
    recorded_paypay = get_keyword_balance(
        recorded_balances, ['PayPay', 'paypay', 'ペイペイ'])

    if recorded_cash is not None:
        cash_balance = recorded_cash
    if recorded_bank is not None:
        bank_balance = recorded_bank
    if recorded_paypay is not None:
        paypay_balance = recorded_paypay

    chart_data = {
        'monthly': {
            'labels': month_labels,
            'income': [monthly_income.get(label, 0) for label in month_labels],
            'expense': [monthly_expense.get(label, 0) for label in month_labels],
        },
        'expense_category': {
            'labels': category_labels,
            'values': [expense_category[label] for label in category_labels],
        },
        'payment_method_count': {
            'labels': payment_method_labels,
            'values': [payment_method_count[label] for label in payment_method_labels],
        },
        'payment_method_amount': {
            'labels': payment_method_labels,
            'values': [payment_method_amount[label] for label in payment_method_labels],
        },
    }

    return render(request, 'kakeibo/chart.html', {
        'chart_data_json': json.dumps(chart_data, ensure_ascii=False),
        'payment_balances': payment_balances,
        'cash_balance': f'{cash_balance:,}',
        'bank_balance': f'{bank_balance:,}',
        'paypay_balance': f'{paypay_balance:,}',
    })


@login_required
def balance_create_view(request):
    if request.method == 'POST':
        form = AccountBalanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kakeibo:category')
    else:
        form = AccountBalanceForm()

    return render(request, 'kakeibo/form_page.html', {
        'form': form,
        'title': '残高を登録',
        'submit_label': '保存する',
        'back_url': 'kakeibo:category',
    })


@login_required
def balance_edit_view(request, pk):
    balance = get_object_or_404(AccountBalance, pk=pk)
    if request.method == 'POST':
        form = AccountBalanceForm(request.POST, instance=balance)
        if form.is_valid():
            form.save()
            return redirect('kakeibo:category')
    else:
        form = AccountBalanceForm(instance=balance)

    return render(request, 'kakeibo/form_page.html', {
        'form': form,
        'title': '残高を編集',
        'submit_label': '更新する',
        'back_url': 'kakeibo:category',
    })


@login_required
def balance_delete_view(request, pk):
    balance = get_object_or_404(AccountBalance, pk=pk)
    if request.method == 'POST':
        balance.delete()
        return redirect('kakeibo:category')
    return render(request, 'kakeibo/balance_delete.html', {'balance': balance})


@login_required
def category_view(request):
    income_categories = Category.objects.filter(transaction_type='income')
    expense_categories = Category.objects.filter(transaction_type='expense')
    payment_methods = PaymentMethod.objects.all()
    account_balances = AccountBalance.objects.select_related(
        'payment_method').order_by('payment_method__name')

    return render(request, 'kakeibo/category.html', {
        'income_categories': income_categories,
        'expense_categories': expense_categories,
        'payment_methods': payment_methods,
        'account_balances': account_balances,
    })


@login_required
def category_create_view(request, transaction_type):
    if transaction_type not in ['income', 'expense']:
        return redirect('kakeibo:category')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.transaction_type = transaction_type
            category.save()
            return redirect('kakeibo:category')
    else:
        form = CategoryForm(initial={'transaction_type': transaction_type})
        form.fields['transaction_type'].widget = forms.HiddenInput()

    return render(request, 'kakeibo/form_page.html', {
        'form': form,
        'title': '収入カテゴリを追加' if transaction_type == 'income' else '支出カテゴリを追加',
        'submit_label': '追加する',
        'back_url': 'kakeibo:category',
    })


@login_required
def category_edit_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('kakeibo:category')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'kakeibo/form_page.html', {
        'form': form,
        'title': 'カテゴリを編集',
        'submit_label': '更新する',
        'back_url': 'kakeibo:category',
    })


@login_required
def payment_method_create_view(request):
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kakeibo:category')
    else:
        form = PaymentMethodForm()

    return render(request, 'kakeibo/form_page.html', {
        'form': form,
        'title': '支払い方法を追加',
        'submit_label': '追加する',
        'back_url': 'kakeibo:category',
    })


@login_required
def payment_method_edit_view(request, pk):
    payment_method = get_object_or_404(PaymentMethod, pk=pk)
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=payment_method)
        if form.is_valid():
            form.save()
            return redirect('kakeibo:category')
    else:
        form = PaymentMethodForm(instance=payment_method)

    return render(request, 'kakeibo/form_page.html', {
        'form': form,
        'title': '支払い方法を編集',
        'submit_label': '更新する',
        'back_url': 'kakeibo:category',
    })


@login_required
def category_delete(request, pk):
    category = Category.objects.get(pk=pk)
    category.delete()
    return redirect('kakeibo:category')


@login_required
def payment_method_delete(request, pk):
    payment_method = PaymentMethod.objects.get(pk=pk)
    payment_method.delete()
    return redirect('kakeibo:category')


@login_required
# 種別に応じてカテゴリを絞り込むAPI
def get_categories(request):
    transaction_type = request.GET.get('type', '')
    if transaction_type in ['income', 'expense']:
        categories = Category.objects.filter(
            transaction_type=transaction_type).values('id', 'name')
    else:
        categories = Category.objects.all().values('id', 'name')
    return JsonResponse(list(categories), safe=False)
