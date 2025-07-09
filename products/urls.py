# products/urls.py
from django.urls import path
from .views import ProductListView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from products.models import Product

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),

]
""" 
urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('create/', ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
]
 """
