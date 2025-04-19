import streamlit as st
import requests
import os
import json
import pandas as pd
import google.generativeai as genai
from apikey import FMP_API_KEY, GEMINI_API_KEY

def get_jsonparsed_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return None
def get_financial_statements(ticker, limit, period, statement_type):
    if statement_type == "Income Statement":
        url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    elif statement_type == "Balance Sheet":
        url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    elif statement_type == "Cash Flow":
        url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?period={period}&limit={limit}&apikey={FMP_API_KEY}"
    
    data = get_jsonparsed_data(url)

    if isinstance(data, list) and data:
        return pd.DataFrame(data)
    else:
        st.error("Unable to fetch financial statements. Please ensure the ticker is correct and try again.")
        return pd.DataFrame()

genai.configure(api_key=GEMINI_API_KEY)

def generate_financial_summary(financial_statements, statement_type):
    """
    Generate a summary of financial statements using Gemini, mimicking the GPT-based structure.
    """

    summaries = []
    for i in range(len(financial_statements)):
        date = safe_get('date')
        
        if statement_type == "Income Statement":
            summary = f"""
For the period ending {date}, the company reported the following key income statement metrics:
- Revenue: {safe_get('revenue')}
- Gross Profit: {safe_get('grossProfit')}
- Operating Income: {safe_get('operatingIncome')}
- Net Income: {safe_get('netIncome')}
"""
        
        elif statement_type == "Balance Sheet":
            summary = f"""
For the period ending {date}, the company reported the following key balance sheet metrics:
- Total Assets: {safe_get('totalAssets')}
- Total Liabilities: {safe_get('totalLiabilities')}
- Total Equity: {safe_get('totalStockholdersEquity')}
"""
        
        elif statement_type == "Cash Flow":
            def safe_get(col):
                return financial_statements[col][i] if col in financial_statements.columns else "N/A"

    summary = f"""
For the period ending {date}, the company reported the following key cash flow metrics:
- Operating Cash Flow: {safe_get('operatingCashFlow')}
- Investing Cash Flow: {safe_get('cashflowFromInvestment')}
- Financing Cash Flow: {safe_get('cashflowFromFinancing')}
- Net Cash Flow: {safe_get('netCashFlow')}
"""
        summaries.append(summary.strip())

    all_summaries = "\n\n".join(summaries)

    prompt = f"""
You are an AI trained to provide financial analysis based on financial statements.

Please analyze the following data and provide insights for the {statement_type.lower()} of a company over the reported time periods.

Summarize each period’s data and then provide a concluding section that discusses trends, anomalies, and insights over time:

{all_summaries}
"""

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text
def financial_statements():
    st.title('GPT-4 & Financial Statements')

    statement_type = st.selectbox("Select financial statement type:", ["Income Statement", "Balance Sheet", "Cash Flow"])

    col1, col2 = st.columns(2)

    with col1:
        period = st.selectbox("Select period:", ["Annual", "Quarterly"]).lower()

    with col2:
        limit = st.number_input("Number of past financial statements to analyze:", min_value=1, max_value=10, value=4)
    

    ticker = st.text_input("Please enter the company ticker:")

    if st.button('Run'):
        if ticker:
            ticker = ticker.upper()
            financial_statements = get_financial_statements(ticker, limit, period, statement_type)

            with st.expander("View Financial Statements"):
                st.dataframe(financial_statements)

            financial_summary = generate_financial_summary(financial_statements, statement_type)

            st.write(f'Summary for {ticker}:\n {financial_summary}\n')
            
def main():
    st.sidebar.title('AI Financial Analyst')
    app_mode = st.sidebar.selectbox("Choose your AI assistant:",
        ["Financial Statements"])
    if app_mode == 'Financial Statements':
        financial_statements()


if __name__ == '__main__':
    main()
