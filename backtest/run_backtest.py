import pandas as pd
from backtest import backtest_symbol
from loguru import logger

logger.add("../logs/runtime.log", rotation="500 KB")

symbols = ["TITAN.NS", "CUB.NS", "SUPRIYA.NS", "COFORGE.NS", "KPITTECH.NS"]  # Replace with your top signals
all_trades = []

for sym in symbols:
    trades = backtest_symbol(sym)
    all_trades.extend(trades)

df = pd.DataFrame(all_trades)
df.to_csv("../data/backtest_results.csv", index=False)
print(df)
