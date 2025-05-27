import yfinance as yf
import pandas as pd
import pandas_ta as ta
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

def sanitize_multicolumn_df(df):
    df.columns = [f"{col[0]}_{col[1]}" for col in df.columns]
    return df

def analyze_symbol(symbol):
    try:
        print(f"Downloading data for: {symbol}")
        data = yf.download(symbol, period="6mo", interval="1d", progress=False)
        print(f"Starting analysis for: {symbol}")

        # Flatten MultiIndex if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        if data.empty or len(data) < 50:
            return None

        # Indicators
        data.ta.adx(high='High', low='Low', close='Close', append=True)
        data.ta.rsi(close='Close', append=True)
        data.ta.macd(close='Close', append=True)
        data.ta.bbands(close='Close', append=True)
        data.ta.ema(length=20, append=True)
        data.ta.ema(length=50, append=True)
        data.ta.stochrsi(close='Close', append=True)

        latest = data.iloc[-1]

        adx = latest.get('ADX_14', 0)
        rsi = latest.get('RSI_14', 100)

        macd_hist = latest.get('MACDh_12_26_9', 0)
        close = latest['Close']
        lower_band = latest.get('BBL_20_2.0', 0)
        upper_band = latest.get('BBU_20_2.0', 0)
        ema20 = latest.get('EMA_20', 0)
        ema50 = latest.get('EMA_50', 0)
        stochrsi = latest.get('STOCHRSIk_14_14_3_3', 50)

        buy_conditions = [
            adx > 20,
            rsi < 30,
            macd_hist > 0,
            close < lower_band,
            ema20 > ema50,
            stochrsi < 20
        ]

        sell_conditions = [
            adx > 20,
            rsi > 70,
            macd_hist < 0,
            close > upper_band,
            ema20 < ema50,
            stochrsi > 80
        ]

        if sum(buy_conditions) >= 4:
            logger.info(f"📈 BUY signal: {symbol}")
            return {'symbol': symbol, 'action': 'BUY'}
        elif sum(sell_conditions) >= 4:
            logger.info(f"📉 SELL signal: {symbol}")
            return {'symbol': symbol, 'action': 'SELL'}

    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
    print(f"Analysis done for: {symbol}")
    return None


# def analyze_symbol(symbol):
#     try:
#         print(f"Downloading data for: {symbol}")
#         df = yf.download(symbol, period="6mo", interval="1d", progress=False)
#         print(f"Starting analysis for: {symbol}")
#         df = sanitize_multicolumn_df(df)
#         if df.empty or len(df) < 15:
#             return None
#
#         df = df.copy(deep=True)
#         df.ta.adx(high='High', low='Low', close='Close', append=True)
#         df.ta.rsi(close='Close', append=True)
#
#         latest = df.iloc[-1]
#         adx = latest.get('ADX_14', 0)
#         rsi = latest.get('RSI_14', 100)
#
#         if adx > 25 and rsi < 30:
#             logger.info(f"📈 Signal generated: {symbol}")
#             return symbol
#         elif adx > 25 and rsi > 70:
#             logger.info(f"📉 SELL signal: {symbol}")
#             return {'symbol': symbol, 'action': 'SELL'}
#     except Exception as e:
#         logger.error(f"Error analyzing {symbol}: {e}")
#     print(f"Analysis done for: {symbol}")
#     return None

def run_strategy(symbols):
    signals = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(analyze_symbol, symbol) for symbol in symbols]
        for future in as_completed(futures):
            result = future.result()
            if result:
                signals.append(result)
    logger.info(f"Total signals generated: {len(signals)}")
    return signals
