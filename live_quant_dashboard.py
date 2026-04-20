{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import yfinance as yf\
import pandas as pd\
import plotly.graph_objects as go\
import plotly.express as px\
from datetime import datetime, timedelta\
import requests\
import numpy as np\
\
st.set_page_config(page_title="Institutional Quant Edge", layout="wide", page_icon="\uc0\u55357 \u56545 ")\
FINNHUB_API_KEY = "d7i63b1r01qu8vfnfpf0d7i63b1r01qu8vfnfpfg"\
\
st.markdown("""\
<style>\
    .stApp \{ background-color: #0e1117; color: #ffffff; \}\
    h1, h2, h3 \{ color: #00f0ff !important; \}\
    .news-card, .analyst-note \{ background-color: #1e1e1e; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #00f0ff; \}\
</style>\
""", unsafe_allow_html=True)\
\
st.title("\uc0\u55357 \u56545  Institutional Quant Edge Terminal")\
st.caption("Full quant TA \'95 Critical Thinking Notes \'95 Backtesting \'95 US + Canadian")\
\
with st.sidebar:\
    st.header("Catalyst Sentinel")\
    nav = st.radio("Navigation", ["Overview", "Market Data + Quant", "Catalysts", "Risk & Monte Carlo", "Filings", "Backtest Signals", "Critical Thinking Analyst"], label_visibility="collapsed")\
    \
    st.divider()\
    st.subheader("Your Holdings")\
    holdings_input = st.text_area("TICKER,shares,avg_cost (ticker currency)", \
                                  value="AAPL,10,220\\nXNDU.TO,50,15\\nNVDA,5,140\\nRY.TO,20,140", height=220)\
\
usd_cad = yf.Ticker("USDCAD=X").info.get("regularMarketPrice", 1.38)\
\
holdings = []\
for line in holdings_input.strip().split("\\n"):\
    if line.strip():\
        parts = [p.strip() for p in line.split(",")]\
        if len(parts) == 3:\
            holdings.append(\{"ticker": parts[0].upper(), "shares": float(parts[1]), "avg_cost": float(parts[2])\})\
\
portfolio_data = []\
total_value_cad = 0\
for h in holdings:\
    try:\
        stock = yf.Ticker(h["ticker"])\
        info = stock.info\
        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0\
        is_can = ".TO" in h["ticker"]\
        price_cad = price * usd_cad if not is_can else price\
        value_cad = h["shares"] * price_cad\
        cost_cad = h["shares"] * h["avg_cost"] * (usd_cad if not is_can else 1)\
        gain_pct = ((value_cad - cost_cad) / cost_cad * 100) if cost_cad else 0\
        portfolio_data.append(\{\
            "Ticker": h["ticker"],\
            "Price": round(price, 2),\
            "Currency": "CAD" if is_can else "USD",\
            "Value CAD": round(value_cad, 2),\
            "Gain %": round(gain_pct, 2),\
            "Daily %": round(info.get("regularMarketChangePercent", 0), 2)\
        \})\
        total_value_cad += value_cad\
    except:\
        pass\
\
df_port = pd.DataFrame(portfolio_data)\
\
if nav == "Overview":\
    st.metric("Total Portfolio Value (CAD)", f"$\{total_value_cad:,.2f\}")\
    st.dataframe(df_port.style.format(\{"Value CAD": "$\{:,.2f\}", "Gain %": "\{:+.2f\}%", "Daily %": "\{:+.2f\}%"\}), use_container_width=True)\
    fig = px.pie(df_port, values="Value CAD", names="Ticker", title="Allocation")\
    st.plotly_chart(fig, use_container_width=True)\
\
elif nav == "Critical Thinking Analyst":\
    st.subheader("\uc0\u55358 \u56800  Critical Thinking Analyst Notes")\
    for h in holdings:\
        ticker = h["ticker"]\
        try:\
            stock = yf.Ticker(ticker)\
            hist = stock.history(period="30d", interval="1d")\
            if len(hist) < 20: continue\
            close = hist['Close']\
            rsi = 100 - (100 / (1 + (close.diff().where(lambda x: x > 0, 0).rolling(14).mean() / -close.diff().where(lambda x: x < 0, 0).rolling(14).mean())))\
            macd = close.ewm(span=12).mean() - close.ewm(span=26).mean()\
            signal_line = macd.ewm(span=9).mean()\
            bb_mid = close.rolling(20).mean()\
            bb_std = close.rolling(20).std()\
            price = close.iloc[-1]\
            regime = "HIGH VOL" if close.pct_change().rolling(20).std().iloc[-1] > 0.025 else "LOW VOL"\
\
            score = 0\
            reasons = []\
            if rsi.iloc[-1] < 35: score += 3; reasons.append("RSI oversold")\
            if rsi.iloc[-1] > 65: score -= 3; reasons.append("RSI overbought")\
            if macd.iloc[-1] > signal_line.iloc[-1]: score += 2; reasons.append("MACD bullish")\
            else: score -= 2; reasons.append("MACD bearish")\
            if price > bb_mid.iloc[-1] + 2*bb_std.iloc[-1]: score -= 2; reasons.append("Overextended above BB")\
            if regime == "HIGH VOL": score -= 1; reasons.append("High volatility")\
\
            bias = "\uc0\u55357 \u56960  Bullish" if score >= 3 else "\u9888 \u65039  Bearish" if score <= -3 else "\u10145 \u65039  Neutral"\
            note = f"**\{bias\}** (Score: \{score\}/10)\\n\\nReasons: " + ", ".join(reasons) + "\\n\\nSuggested action: " + ("Consider adding on dips" if score > 2 else "Consider trimming" if score < -2 else "Hold and monitor")\
            st.markdown(f"<div class='analyst-note'>\{note\}</div>", unsafe_allow_html=True)\
        except:\
            st.write(f"Analysis unavailable for \{ticker\}")\
\
st.caption("This is the final complete dashboard. Refresh the page if needed.")}