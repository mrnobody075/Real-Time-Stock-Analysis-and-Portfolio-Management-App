# stocktool/views.py
import requests
from django.shortcuts import render
import pprint  # just for better formatting
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import redirect
import yfinance as yf
import matplotlib.pyplot as plt
from django.http import Http404
from datetime import timedelta
from django.utils import timezone
from .models import NewsArticle  # import your model


@login_required
def home_view(request):
    api_key = settings.NEWS_API_KEY


    url = (
        f"https://newsapi.org/v2/everything?"
        f"q=top&language=en&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
    )

    response = requests.get(url)
    data = response.json()
    articles = data.get('articles', [])
    return render(request, 'stocktool/home.html', {'articles': articles})


def news_view(request, category='top'):
    api_key = settings.NEWS_API_KEY

    if category == 'top':
        query = 'finance'
    elif category == 'local':
        query = 'Indian stock market OR Sensex OR Nifty'
    elif category == 'global':
        query = 'global economy OR international markets'
    else:
        query = 'finance'

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&language=en&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
    )

    response = requests.get(url)
    data = response.json()
    articles = data.get('articles', [])

    return render(request, 'stocktool/financial_news.html', {
        'articles': articles,
        'category': category,
    })

def stock_redirect_view(request):
    symbol = request.GET.get('query')
    if symbol:
        return redirect('stock_detail', symbol=symbol.upper())
    return redirect('home')


import yfinance as yf
from django.shortcuts import render


def stock_detail_view(request, symbol):
    symbol = symbol.upper()

    # If it's a common Indian stock symbol (e.g., INFY), try appending .NS
    if not symbol.endswith(('.NS', '.BO')) and len(symbol) <= 5:
        test_symbol = symbol + ".NS"
        try:
            test_info = yf.Ticker(test_symbol).info
            if test_info.get("regularMarketPrice") is not None:
                symbol = test_symbol
        except Exception:
            pass  # fallback to original symbol

    stock = yf.Ticker(symbol)

    try:
        info = stock.info
        current_price = info.get("regularMarketPrice")
        currency = info.get("currency")
        full_name = info.get("longName") or info.get("shortName")
        CURRENCY_SYMBOLS = {
            "USD": "$",
            "INR": "₹",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
        }

        currency_code = info.get("currency")
        currency_symbol = CURRENCY_SYMBOLS.get(currency_code, currency_code)  # fallback to code if unknown
        officers = info.get("companyOfficers")
        ceo = None
        if officers:
            for person in officers:
                if person.get("title") and "CEO" in person["title"]:
                    ceo = person.get("name")
                    break
        EXCHANGE_MAP = {
            "NMS": "NASDAQ",
            "NYQ": "NYSE",
            "NSI": "NSE (India)",
            "BSE": "BSE (India)",
        }
        exchange = EXCHANGE_MAP.get(info.get("exchange"), info.get("exchange"))
        def format_dataframe(df):
            if df is not None and not df.empty:
                df = df.fillna('-')
                return {
                    "columns": [col.strftime("%b %Y") if hasattr(col, 'strftime') else str(col) for col in df.columns],
                    "rows": [
                        {"label": index, "values": [df.at[index, col] for col in df.columns]}
                        for index in df.index
                    ]
                }
            return None

        financials_data = format_dataframe(stock.financials)
        balance_sheet_data = format_dataframe(stock.balance_sheet)
        cashflow_data = format_dataframe(stock.cashflow)
    except Exception as e:
        return render(request, 'stocktool/stock_detail.html', {
            'error': f"Could not fetch stock data for {symbol.upper()}."
        })

    context = {
        'symbol': symbol.upper(),
        'current_price': current_price,
        'currency': currency_symbol,
        'full_name': full_name,
        'exchange': exchange,
        'summary': info.get("longBusinessSummary"),
        'employees': info.get("fullTimeEmployees"),
        'website': info.get("website"),
        'ceo': ceo,
        'previous_close': info.get("previousClose"),
        'day_range': f"{info.get('dayLow')} - {info.get('dayHigh')}" if info.get("dayLow") and info.get(
            "dayHigh") else None,
        'year_range': f"{info.get('fiftyTwoWeekLow')} - {info.get('fiftyTwoWeekHigh')}" if info.get(
            "fiftyTwoWeekLow") and info.get("fiftyTwoWeekHigh") else None,
        'market_cap': info.get("marketCap"),
        'avg_volume': info.get("averageVolume"),
        'pe_ratio': info.get("trailingPE"),
        'dividend_yield': info.get("dividendYield"),
        'primary_exchange': exchange,
        'financials': financials_data,
        'balance_sheet': balance_sheet_data,
        'cash_flow': cashflow_data,
    }

    return render(request, 'stocktool/stock_detail.html', context)

