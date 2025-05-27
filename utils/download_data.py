import pandas as pd
from nsepython import nse_eq_symbols

# Register the pandas_ta extension (optional in latest versions, but good practice)
pd.set_option('display.max_columns', None)

def get_bulk_data():
    df = pd.DataFrame(nse_eq_symbols())
    symbols = df[0].astype(str).str.strip()
    yahoo_symbols = symbols + ".NS"
    yahoo_symbols.to_csv("data/formatted_symbols.csv", index=False, header=False)
    print(f"✅ {len(yahoo_symbols)} symbols cleaned and saved to 'data/formatted_symbols.csv'")
    return yahoo_symbols.tolist()
