import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.io as pio


def balance_sheet_graph(stock, symbol):
    # ----- Quarterly -----
    totalassets_series = stock.quarterly_balance_sheet.loc['Total Assets'].T
    tliability_series = stock.quarterly_balance_sheet.loc['Total Liabilities Net Minority Interest'].T

    totalassets_df = totalassets_series.reset_index()
    totalassets_df.columns = ['Quarter', 'Total Assets']

    tliability_df = tliability_series.reset_index()
    tliability_df.columns = ['Quarter', 'Total Liabilities']

    merged_df = pd.merge(totalassets_df, tliability_df, on='Quarter').dropna()

    plot_df = merged_df.melt(id_vars='Quarter', value_vars=['Total Assets', 'Total Liabilities'],
                             var_name='Metric', value_name='Amount')

    fig_quarterly = px.bar(plot_df, x='Quarter', y='Amount', color='Metric',
                           barmode='group', title=f"{symbol} - Quarterly Total Assets vs Total Liabilities")
    quarterly_balance_html = pio.to_html(fig_quarterly, full_html=False)

    # ----- Annual -----
    totalassetsa_series = stock.balance_sheet.loc['Total Assets'].T
    tliabilitya_series = stock.balance_sheet.loc['Total Liabilities Net Minority Interest'].T

    totalassetsa_df = totalassetsa_series.reset_index()
    totalassetsa_df.columns = ['Annual', 'Total Assets']

    tliabilitya_df = tliabilitya_series.reset_index()
    tliabilitya_df.columns = ['Annual', 'Total Liabilities']

    mergeda_df = pd.merge(totalassetsa_df, tliabilitya_df, on='Annual').dropna()

    plota_df = mergeda_df.melt(id_vars='Annual', value_vars=['Total Assets', 'Total Liabilities'],
                               var_name='Metric', value_name='Amount')

    fig_annual_balance = px.bar(plota_df, x='Annual', y='Amount', color='Metric',
                                barmode='group', title=f"{symbol} - Annual Total Assets vs Total Liabilities")
    annual_balance_html = pio.to_html(fig_annual_balance, full_html=False)

    return quarterly_balance_html, annual_balance_html


def income_graph(stock, symbol):
    # ----- Quarterly -----
    revenue_series = stock.quarterly_financials.loc['Total Revenue'].T
    netIncome_series = stock.quarterly_financials.loc['Net Income'].T

    revenue_df = revenue_series.reset_index()
    revenue_df.columns = ['Quarter', 'Revenue']
    netIncome_df = netIncome_series.reset_index()
    netIncome_df.columns = ['Quarter', 'Net Income']

    merged_df = pd.merge(revenue_df, netIncome_df, on='Quarter').dropna()

    plot_df = merged_df.melt(id_vars='Quarter', value_vars=['Revenue', 'Net Income'],
                             var_name='Metric', value_name='Amount')

    fig_quarterly = px.bar(plot_df, x='Quarter', y='Amount', color='Metric',
                           barmode='group', title=f"{symbol} - Quarterly Revenue vs Net Income")
    quarterly_graph_html = pio.to_html(fig_quarterly, full_html=False)

    # ----- Annual -----
    revenue_series_a = stock.financials.loc['Total Revenue'].T
    netIncome_series_a = stock.financials.loc['Net Income'].T

    revenue_df_a = revenue_series_a.reset_index()
    revenue_df_a.columns = ['Annual', 'Revenue']
    netIncome_df_a = netIncome_series_a.reset_index()
    netIncome_df_a.columns = ['Annual', 'Net Income']

    merged_df_a = pd.merge(revenue_df_a, netIncome_df_a, on='Annual').dropna()

    plot_df_a = merged_df_a.melt(id_vars='Annual', value_vars=['Revenue', 'Net Income'],
                                 var_name='Metric', value_name='Amount')

    fig_annual_income = px.bar(plot_df_a, x='Annual', y='Amount', color='Metric',
                               barmode='group', title=f"{symbol} - Yearly Revenue vs Net Income")
    annual_income_graph_html = pio.to_html(fig_annual_income, full_html=False)

    return quarterly_graph_html, annual_income_graph_html
def generate_price_chart(stock, symbol, period, interval, label):
    df = stock.history(period=period, interval=interval).reset_index()

    fig = px.line(df, x='Datetime' if 'Datetime' in df else 'Date', y='Close',
                  title=f"{symbol} Price - {label}",
                  labels={'Datetime': 'Time', 'Date': 'Date', 'Close': 'Price'},
                  template="plotly_white")

    latest_price = df['Close'].iloc[-1]
    prev_close = stock.info.get("previousClose", None)

    if prev_close:
        fig.add_hline(y=prev_close, line_dash="dot", line_color="gray",
                      annotation_text=f"Prev Close ₹{prev_close}", annotation_position="bottom right")

    fig.add_scatter(x=[df.iloc[-1][0]], y=[latest_price],
                    mode='markers+text', marker=dict(color='green', size=10),
                    text=[f"₹{latest_price:.2f}"], textposition='top right')

    return pio.to_html(fig, full_html=False)
