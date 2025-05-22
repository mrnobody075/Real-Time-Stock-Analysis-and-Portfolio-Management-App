import yfinance as yf

def unrealised_profit(symbol, quantity, bought_price):
    stock = yf.Ticker(symbol)
    info = stock.info
    current_price = info.get('regularMarketPrice')

    if current_price is None:
        return None  # or raise an error or return 0

    profit = quantity * (current_price - float(bought_price))
    return profit

def cost_of_portfolio(symbol, quantity, bought_price):
    total_cost = quantity * float(bought_price)
    return total_cost
import yfinance as yf

def convert_to_inr(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info

    price = info.get('regularMarketPrice')
    currency = info.get('currency')

    if price is None or currency is None:
        return None  # Could not fetch price or currency

    if currency == "INR":
        return price  # Already in INR

    try:
        # Construct exchange ticker like USDINR=X
        fx_ticker = yf.Ticker(f"{currency}INR=X")
        exchange_rate = fx_ticker.info.get('regularMarketPrice')

        if exchange_rate is None:
            return None  # Could not fetch exchange rate

        price_in_inr = price * exchange_rate
        return price_in_inr

    except Exception as e:
        print("Error during currency conversion:", e)
        return None
