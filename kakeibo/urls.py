# kakeibo/urls.py
from django.urls import path
from . import views

app_name = 'kakeibo'

urlpatterns = [
    path('', views.list_view, name='home'),
    path('add/', views.add_view, name='add'),
    path('list/', views.list_view, name='list'),
    path('edit/<int:pk>/', views.edit_view, name='edit'),
    path('delete/<int:pk>/', views.delete_view, name='delete'),
    path('chart/', views.chart_view, name='chart'),
    path('category/', views.category_view, name='category'),
    path('category/delete/<int:pk>/',
         views.category_delete, name='category_delete'),
    path('payment-method/delete/<int:pk>/',
         views.payment_method_delete, name='payment_method_delete'),
    path('api/categories/', views.get_categories, name='get_categories'),
]
