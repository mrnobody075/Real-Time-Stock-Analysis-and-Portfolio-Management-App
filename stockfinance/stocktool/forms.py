from django import forms

class StockPortfolioForm(forms.Form):
    stock_symbol = forms.CharField(max_length=10)
    quantity = forms.IntegerField(min_value=1)