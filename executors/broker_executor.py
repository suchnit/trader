from loguru import logger

def execute_trades(signals):
    buy = 0
    sell = 0

    for s in signals:
        if s['action']=='BUY':
            buy = buy+1
        else:
            sell = sell+1

        logger.info(f"[SIMULATION] {s['action']}ING: {s['symbol']} @ {s['close']} (Confidence: {s['score']})")
        # Place live order using broker API here
    logger.info(f"BUY: {buy}, SELL: {sell}")