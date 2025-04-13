from django.contrib import admin
from .models import Wishlist, Stock

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user']
    search_fields = ['name', 'user__username']

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'symbol', 'wishlist']
    search_fields = ['name', 'symbol', 'wishlist__name']