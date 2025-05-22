import matplotlib.pyplot as plt
import io
import base64
import yfinance as yf

def get_financial_data_charts(symbol):
    stock = yf.Ticker(symbol)

    try:
        financials = stock.financials
        balance = stock.balance_sheet
        cashflow = stock.cashflow

        def get_value_safe(df, label):
            return df.loc[label].iloc[0] if label in df.index else None

        # Income Statement
        TotalRevenue = get_value_safe(financials, 'Total Revenue')
        NetIncome = get_value_safe(financials, 'Net Income')
        OperatingExpense = get_value_safe(financials, 'Operating Expense')
        RnD = get_value_safe(financials, 'Research and Development')
        GrossProfit = get_value_safe(financials, 'Gross Profit')
        EPS = get_value_safe(financials, 'Diluted EPS')
        EBIT = get_value_safe(financials, 'EBIT')
        netProfitMargin = (NetIncome / TotalRevenue * 100) if TotalRevenue else None

        # Balance Sheet
        equity = get_value_safe(balance, 'Total Equity Gross Minority Interest')
        ROE = (NetIncome / equity * 100) if equity else None
        total_assets = get_value_safe(balance, 'Total Assets')
        total_liabilities = get_value_safe(balance, 'Total Liabilities Net Minority Interest')

        # Cash Flow
        free_cash_flow = get_value_safe(cashflow, 'Free Cash Flow')
        operating_cash_flow = get_value_safe(cashflow, 'Operating Cash Flow')
        capital_expenditure = get_value_safe(cashflow, 'Capital Expenditure')

        def plot_chart(labels, values, title):
            fig, ax = plt.subplots()
            ax.bar(labels, values, color='skyblue')
            ax.set_title(title)
            ax.set_ylabel('Amount')
            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode('utf-8')

        income_chart = plot_chart(
            ['Revenue', 'Operating Exp', 'Gross Profit', 'Net Income'],
            [TotalRevenue, OperatingExpense, GrossProfit, NetIncome],
            'Income Statement'
        )

        balance_chart = plot_chart(
            ['Total Assets', 'Total Liabilities', 'Equity'],
            [total_assets, total_liabilities, equity],
            'Balance Sheet'
        )

        cashflow_chart = plot_chart(
            ['Operating Cash Flow', 'CapEx', 'Free Cash Flow'],
            [operating_cash_flow, capital_expenditure, free_cash_flow],
            'Cash Flow'
        )

        return {
            'TotalRevenue': TotalRevenue,
            'OperatingExpense': OperatingExpense,
            'NetIncome': NetIncome,
            'RnD': RnD,
            'GrossProfit': GrossProfit,
            'EPS': EPS,
            'EBIT': EBIT,
            'netProfitMargin': netProfitMargin,
            'ROE': ROE,
            'equity': equity,
            'income_chart': income_chart,
            'balance_chart': balance_chart,
            'cashflow_chart': cashflow_chart
        }

    except Exception as e:
        print("Error in get_financial_data_charts:", e)
        return {}
