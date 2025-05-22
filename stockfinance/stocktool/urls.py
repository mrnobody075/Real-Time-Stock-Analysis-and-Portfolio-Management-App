# stocktool/urls.py
from django.urls import path
from . import views
app_name = 'stocktool'
urlpatterns = [
    path('', views.home_view, name='home'),
    path('news/<str:category>/', views.news_view, name='financial_news'),
    path('search/', views.stock_redirect_view, name='stock_redirect'),
    path('search/<str:symbol>/', views.stock_detail_view, name='stock_detail'),
    path('portfolio/', views.manage_portfolio, name='manage_portfolio'),

]
