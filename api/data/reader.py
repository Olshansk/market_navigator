import pandas as pd

FEATHER_PATH = "/Users/olshansky/workspace/tip/daily_data.feather"

# TODO:
# 1. Reimport batch CSV data
# 2. Add support for appending
# 3. Recompute feather data once a day (cron?)
def read_full_df():
    df_full = pd.read_feather(FEATHER_PATH)
    df_full.set_index("date")
    df_full.index = pd.to_datetime(df_full["date"])
    return df_full.sort_index()
