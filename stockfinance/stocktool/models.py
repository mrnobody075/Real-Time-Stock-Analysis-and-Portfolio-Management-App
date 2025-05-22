from django.db import models
from django.contrib.auth.models import User

class StockPortfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stock_portfolios")
    stock_symbol = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField()
    bought_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_of_purchase = models.DateField()

    def __str__(self):
        return f"{self.stock_symbol} - {self.user.username}"