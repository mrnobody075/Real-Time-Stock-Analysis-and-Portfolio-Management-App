from django import forms
from .models import Wishlist, Stock

class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['name']

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['name', 'symbol']