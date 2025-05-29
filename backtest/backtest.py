import pandas as pd
import yfinance as yf
from strategies.momentum_strategy import analyze_symbol  # Adjust import as needed
from datetime import timedelta

def backtest_symbol(symbol, period="300d"):
    data = yf.download(symbol, period=period, interval="1d", progress=False)
    if data.empty or len(data) < 60:
        print(f"Skipping {symbol} due to insufficient data.")
        return []

    # If MultiIndex columns (e.g., from yfinance), flatten them
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in data.columns]
    else:
        data.columns = data.columns.str.strip()

    # Drop duplicate columns if any
    data = data.loc[:, ~data.columns.duplicated()]

    # Pre-calculate all indicators used in your analyzer
    import pandas_ta as ta
    data.ta.adx(high='High', low='Low', close='Close', append=True)
    data.ta.rsi(close='Close', append=True)
    data.ta.macd(close='Close', append=True)
    data.ta.bbands(close='Close', append=True)
    data.ta.ema(length=20, append=True)
    data.ta.ema(length=50, append=True)
    data.ta.ema(length=200, append=True)
    data.ta.stochrsi(close='Close', append=True)

    trades = []
    position = None  # None, 'LONG', or 'SHORT'
    entry_price = 0
    entry_date = None

    for i in range(200, len(data) - 1):  # Start after 200 to allow indicator warm-up
        print(f"symbol: {symbol}, count: {i-200}")
        subset = data.iloc[:i+1].copy()
        subset.columns = [col.replace(f'_{symbol}', '') for col in subset.columns]
        latest_date = subset.index[-1]

        # Mock the analyzer using slice
        result = analyze_symbol(symbol=symbol, verbose=False)
        if not result:
            continue

        signal = result.get('action')
        price = subset['Close'].iloc[-1]

        # Simple strategy: Enter on signal, exit on reverse signal
        if signal == 'BUY' and position is None:
            position = 'LONG'
            entry_price = price
            entry_date = latest_date
            trades.append(("BUY", latest_date, price))
        elif signal == 'SELL' and position == 'LONG':
            trades.append(("SELL", latest_date, price))
            trades.append(("TRADE", entry_date, entry_price, latest_date, price))
            position = None
            entry_price = None
            entry_date = None

    return trades
