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
    # --- データ取得 ---
    stock = yf.Ticker(ticker_symbol)
    
    try:
        info = stock.info
    except:
        info = {"longName": ticker_symbol}

    # 財務データの取得（ここがエラーの元だったので慎重に取得）
    hist_financials = stock.financials.T
    bs = stock.balance_sheet.T

    # 指標の取得
    current_price = info.get('currentPrice') or 0
    pbr = info.get('priceToBook') or 0
    raw_yield = info.get('dividendYield') or 0
    # 利回りの計算修正（342%のようなミスを防ぐ）
    dividend_yield = raw_yield if raw_yield > 1 else raw_yield * 100

    # --- 2. 銘柄名と基本指標の表示 ---
    st.header(f"{info.get('longName', ticker_symbol)}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("現在株価", f"{current_price}円")
    col2.metric("PBR", f"{pbr:.2f}倍")
    col3.metric("配当利回り", f"{dividend_yield:.2f}%")

    # --- 3. 業績推移グラフ ---
    if not hist_financials.empty:
        st.subheader("業績推移（売上高・純利益）")
        rev = hist_financials.get('Total Revenue', pd.Series()) / 1_000_000
        net = hist_financials.get('Net Income Common Stockholders', pd.Series()) / 1_000_000
        
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        ax1.bar(rev.index.year, rev, label='売上高', color='lightgrey', alpha=0.5)
        ax1.plot(net.index.year, net, label='純利益', color='red', marker='o')
        ax1.set_ylabel("単位: 百万円")
        ax1.legend()
        st.pyplot(fig1)

        # --- 4. ROE推移グラフ（12%基準） ---
        if not bs.empty:
            st.subheader("ROE推移（目標12%）")
            # ROE = 純利益 / 自己資本
            equity = bs.get('Stockholders Equity', pd.Series())
            # 年を合わせて計算
            roe = (net * 1_000_000 / equity) * 100
            roe = roe.dropna() # 空白データを除外

            if not roe.empty:
                fig2, ax2 = plt.subplots(figsize=(10, 4))
                ax2.plot(roe.index.year, roe, label='ROE (%)', color='green', marker='s')
                # 12%のオレンジ基準線
                ax2.axhline(12, color='orange', linestyle='--', label='目標12%')
                # 12%以上のエリアを薄く塗る
                ax2.fill_between(roe.index.year, 12, roe, where=(roe >= 12), color='green', alpha=0.1, interpolate=True)
                ax2.set_ylabel("ROE (%)")
                ax2.set_ylim(0, max(roe.max() + 5, 20))
                ax2.legend()
                st.pyplot(fig2)

                # 自己資本比率
                latest_equity = equity.iloc[0]
                latest_assets = bs.get('Total Assets', pd.Series([1])).iloc[0]
                eq_ratio = (latest_equity / latest_assets) * 100
                st.write(f"最新の自己資本比率: {eq_ratio:.1f}%")
                if eq_ratio >= 50:
                    st.success("✅ 財務優良（50%以上）")
    else:
        st.error("財務データが取得できませんでした。しばらく時間を置いてから再度お試しください。")
    # スペシャルシチュエーション用メモ
    print("-" * 50)
    print("【メモ】")
    if pbr < 1: print("・PBR1倍割れ：資産価値に対して割安の可能性があります。")
    if dividend_yield > 3: print("・高配当：インカムゲインの魅力があります。")
    if eq_ratio > 70: print("・鉄壁の財務：不況にも強い可能性があります。")

# 実行
deep_analyze_stock(ticker_symbol)