from django.urls import path
from . import views
app_name = 'wishlistapp'
urlpatterns = [
    path('', views.wishlist_list_and_create, name='wishlist_list_and_create'),
    path('<int:pk>/', views.wishlist_detail, name='wishlist_detail'),
    path('<int:wishlist_id>/stocks/add/', views.stock_add, name='stock_add'),
    path('wishlist/<int:wishlist_id>/stocks/<int:stock_id>/delete/', views.stock_delete, name='stock_delete'),
    path('<int:wishlist_id>/delete/', views.wishlist_delete, name='wishlist_delete'),

]