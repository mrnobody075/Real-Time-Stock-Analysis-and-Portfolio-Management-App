from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile

import re

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')  # 👈 New

        if not username or not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect('accounts:signup')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('accounts:signup')

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return redirect('accounts:signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('accounts:signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return redirect('accounts:signup')

        user = User.objects.create_user(username=username, password=password, email=email)
        messages.success(request, "Account created successfully.")
        return redirect('accounts:login')

    return render(request, 'accounts/signup.html')

@login_required
def home_view(request):
    return render(request, 'accounts/home.html')
# accounts/views.py

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.bio = request.POST.get('bio', '')
        profile.save()

    return render(request, 'accounts/profile.html', {'profile': profile})
