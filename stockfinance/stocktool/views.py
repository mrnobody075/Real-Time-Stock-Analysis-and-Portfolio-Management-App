import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.io as pio
from django.utils.timezone import now
from .utils.finance_charts import balance_sheet_graph, income_graph, generate_price_chart
from .utils.sumofportfolio import convert_to_inr, cost_of_portfolio, unrealised_profit
from .models import StockPortfolio
from .forms import StockPortfolioForm

def get_portfolio_summary(user):
    portfolio = StockPortfolio.objects.filter(user=user)
    total_cost = 0
    total_current_value = 0
    total_unrealised_profit = 0

    for stock in portfolio:
        cost = cost_of_portfolio(stock.stock_symbol, stock.quantity, stock.bought_price)
        profit = unrealised_profit(stock.stock_symbol, stock.quantity, stock.bought_price)

        total_cost += cost
        if profit is not None:
            total_unrealised_profit += profit
            total_current_value += (cost + profit)

    return {
        'total_cost': round(total_cost, 2),
        'total_current_value': round(total_current_value, 2),
        'unrealised_profit': round(total_unrealised_profit, 2),
    }


@login_required
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

@login_required
def stock_redirect_view(request):
    symbol = request.GET.get('query')
    if symbol:
        return redirect('stocktool:stock_detail', symbol=symbol.upper())
    return redirect('stocktool:home')

def fetch_stock_news(symbol):
    API_KEY = settings.NEWS_API_KEY
    NEWS_API_URL = f"https://newsapi.org/v2/everything?q={symbol}+stock&apiKey={API_KEY}"

    try:
        response = requests.get(NEWS_API_URL)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        news_data = response.json()
          # Debug log

        # Limit the articles to 5
        articles = [
            {
                "title": article["title"],
                "source": article["source"]["name"],
                "url": article["url"],
                "published_at": article["publishedAt"],
                "description": article["description"],
            }
            for article in news_data.get("articles", [])[:5]  # Limit to 5 articles
        ]

        return articles
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []
@login_required
def stock_detail_view(request, symbol):
    symbol = symbol.upper()
    news_articles = fetch_stock_news(symbol)

    # Adjust Indian stock symbols (e.g., INFY -> INFY.NS)
    if not symbol.endswith(('.NS', '.BO')) and len(symbol) <= 10:
        test_symbol = symbol + ".NS"
        try:
            test_info = yf.Ticker(test_symbol).info
            if test_info.get("regularMarketPrice") is not None:
                symbol = test_symbol
        except Exception:
            pass  # Fallback to original symbol if .NS doesn't work
    print(symbol)

    stock = yf.Ticker(symbol)

    try:
        # Fetch stock info
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
        currency_symbol = CURRENCY_SYMBOLS.get(currency, currency)  # Fallback to currency code
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

        # Fetch financials, balance sheet, and cash flow
        income_statement = stock.financials
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow

        # Extract specific financial data
        TotalRevenue = income_statement.loc['Total Revenue'].iloc[0] if 'Total Revenue' in income_statement.index else None
        OperatingExpense = income_statement.loc['Operating Expense'].iloc[0] if 'Operating Expense' in income_statement.index else None
        NetIncome = income_statement.loc['Net Income'].iloc[0] if 'Net Income' in income_statement.index else None
        RnD = income_statement.loc['Research And Development'].iloc[0] if 'Research And Development' in income_statement.index else None
        GrossProfit = income_statement.loc['Gross Profit'].iloc[0] if 'Gross Profit' in income_statement.index else None
        OperatingIncome = income_statement.loc['EBIT'].iloc[0] if 'EBIT' in income_statement.index else None
        EPS = income_statement.loc['Diluted EPS'].iloc[0] if 'Diluted EPS' in income_statement.index else None

        TotalAssets = balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in balance_sheet.index else None
        TotalLiabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[0] if 'Total Liabilities Net Minority Interest' in balance_sheet.index else None
        equity = balance_sheet.loc['Total Equity Gross Minority Interest'].iloc[0] if 'Total Equity Gross Minority Interest' in balance_sheet.index else None

        # Calculate derived metrics
        netProfitMargin = (NetIncome / TotalRevenue) * 100 if TotalRevenue and NetIncome else None
        ROE = (NetIncome / equity) * 100 if equity and NetIncome else None

        NetCash = cash_flow.loc['Changes In Cash'].iloc[0] if 'Changes In Cash' in cash_flow.index else None
        FreeCashFlow = cash_flow.loc['Free Cash Flow'].iloc[0] if 'Free Cash Flow' in cash_flow.index else None
        CashFromOperations = cash_flow.loc['Operating Cash Flow'].iloc[0] if 'Operating Cash Flow' in cash_flow.index else None
        CashFromInvesting = cash_flow.loc['Investing Cash Flow'].iloc[0] if 'Investing Cash Flow' in cash_flow.index else None
        CashFinancing = cash_flow.loc['Financing Cash Flow'].iloc[0] if 'Financing Cash Flow' in cash_flow.index else None

    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return render(request, 'stocktool/stock_detail.html', {
            'error': f"Could not fetch stock data for {symbol.upper()}."
        })
    quarterly_income_html, annual_income_html = income_graph(stock, symbol)
    quarterly_balance_html, annual_balance_html = balance_sheet_graph(stock, symbol)
    previous_close = info.get("previousClose")
    # Validate that both current_price and previous_close are not None
    if current_price is not None and previous_close is not None:
        price_change = round(current_price - previous_close, 2)
        percent_change = round((price_change / previous_close) * 100, 2)
    else:
        price_change = None
        percent_change = None
    try:
        history_data = stock.history(period='1d')
        if not history_data.empty:  # Check if the DataFrame is not empty
            last_updated = history_data.index[-1].strftime("%b %d, %I:%M:%S %p %Z")
        else:
            last_updated = "No data available for the last trading day."
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        last_updated = "Error fetching last updated time."
    charts = {
        "1D": generate_price_chart(stock, symbol, "1d", "1m", "1 Day"),
        "5D": generate_price_chart(stock, symbol, "5d", "5m", "5 Days"),
        "1M": generate_price_chart(stock, symbol, "1mo", "30m", "1 Month"),
        "6M": generate_price_chart(stock, symbol, "6mo", "1d", "6 Months"),
        "1Y": generate_price_chart(stock, symbol, "1y", "1d", "1 Year"),
        "5Y": generate_price_chart(stock, symbol, "5y", "1wk", "5 Years"),
        "MAX": generate_price_chart(stock, symbol, "max", "1mo", "Max"),
    }


    # Context to render template
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
        'day_range': f"{info.get('dayLow')} - {info.get('dayHigh')}" if info.get("dayLow") and info.get("dayHigh") else None,
        'year_range': f"{info.get('fiftyTwoWeekLow')} - {info.get('fiftyTwoWeekHigh')}" if info.get("fiftyTwoWeekLow") and info.get("fiftyTwoWeekHigh") else None,
        'market_cap': info.get("marketCap"),
        'avg_volume': info.get("averageVolume"),
        'pe_ratio': info.get("trailingPE"),
        'dividend_yield': info.get("dividendYield"),
        'primary_exchange': exchange,
        'TotalRevenue': TotalRevenue,
        'OperatingExpense': OperatingExpense,
        'NetIncome': NetIncome,
        'RnD': RnD,
        'GrossProfit': GrossProfit,
        'OperatingIncome': OperatingIncome,
        'EPS': EPS,
        'TotalAssets': TotalAssets,
        'TotalLiabilities': TotalLiabilities,
        'equity': equity,
        'netProfitMargin': netProfitMargin,
        'ROE': ROE,
        'NetCash': NetCash,
        'FreeCashFlow': FreeCashFlow,
        'CashOps': CashFromOperations,
        'CashInvesting': CashFromInvesting,
        'CashFinancing': CashFinancing,
        'quarterly_income_html': quarterly_income_html,
        'annual_income_html': annual_income_html,
        'quarterly_balance_html':quarterly_balance_html,
        'annual_balance_html': annual_balance_html,
        'price_change': price_change,
        'percent_change': percent_change,
        'last_updated' : last_updated,
        "charts": charts,
        'news_articles': news_articles,

    }

    return render(request, 'stocktool/stock_detail.html', context)



