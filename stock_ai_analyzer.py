
# 文件名：stock_ai_analyzer.py

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

st.set_page_config(page_title="AI美股分析小程序", layout="wide")
st.title("📈 AI美股分析小程序")

with st.sidebar:
    st.header("🧾 参数设置")
    ticker_symbol = st.text_input("输入股票代码 (如 AAPL, TSLA)", value="AAPL")
    start_date = st.date_input("开始日期", value=date.today() - timedelta(days=365))
    end_date = st.date_input("结束日期", value=date.today())

@st.cache_data(show_spinner=False)
def load_data(symbol, start, end):
    stock = yf.Ticker(symbol)
    df_price = stock.history(start=start, end=end)
    info = stock.info
    return df_price, info

try:
    df, info = load_data(ticker_symbol, start_date, end_date)
except Exception as e:
    st.error(f"数据加载失败：{e}")
    st.stop()

st.subheader("📊 公司基本信息")
if info:
    col1, col2, col3 = st.columns(3)
    col1.metric("公司名称", info.get("longName", "N/A"))
    col2.metric("行业", info.get("sector", "N/A"))
    col3.metric("市值", f"{info.get('marketCap', 0) / 1e9:.2f} B")

    col1.metric("市盈率 (PE)", info.get("trailingPE", "N/A"))
    col2.metric("收益增长率", f"{info.get('earningsQuarterlyGrowth', 0) * 100:.2f}%")
    col3.metric("ROE", f"{info.get('returnOnEquity', 0) * 100:.2f}%")

st.subheader("📉 股价走势图")
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index,
            open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            name='K线'))
fig.update_layout(xaxis_title="日期", yaxis_title="价格(USD)",
                  height=600, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

def generate_suggestion(info):
    pe = info.get("trailingPE", None)
    growth = info.get("earningsQuarterlyGrowth", 0)
    roe = info.get("returnOnEquity", 0)

    if pe and pe < 15 and growth > 0.1 and roe > 0.15:
        return "📈 建议：基本面良好，当前股价可能被低估，可考虑买入。"
    elif pe and pe > 30:
        return "⚠️ 建议：估值偏高，注意风险。"
    else:
        return "⏳ 建议：观察中，建议等待更多财报数据。"

st.subheader("🧠 AI分析建议")
suggestion = generate_suggestion(info)
st.info(suggestion)

with st.expander("📤 导出分析报告（开发中）"):
    st.write("未来将支持导出为 PDF 或 HTML 分析报告。")
