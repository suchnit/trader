import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# Thresholds with fallback defaults
BUY_THRESHOLD = float(os.getenv("BUY_THRESHOLD", 2.5))
SELL_THRESHOLD = float(os.getenv("SELL_THRESHOLD", 3.0))
TREND_DISTANCE_THRESHOLD = float(os.getenv("TREND_DISTANCE_THRESHOLD", "0.01"))
SLOPE_PCT_THRESHOLD = float(os.getenv("SLOPE_PCT_THRESHOLD", "0.01"))  # 1%
