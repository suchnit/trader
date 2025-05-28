import yfinance as yf
import pandas as pd
import pandas_ta as ta
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
import traceback
import sys

def sanitize_multicolumn_df(df):
    df.columns = [f"{col[0]}_{col[1]}" for col in df.columns]
    return df

def analyze_symbol(symbol):
    try:
        data = yf.download(symbol, period="6mo", interval="1d", progress=False)

        # Flatten MultiIndex if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        # Drop duplicate columns
        data = data.loc[:, ~data.columns.duplicated()]

        # Basic checks
        if data.empty or len(data) < 50:
            logger.warning(f"⚠️ Insufficient data for: {symbol}")
            return None

        # Ensure numeric columns
        data = data.apply(pd.to_numeric, errors='coerce')

        # Add indicators
        data.ta.adx(high='High', low='Low', close='Close', append=True)
        data.ta.rsi(close='Close', append=True)
        data.ta.macd(close='Close', append=True)
        data.ta.bbands(close='Close', append=True)
        data.ta.ema(length=20, append=True)
        data.ta.ema(length=50, append=True)
        data.ta.stochrsi(close='Close', append=True)

        latest = data.iloc[-1]

        # Skip low-volume stocks
        if latest['Volume'] < 100000 or latest['Close'] < 100:
            return None

        def extract_float(val):
            if isinstance(val, pd.Series):
                return val.iloc[-1]
            return float(val) if pd.notna(val) else 0

        # Safely extract values
        adx = extract_float(latest.get('ADX_14', 0))
        rsi = extract_float(latest.get('RSI_14', 100))
        macd_hist = extract_float(latest.get('MACDh_12_26_9', 0))
        close = extract_float(latest['Close'])
        lower_band = extract_float(latest.get('BBL_20_2.0', 0))
        upper_band = extract_float(latest.get('BBU_20_2.0', 0))
        ema20 = extract_float(latest.get('EMA_20', 0))
        ema50 = extract_float(latest.get('EMA_50', 0))
        stochrsi = extract_float(latest.get('STOCHRSIk_14_14_3_3', 50))

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

        buy_score = sum(buy_conditions)
        sell_score = sum(sell_conditions)

        if buy_score >= 3:
            logger.info(f"📈 BUY signal: {symbol}")
            return {'symbol': symbol, 'action': 'BUY', 'score': buy_score, 'close': close}
        elif sell_score >= 4:
            logger.info(f"📉 SELL signal: {symbol}")
            return {'symbol': symbol, 'action': 'SELL', 'score': sell_score, 'close': close}

    except Exception as e:
        logger.error(f"❌ Error analyzing {symbol}: {e}")
        traceback.print_exc()

    return None

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
