from loguru import logger

def execute_trades(signals):
    for s in signals:
        logger.info(f"[SIMULATION] {s['action']}ING: {s['symbol']}")
        # Place live order using broker API here