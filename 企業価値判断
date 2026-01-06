import yfinance as yf
import pandas as pd

def calculate_intrinsic_value(ticker_symbol, discount_rate=0.08, growth_rate_projection=0.03, projection_years=5):
    """
    Yahoo Financeからデータを取得し、DCF法で理論株価を算出する簡易関数
    """
    stock = yf.Ticker(ticker_symbol)
    
    # 1. 財務データの取得
    try:
        # キャッシュフロー計算書の取得
        cash_flow = stock.cashflow
        # 発行済株式数の取得
        shares_outstanding = stock.info.get('sharesOutstanding', None)
        # 現在の株価
        current_price = stock.history(period="1d")['Close'].iloc[-1]
        
        if cash_flow.empty or shares_outstanding is None:
            return "データが取得できませんでした。"
            
    except Exception as e:
        return f"エラーが発生しました: {e}"

    # 2. 直近のフリーキャッシュフロー(FCF)の計算
    # FCF = 営業キャッシュフロー + 投資キャッシュフロー(通常マイナスなので足す形になるが、yfinanceでは項目確認が必要)
    # 簡易的に Free Cash Flow の項目があればそれを使う、なければ計算
    try:
        # yfinanceの項目名は変わることがあるため注意が必要
        fcf_series = cash_flow.loc['Free Cash Flow']
        latest_fcf = fcf_series.iloc[0] # 最新年度
    except KeyError:
        # 手動計算: Operating Cash Flow - Capital Expenditure
        op_cf = cash_flow.loc['Operating Cash Flow'].iloc[0]
        capex = cash_flow.loc['Capital Expenditure'].iloc[0]
        latest_fcf = op_cf + capex # CapExはマイナス値で入っていることが多い

    # 3. 将来FCFの予測と現在価値への割引 (ご提示の数式のΣ部分)
    future_fcfs = []
    discounted_fcfs = []
    
    current_fcf = latest_fcf
    
    for t in range(1, projection_years + 1):
        # 成長率に基づいて将来FCFを予測
        predicted_fcf = current_fcf * (1 + growth_rate_projection)
        future_fcfs.append(predicted_fcf)
        
        # 現在価値に割り引く: FCF / (1+r)^t
        dcf = predicted_fcf / ((1 + discount_rate) ** t)
        discounted_fcfs.append(dcf)
        
        current_fcf = predicted_fcf

    # 4. ターミナルバリュー（永続価値）の計算
    # 5年目以降、永久に安定成長すると仮定した場合の価値
    terminal_growth_rate = 0.02 # 永久成長率（インフレ率相当など）
    terminal_value = (future_fcfs[-1] * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
    discounted_terminal_value = terminal_value / ((1 + discount_rate) ** projection_years)

    # 5. 合計企業価値
    total_enterprise_value = sum(discounted_fcfs) + discounted_terminal_value

    # 現金と負債の調整（ネットキャッシュ）を足し引きして株主価値にするのが正確ですが、
    # ここでは簡易化のため、このまま株式数で割ります。
    
    intrinsic_value_per_share = total_enterprise_value / shares_outstanding

    # 結果の表示
    print(f"--- 分析対象: {ticker_symbol} ---")
    print(f"現在の株価: {current_price:,.2f}")
    print(f"理論株価 (Intrinsic Value): {intrinsic_value_per_share:,.2f}")
    
    if intrinsic_value_per_share > current_price:
        print("判定: 割安 (Undervalued)")
        print(f"安全域 (Upside): {((intrinsic_value_per_share - current_price) / current_price) * 100:.2f}%")
    else:
        print("判定: 割高 (Overvalued)")

# --- 使用例 ---
# 米国株: Apple ('AAPL')
# 日本株: トヨタ ('7203.T') ※日本株は .T をつける
calculate_intrinsic_value('AAPL', discount_rate=0.09, growth_rate_projection=0.05)
