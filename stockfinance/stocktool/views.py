import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import yfinance as yf


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


def stock_detail_view(request, symbol):
    symbol = symbol.upper()

    # Adjust Indian stock symbols (e.g., INFY -> INFY.NS)
    if not symbol.endswith(('.NS', '.BO')) and len(symbol) <= 5:
        test_symbol = symbol + ".NS"
        try:
            test_info = yf.Ticker(test_symbol).info
            if test_info.get("regularMarketPrice") is not None:
                symbol = test_symbol
        except Exception:
            pass  # Fallback to original symbol if .NS doesn't work

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

    try:
        # Fetch quarterly financials
        quarterly_financials = stock.quarterly_financials

        # Extract annual and quarterly revenue and income data
        revenue_annual = income_statement.loc['Total Revenue'] if 'Total Revenue' in income_statement.index else None
        income_annual = income_statement.loc['Net Income'] if 'Net Income' in income_statement.index else None

        revenue_quarterly = quarterly_financials.loc['Total Revenue'] if 'Total Revenue' in quarterly_financials.index else None
        income_quarterly = quarterly_financials.loc['Net Income'] if 'Net Income' in quarterly_financials.index else None

        # Directory to save graphs
        graph_dir = "static/stocktool/graphs"
        os.makedirs(graph_dir, exist_ok=True)

        # Generate yearly revenue and income graph
        if revenue_annual is not None and income_annual is not None:
            plt.figure(figsize=(8, 6))
            plt.bar(revenue_annual.index, revenue_annual.values / 1e9, label="Revenue (Billion)", alpha=0.7)
            plt.bar(income_annual.index, income_annual.values / 1e9, label="Income (Billion)", alpha=0.7)
            plt.title(f"Yearly Revenue and Income - {symbol}")
            plt.xlabel("Year")
            plt.ylabel("Amount (in Billion)")
            plt.legend()
            annual_graph_path = os.path.join(graph_dir, f"{symbol}_annual.png")
            plt.savefig(annual_graph_path)
            plt.close()
        else:
            annual_graph_path = None

        # Generate quarterly revenue and income graph
        if revenue_quarterly is not None and income_quarterly is not None:
            plt.figure(figsize=(8, 6))
            plt.bar(revenue_quarterly.index, revenue_quarterly.values / 1e9, label="Revenue (Billion)", alpha=0.7)
            plt.bar(income_quarterly.index, income_quarterly.values / 1e9, label="Income (Billion)", alpha=0.7)
            plt.title(f"Quarterly Revenue and Income - {symbol}")
            plt.xlabel("Quarter")
            plt.ylabel("Amount (in Billion)")
            plt.legend()
            quarterly_graph_path = os.path.join(graph_dir, f"{symbol}_quarterly.png")
            plt.savefig(quarterly_graph_path)
            plt.close()
        else:
            quarterly_graph_path = None

    except Exception as e:
        print(f"Error generating graphs: {e}")
        annual_graph_path = None
        quarterly_graph_path = None

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
        'annual_graph': annual_graph_path,
        'quarterly_graph': quarterly_graph_path,
    }

    return render(request, 'stocktool/stock_detail.html', context)