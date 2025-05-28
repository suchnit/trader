from strategies.momentum_strategy import run_strategy
from utils.download_data import get_bulk_data
from executors.broker_executor import execute_trades
from loguru import logger

logger.add("logs/runtime.log", rotation="500 KB")

if __name__ == '__main__':
    logger.info("🚀 Starting strategy execution")
    symbols = get_bulk_data()
    signals = run_strategy(symbols)
    execute_trades(signals)

    logger.info(f"✅ {len(symbols)} symbols analysed")
    logger.info("✅ Strategy execution completed")