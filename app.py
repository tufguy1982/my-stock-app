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
        info = stock.info  #
    except:
           info = {"longName": ticker_symbol} # エラー時に名前だけでも表示

    # 指標を個別に取得（infoがダメな時の保険）
    current_price = info.get('currentPrice') or stock.history(period="1d")['Close'].iloc[-1]
    pbr = info.get('priceToBook') or 0
    # --- 3. 指標の計算と表示修正 ---
    st.subheader("基本指標")
    col1, col2, col3 = st.columns(3)
    
    # 配当利回りの修正（数値がある場合のみ適切に処理）
    raw_yield = info.get('dividendYield')
    if raw_yield:
        # 0.03 のような小数で来る場合と 3.4 のような数値で来る場合があるため調整
        dividend_yield = raw_yield if raw_yield > 1 else raw_yield * 100
    else:
        dividend_yield = 0

    col1.metric("現在株価", f"{current_price}円")
    col2.metric("PBR", f"{pbr:.2f}倍")
    col3.metric("配当利回り", f"{dividend_yield:.2f}%")

    # --- 4. 業績推移グラフ ---
    st.subheader("業績推移（売上高・純利益）")
    rev = hist_financials.get('Total Revenue', pd.Series()) / 1_000_000
    net = hist_financials.get('Net Income Common Stockholders', pd.Series()) / 1_000_000
    
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.bar(rev.index.year, rev, label='売上高', color='lightgrey', alpha=0.5)
    ax1.plot(net.index.year, net, label='純利益', color='red', marker='o')
    ax1.set_ylabel("単位: 百万円")
    ax1.legend()
    st.pyplot(fig1)

    # --- 5. ROE推移グラフ（12%基準線付き） ---
    st.subheader("ROE推移（目標12%）")
    bs = stock.balance_sheet.T
    if not bs.empty and not hist_financials.empty:
        # ROE = 純利益 / 自己資本
        equity = bs.get('Stockholders Equity', pd.Series())
        roe = (net * 1_000_000 / equity) * 100
        roe = roe.dropna() # データがない年を除外

        fig2, ax2 = plt.subplots(figsize=(10, 4))
        ax2.plot(roe.index.year, roe, label='ROE (%)', color='green', marker='s', linewidth=2)
        # 12%の基準線を引き、背景を薄く塗る
        ax2.axhline(12, color='orange', linestyle='--', label='目標12%')
        ax2.fill_between(roe.index.year, 12, roe, where=(roe >= 12), color='green', alpha=0.1)
        
        ax2.set_ylabel("ROE (%)")
        ax2.set_ylim(0, max(roe.max() + 5, 20)) # グラフの縦軸を見やすく調整
        ax2.legend()
        st.pyplot(fig2)

        # 最新の自己資本比率チェック
        latest_equity = equity.iloc[0]
        latest_assets = bs.get('Total Assets', pd.Series([1])).iloc[0]
        eq_ratio = (latest_equity / latest_assets) * 100
        
        st.write(f"最新の自己資本比率: {eq_ratio:.1f}%")
        if eq_ratio >= 50:
            st.success("✅ 財務優良（50%以上）")