@login_required
def manage_portfolio(request):
    error = None
    if request.method == 'POST':
        if 'add_stock' in request.POST:
            form = StockPortfolioForm(request.POST)
            if form.is_valid():
                stock_symbol = form.cleaned_data['stock_symbol'].upper()
                quantity = form.cleaned_data['quantity']

                # Check if it's a valid stock symbol (add .NS for Indian stocks)
                if not stock_symbol.endswith(('.NS', '.BO')) and len(stock_symbol) <= 10:
                    test_symbol = stock_symbol + ".NS"
                    try:
                        test_info = yf.Ticker(test_symbol).info
                        if test_info.get("regularMarketPrice") is not None:
                            stock_symbol = test_symbol
                    except Exception:
                        pass

                ticker = yf.Ticker(stock_symbol)
                price = ticker.info.get('regularMarketPrice')

                if price is None:
                    error = f'Could not retrieve price for stock symbol {stock_symbol}.'
                else:
                    StockPortfolio.objects.create(
                        user=request.user,
                        stock_symbol=stock_symbol,
                        quantity=quantity,
                        bought_price=price,
                        date_of_purchase=now().date()
                    )
                    return redirect('stocktool:manage_portfolio')

        elif 'delete_stock' in request.POST:
            stock_id = request.POST.get('stock_id')
            StockPortfolio.objects.filter(id=stock_id, user=request.user).delete()
            return redirect('stocktool:manage_portfolio')

    else:
        form = StockPortfolioForm()

    # Get portfolio and calculate summary
    summary = get_portfolio_summary(request.user)

    context = {
        'form': form,
        'portfolio': StockPortfolio.objects.filter(user=request.user),
        'error': error,
        **summary
    }

    return render(request, 'stocktool/manage_portfolio.html', context)

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

    # Get portfolio summary
    summary = get_portfolio_summary(request.user)

    return render(request, 'stocktool/home.html', {
        'articles': articles,
        **summary
    })

