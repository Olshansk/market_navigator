import os
import requests_cache
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import json
import time

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from iexfinance.refdata import get_symbols, get_iex_symbols, get_symbols
from iexfinance.stocks import get_historical_data
from iexfinance.altdata import get_social_sentiment
from iexfinance.stocks import Stock

# TODO(olshansky): Generalize this when we have more than one script
environment = os.getenv('ENVIRONMENT')

# Reference: https://iexcloud.io/docs/api/?gclid=CjwKCAiA4o79BRBvEiwAjteoYP0BtY28kGPakJs9r71RIpoKP_v2OVC1_J_GNRzyUEBQjox_mf-NVxoCE-UQAvD_BwE#request-limits
# tl;dr 100 requests per second
RATE_LIMIT_REQUESTS = 100  # Number of requests to make before sleeping
RATE_LIMIT_SLEEP =  10 # Amount of time to sleep whenever "waiting"

def is_prod():
    return environment == "PROD"

if is_prod():
    # TODO: Delete from PROD once things work.
    requests_cache.install_cache('iex_cache')
    # TODO(olshansky): Update the domain here: https://iexcloud.io/console/tokens
    IEX_TOKEN = "pk_5839e587dee649c7a3653e6fbadf7230"
    os.environ["IEX_API_VERSION"] = "iexcloud-v1"
    LAST_SYMBOL_IDX = -1
else:
    # TODO: Figure out if URL parameters are taken into account when caching
    requests_cache.install_cache('iex_cache')
    IEX_TOKEN = "Tpk_57fa15c2c86b4dadbb31e0c1ad1db895"
    os.environ["IEX_API_VERSION"] = "iexcloud-sandbox"
    LAST_SYMBOL_IDX = 10

# Deployment constants.
BUCKET_DIR = "/data/market_navigator/static_data"

# Analysis constants.
NUM_BUS_DAYS = 252 # TODO(olshansky): Better way to convert 52 weeks to business days
MAX_DELTA_PER = 0.2
NUM_YEARS_HISTORY = 5

# Graph visualization constants.
RED = "#FF0000"
BLUE = "#0000FF"

# The data fro IEX seems to be corrupted and have multiple entries for the same date. Only doing this as a workaround
# but need to eventually understand why it's happening.
# https://stackoverflow.com/questions/13035764/remove-rows-with-duplicate-indices-pandas-dataframe-and-timeseries
def drop_duplicate_indecies(df):
    return df.loc[~df.index.duplicated(keep='first')]

def is_near_min(delta):
    def is_near_min_internal(row):
        if math.isnan(row.rolling_min):
            return None
        else:
            return abs(row.rolling_min - row.close) / row.close < delta
    return is_near_min_internal

def is_near_max(delta):
    def is_near_max_internal(row):
        if math.isnan(row.rolling_min):
            return None
        else:
            return abs(row.rolling_max - row.close) / row.close < delta
    return is_near_max_internal

def count_trues(row):
    filtered = [v for v in row.values if (v is not None and not math.isnan(v))]
    l = len(filtered)
    s = filtered.count(True)
    return round(s / l, 2) if l > 0 else None

def get_min_max_dfs(symbols):
    end_date = datetime.now()
    start_date = end_date - relativedelta(years=NUM_YEARS_HISTORY)

    df_min = pd.DataFrame(columns=['date'])
    df_min.set_index('date', inplace=True)

    df_max = pd.DataFrame(columns=['date'])
    df_max.set_index('date', inplace=True)

    num_requests_since_last_sleep = 0

    for symbol_metadata in symbols:
        symbol = symbol_metadata['symbol']
        try:
            df = get_historical_data(symbol, start_date, end_date, close_only=True, output_format='pandas', token=IEX_TOKEN)
            num_requests_since_last_sleep += 1
            if num_requests_since_last_sleep > RATE_LIMIT_REQUESTS:
                time.sleep(RATE_LIMIT_SLEEP)

            # TODO: Remove this eventually once iex or python module fixes things...
            df = drop_duplicate_indecies(df)

            df['rolling_max'] = df['close'].rolling(window=NUM_BUS_DAYS, min_periods=NUM_BUS_DAYS).max()
            df['rolling_min'] = df['close'].rolling(window=NUM_BUS_DAYS, min_periods=NUM_BUS_DAYS).min()

            min_key = f'{symbol}_near_min'
            max_key = f'{symbol}_near_max'

            df_min[min_key] = df.apply(is_near_min(MAX_DELTA_PER), axis=1)
            df_max[max_key] = df.apply(is_near_max(MAX_DELTA_PER), axis=1)

            print(f"Successfully processed {symbol}", flush=True)
        except Exception as e:
            print(f"Failed to process {symbol}: {e}.", flush=True)

    return (df, df_min, df_max)

# TODO: Remind yourself how this work by running it in a notebook.
def compute_stocks_near_max_min(df_max, df_min):
    df_res = pd.DataFrame(columns=['date'])
    df_res.set_index('date', inplace=True)

    df_res['near_max'] = df_max.apply(count_trues, axis=1)
    df_res['near_min'] = df_min.apply(count_trues, axis=1)

    return df_res

def save_daily_results(df):
    ax = df.plot(color=[RED, BLUE], figsize=(20,10))
    ax.set_title(f"Percentage of stocks within {MAX_DELTA_PER * 100}% of 52 week min/max.")
    ax.axhline(y=df['near_max'].mean(), linestyle='--', color=RED)
    ax.axhline(y=df['near_min'].mean(), linestyle='--', color=BLUE)

    curr_date = "{:%Y_%m_%d}".format(datetime.now())

    env_prefix = "" if is_prod() else "dev_"

    fig = ax.get_figure()
    fig.savefig(f"{BUCKET_DIR}/{env_prefix}per_high_low_{curr_date}.png")
    fig.savefig(f"{BUCKET_DIR}/{env_prefix}per_high_low_latest.png")

    data = {
        'near_max' : df.iloc[-1].near_max,
        'near_min' : df.iloc[-1].near_min,
        'avg_near_max' : df.iloc[-1].near_min,
        'avg_near_min' : df.iloc[-1].near_min
    }
    with open(f'{BUCKET_DIR}/{env_prefix}per_high_low_{curr_date}.json', 'w') as f:
        json.dump(data, f)
    with open(f'{BUCKET_DIR}/{env_prefix}per_high_low_latest.json', 'w') as f:
        json.dump(data, f)

def main():
    symbols = get_symbols(token=IEX_TOKEN)[:LAST_SYMBOL_IDX]
    print("DONE retrieving symbols", flush=True)
    (df, df_min, df_max) = get_min_max_dfs(symbols)
    print("DONE computing dfs", flush=True)
    df_res = compute_stocks_near_max_min(df_max, df_min)
    print("DONE computing min & max", flush=True)
    save_daily_results(df_res)
    print("DONE saving results.", flush=True)

if __name__ == "__main__":
    main()
