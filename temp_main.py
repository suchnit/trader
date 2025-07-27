import yfinance as yf
import pandas as pd
import pandas_ta as ta

symbol = "5PAISA.NS"
data = yf.download(symbol, period="12mo", interval="1d", progress=False)

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(1)
data = data.loc[:, ~data.columns.duplicated()]
data = data.apply(pd.to_numeric, errors='coerce')

# Add indicators
data.ta.adx(high='High', low='Low', close='Close', append=True)
data.ta.rsi(close='Close', append=True)
data.ta.macd(close='Close', append=True)
data.ta.bbands(length=20, std=2.0, close='Close', append=True)
data.ta.ema(length=20, append=True)
data.ta.ema(length=50, append=True)
data.ta.ema(length=200, close='Close', append=True)
data.ta.stochrsi(close='Close', append=True)

latest = data.iloc[-1]

# Print key indicators
print("Latest Indicators for 5PAISA:")
print(f"Close: {latest['Close']}")
print(f"ADX: {latest['ADX_14']}")
print(f"RSI: {latest['RSI_14']}")
print(f"MACD Histogram: {latest['MACDh_12_26_9']}")
print(f"Bollinger Bands (Lower, Upper): {latest['BBL_20_2.0']}, {latest['BBU_20_2.0']}")
print(f"EMAs (20, 50, 200): {latest['EMA_20']}, {latest['EMA_50']}, {latest['EMA_200']}")
print(f"StochRSI K: {latest['STOCHRSIk_14_14_3_3']}")
