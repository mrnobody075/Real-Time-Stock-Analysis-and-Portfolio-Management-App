from .views import signup_view, home_view
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import profile_view
app_name = 'accounts'
urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('', home_view, name='home'),# 👈 this will be shown after login
    path('profile/', profile_view, name='profile'),
]
