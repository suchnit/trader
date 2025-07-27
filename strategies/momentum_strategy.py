import os
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
import traceback
from config import BUY_THRESHOLD, SELL_THRESHOLD, TREND_DISTANCE_THRESHOLD, SLOPE_PCT_THRESHOLD, ADX_THRESHOLD
import sys

def sanitize_multicolumn_df(df):
    df.columns = [f"{col[0]}_{col[1]}" for col in df.columns]
    return df

def detect_trend(data, close,ema200, ema_key='EMA_200', threshold=0.01, min_slope=0.05, window=5):
    slope = 0
    slope_pct = 0

    if len(data) >= 6:
        prev_ema = data['EMA_200'].iloc[-6]
        slope = ema200 - prev_ema
        slope_pct = slope / prev_ema if prev_ema != 0 else 0

    in_up = (close > ema200 * (1 + TREND_DISTANCE_THRESHOLD)) and slope_pct > SLOPE_PCT_THRESHOLD
    in_down = (close < ema200 * (1 - TREND_DISTANCE_THRESHOLD)) and slope_pct < -SLOPE_PCT_THRESHOLD

    return in_up, in_down, slope

def analyze_symbol(symbol, verbose=False):
    try:
        data = yf.download(symbol, period="400d", interval="1d", progress=False)

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        data = data.loc[:, ~data.columns.duplicated()]
        data = data.apply(pd.to_numeric, errors='coerce')

        if data.empty or len(data) < 50:
            logger.warning(f"⚠️ Insufficient data for: {symbol}")
            return None

        latest = data.iloc[-1]
        if latest['Volume'] < 100_000 or latest['Close'] < 100:
            return None

        data.ta.adx(high='High', low='Low', close='Close', append=True)
        data.ta.rsi(close='Close', append=True)
        data.ta.macd(close='Close', append=True)
        data.ta.bbands(close='Close', append=True)
        data.ta.ema(length=20, append=True)
        data.ta.ema(length=50, append=True)
        data.ta.ema(length=200, append=True)
        data.ta.stochrsi(close='Close', append=True)

        if data.empty or len(data) < 250:
            logger.warning(f"⚠️ Not enough data for EMA200 + slope: {symbol}")
            return None

        if 'EMA_200' not in data.columns:
            logger.warning(f"⚠️ EMA_200 not available for {symbol} — skipping slope calculation.")
            return None

        latest = data.iloc[-1]

        def extract_float(val):
            if isinstance(val, pd.Series):
                return val.iloc[-1]
            return float(val) if pd.notna(val) else 0

        adx = extract_float(latest.get('ADX_14', 0))
        rsi = extract_float(latest.get('RSI_14', 100))
        macd_hist = extract_float(latest.get('MACDh_12_26_9', 0))
        close = extract_float(latest.get('Close'))
        lower_band = extract_float(latest.get('BBL_20_2.0', 0))
        upper_band = extract_float(latest.get('BBU_20_2.0', 0))
        ema20 = extract_float(latest.get('EMA_20', 0))
        ema50 = extract_float(latest.get('EMA_50', 0))
        ema200 = extract_float(latest.get('EMA_200', 0))
        stochrsi = extract_float(latest.get('STOCHRSIk_14_14_3_3', 50))
        in_uptrend, in_downtrend, ema_slope = detect_trend(data, close, ema200)

        def evaluate_momentum_signal(rsi, stochrsi):
            if rsi < 30:
                if stochrsi < 20:
                    return 'buy'
                else:
                    return 'watchlist'
            elif rsi > 70:
                if stochrsi > 80:
                    return 'sell'
                else:
                    return 'watchlist'
            else:
                return 'neutral'

        momentum_rating = evaluate_momentum_signal(rsi, stochrsi)

        if momentum_rating not in ['buy', 'sell'] and adx <= ADX_THRESHOLD:
            if verbose:
                logger.debug(f"{symbol} :: Skipping due to weak trend and no strong momentum signal (ADX: {adx}, Momentum: {momentum_rating})")
            return None

        buy_conditions = [
            macd_hist > 0,
            close < lower_band,
            ema20 > ema50,
            momentum_rating == 'buy'
        ]

        sell_conditions = [
            macd_hist < 0,
            close > upper_band,
            ema20 < ema50,
            momentum_rating == 'sell'
        ]

        weights = [1.2, 0.6, 1.0, 1.0]
        buy_score = sum(w if cond else 0 for w, cond in zip(weights, buy_conditions))
        sell_score = sum(w if cond else 0 for w, cond in zip(weights, sell_conditions))

        if verbose:
            logger.debug(f"{symbol} :: Buy Conditions: {buy_conditions} | Buy Score: {buy_score:.2f}")
            logger.debug(f"{symbol} :: Sell Conditions: {sell_conditions} | Sell Score: {sell_score:.2f}")
            logger.debug(f"{symbol} :: ADX: {adx}, RSI: {rsi}, MACD_Hist: {macd_hist}, Close: {close}, EMA20: {ema20}, EMA50: {ema50}, EMA200: {ema200}, StochRSI: {stochrsi}, Momentum: {momentum_rating}")

        if buy_score >= BUY_THRESHOLD and buy_score > sell_score and in_uptrend:
            logger.info(f"📈 BUY signal: {symbol}")
            return {
                'symbol': symbol,
                'action': 'BUY',
                'score': round(buy_score, 2),
                'close': close,
                'version': 'adx_rsi_v2.6'
            }
        elif sell_score >= SELL_THRESHOLD and sell_score > buy_score and in_downtrend:
            logger.info(f"📉 SELL signal: {symbol}")
            return {
                'symbol': symbol,
                'action': 'SELL',
                'score': round(sell_score, 2),
                'close': close,
                'version': 'adx_rsi_v2.6'
            }
        elif abs(buy_score - sell_score) < 0.5 and not in_uptrend and not in_downtrend:
            return {
                'symbol': symbol,
                'action': 'WATCH',
                'score': round(max(buy_score, sell_score), 2),
                'close': close,
                'version': 'adx_rsi_v2.6'
            }
    except Exception as e:
        logger.error(f"❌ Error analyzing {symbol}: {e}")
        traceback.print_exc()

    return None


def run_strategy(symbols):
    signals = []
    logger.info(f"📊 Using thresholds - BUY: {BUY_THRESHOLD}, SELL: {SELL_THRESHOLD}")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(analyze_symbol, symbol) for symbol in symbols]
        for future in as_completed(futures):
            result = future.result()
            if result:
                signals.append(result)
    logger.info(f"Total signals generated: {len(signals)}")
    return signals
