# trader

1. ADX (Average Directional Index) measures trend strength, not direction.
Below 20: trend is weak or sideways → better to avoid signals (noise).
Above 20: indicates a meaningful trend (up or down).
Some traders use 25 as a stricter filter, but 20 is a common lower bound for detecting the beginning of a trend.

2. RSI < 30 (Buy) / > 70 (Sell)
Thresholds:
    Buy: RSI < 30 (oversold)
    Sell: RSI > 70 (overbought)
Why:
    RSI (Relative Strength Index) gauges momentum and reversal potential.
    <30: asset is likely oversold → possible bounce.
        70: asset is overbought → could correct.
🎯 Can tune to 35/65 or 25/75 for more or less sensitivity.

3. MACD Histogram > 0 (Buy) / < 0 (Sell)

Threshold: 0
Why:
    MACD Histogram shows momentum crossover:
            0 = bullish crossover (MACD line above signal)
        <0 = bearish crossover
    Crossing zero means change in momentum direction.
✅ Use this to detect early trend reversals or momentum confirmation.

4. Price < Lower BB (Buy) / > Upper BB (Sell)

Threshold: Breaks Bollinger Bands
Why:
    Price outside Bollinger Bands = statistically rare move (2+ standard deviations).
    Below lower band → potentially oversold dip → mean reversion.
    Above upper band → overbought spike → mean reversion or correction.
✅ Use this to catch extreme price action.
🎯 Works well in ranging markets, less in trending ones.

5. EMA20 > EMA50 (Buy) / EMA20 < EMA50 (Sell)

Threshold: Short EMA crossing over long
Why:
    Moving average crossovers are classic trend-following signals.
    EMA20 > EMA50 → short-term bullish trend forming.
    EMA20 < EMA50 → short-term bearish pressure.
✅ This adds trend confirmation to other signals.

6. StochRSI < 20 (Buy) / > 80 (Sell)
Thresholds:
    <20 = Oversold
    80 = Overbought
Why:
    StochRSI is RSI of RSI — a faster oscillator for momentum extremes.
    More sensitive to turns than RSI — better for timing entries/exits.
    0–20 → buy zone
    80–100 → sell zone
✅ Use this to sharpen entries after broader signals (like RSI or MACD).