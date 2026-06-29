# kakeibo/views.py
from django.contrib.auth.decorators import login_required
import io
import base64
import pandas as pd
from django import forms
from .models import Transaction, Category, PaymentMethod
from .forms import TransactionForm, CategoryForm, PaymentMethodForm
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
plt.rcParams['font.family'] = 'Hiragino Sans'


def build_transaction_filter_context(request):
    transactions = Transaction.objects.select_related(
        'category', 'payment_method')

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
            payment_method_id=selected_payment_method)

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

    for t in transactions:
        t.amount_formatted = f'{t.amount:,}'

    return render(request, 'kakeibo/list.html', {
        'transactions': transactions,
        'total_income': f'{total_income:,}',
        'total_expense': f'{total_expense:,}',
        'balance': f'{balance:,}',
        'balance_sign': balance >= 0,
        'types': context['types'],

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

    df = pd.DataFrame(list(transactions.values(
        'date', 'category_id', 'transaction_type', 'amount')))

    # カテゴリ名を取得
    categories = {c.id: c.name for c in Category.objects.all()}
    df['category_name'] = df['category_id'].map(categories)

    charts = {}

    # ① 支出カテゴリ別 円グラフ
    expense_df = df[df['transaction_type'] == 'expense']
    if not expense_df.empty:
        summary = expense_df.groupby('category_name')['amount'].sum()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(summary.values, labels=summary.index,
               autopct='%1.1f%%', startangle=90)
        ax.set_title('支出カテゴリ別割合')
        charts['pie'] = fig_to_base64(fig)

    # ② 月別収支 棒グラフ
    df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
    monthly_income = df[df['transaction_type'] == 'income'].groupby('month')[
        'amount'].sum()
    monthly_expense = df[df['transaction_type'] == 'expense'].groupby('month')[
        'amount'].sum()
    months = sorted(set(monthly_income.index) | set(monthly_expense.index))

    fig, ax = plt.subplots(figsize=(8, 4))
    x = range(len(months))
    ax.bar([i - 0.2 for i in x], [monthly_income.get(m, 0)
           for m in months], width=0.4, label='収入', color='steelblue')
    ax.bar([i + 0.2 for i in x], [monthly_expense.get(m, 0)
           for m in months], width=0.4, label='支出', color='salmon')
    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=45)
    ax.set_title('月別収支')
    ax.legend()
    plt.tight_layout()
    charts['bar'] = fig_to_base64(fig)

    if not expense_df.empty:
        cat_summary = expense_df.groupby('category_name')[
            'amount'].sum().reset_index()
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.barplot(data=cat_summary, x='amount',
                    y='category_name', ax=ax, palette='coolwarm')
        ax.set_title('カテゴリ別支出金額')
        ax.set_xlabel('金額（円）')
        ax.set_ylabel('カテゴリ')
        plt.tight_layout()
        charts['hbar'] = fig_to_base64(fig)

    return render(request, 'kakeibo/chart.html', {'charts': charts})


def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    image = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return image


@login_required
def category_view(request):
    income_categories = Category.objects.filter(transaction_type='income')
    expense_categories = Category.objects.filter(transaction_type='expense')
    payment_methods = PaymentMethod.objects.all()

    return render(request, 'kakeibo/category.html', {
        'income_categories': income_categories,
        'expense_categories': expense_categories,
        'payment_methods': payment_methods,
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
