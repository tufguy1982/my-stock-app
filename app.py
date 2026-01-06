import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# アプリのタイトル
st.title("高精度・銘柄分析ツール")

# 1. 入力サイドバー
st.sidebar.header("設定")
ticker_symbol = st.sidebar.text_input("銘柄コードを入力 (例: 7718.T)", "7718.T")

if ticker_symbol:
    # データ取得
    stock = yf.Ticker(ticker_symbol)
    try:
    info = stock.info
except:
    info = {"longName": ticker_symbol} # エラー時に名前だけでも表示

# 指標を個別に取得（infoがダメな時の保険）
current_price = info.get('currentPrice') or stock.history(period="1d")['Close'].iloc[-1]
pbr = info.get('priceToBook') or 0
# ...以下続く
    hist_financials = stock.financials.T
    
    # 銘柄名の表示
    st.header(f"{info.get('longName', ticker_symbol)}")

    # 2. 指標の表示（タイル形式）
    col1, col2, col3 = st.columns(3)
    current_price = info.get('currentPrice', 0)
    pbr = info.get('priceToBook', 0)
    dividend_yield = (info.get('dividendYield', 0) or 0) * 100

    col1.metric("現在株価", f"{current_price}円")
    col2.metric("PBR", f"{pbr:.2f}倍")
    col3.metric("配当利回り", f"{dividend_yield:.2f}%")

    # 3. グラフ表示
    st.subheader("業績推移（売上高・純利益）")
    rev = hist_financials.get('Total Revenue', pd.Series()) / 1_000_000
    net = hist_financials.get('Net Income Common Stockholders', pd.Series()) / 1_000_000
    
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(rev.index.year, rev, label='売上高', color='lightgrey', alpha=0.5)
    ax1.plot(net.index.year, net, label='純利益', color='red', marker='o')
    ax1.set_ylabel("単位: 百万円")
    ax1.legend()
    st.pyplot(fig)

    # 4. 判定ロジック
    st.subheader("AI自動チェック")
    bs = stock.balance_sheet.T
    equity = bs.get('Stockholders Equity', pd.Series()).iloc[0]
    assets = bs.get('Total Assets', pd.Series()).iloc[0]
    eq_ratio = (equity / assets) * 100

    if eq_ratio > 50:
        st.success(f"✅ 自己資本比率 {eq_ratio:.1f}%: 財務は非常に健全です。")
    else:
        st.warning(f"⚠️ 自己資本比率 {eq_ratio:.1f}%: 財務に注意が必要です。")

    if pbr < 1:
        st.info("✅ PBR 1倍割れ: 資産価値から見て割安圏内です。")