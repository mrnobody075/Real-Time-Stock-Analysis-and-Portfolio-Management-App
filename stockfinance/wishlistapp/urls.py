from django.urls import path
from . import views

urlpatterns = [
    path('', views.wishlist_list, name='wishlist_list'),
    path('new/', views.wishlist_create, name='wishlist_create'),
    path('<int:pk>/', views.wishlist_detail, name='wishlist_detail'),
    path('<int:wishlist_id>/stocks/add/', views.stock_add, name='stock_add'),
    path('wishlist/<int:wishlist_id>/stocks/<int:stock_id>/delete/', views.stock_delete, name='stock_delete'),


]