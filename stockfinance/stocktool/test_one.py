from .models import StockPortfolio

# Fetch all stock records
all_stocks = StockPortfolio.objects.all()

# Example: Loop through and print each stock
for stock in all_stocks:
    print(f"User: {stock.user.username}, Stock: {stock.stock_symbol}, Quantity: {stock.quantity}")