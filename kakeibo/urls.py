# kakeibo/urls.py
from django.urls import path
from . import views

app_name = 'kakeibo'

urlpatterns = [
    path('', views.list_view, name='home'),
    path('add/', views.add_view, name='add'),
    path('list/', views.list_view, name='list'),
    path('filter/', views.filter_view, name='filter'),
    path('edit/<int:pk>/', views.edit_view, name='edit'),
    path('delete/<int:pk>/', views.delete_view, name='delete'),
    path('chart/', views.chart_view, name='chart'),
    path('category/', views.category_view, name='category'),
    path('category/add/<str:transaction_type>/',
         views.category_create_view, name='category_add'),
    path('category/edit/<int:pk>/',
         views.category_edit_view, name='category_edit'),
    path('category/delete/<int:pk>/',
         views.category_delete, name='category_delete'),
    path('payment-method/add/',
         views.payment_method_create_view, name='payment_method_add'),
    path('payment-method/edit/<int:pk>/',
         views.payment_method_edit_view, name='payment_method_edit'),
    path('payment-method/delete/<int:pk>/',
         views.payment_method_delete, name='payment_method_delete'),
    path('balance/add/', views.balance_create_view, name='balance_add'),
    path('balance/edit/<int:pk>/', views.balance_edit_view, name='balance_edit'),
    path('balance/delete/<int:pk>/',
         views.balance_delete_view, name='balance_delete'),
    path('api/categories/', views.get_categories, name='get_categories'),
]
