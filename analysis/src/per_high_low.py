import sys
import os
import requests_cache
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import json
import time
import warnings
import tables
import altair as alt

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from iexfinance.refdata import get_symbols, get_iex_symbols
from iexfinance.stocks import get_historical_data
from iexfinance.altdata import get_social_sentiment
from iexfinance.stocks import Stock
from iex_helpers.caching import get_historical_data_cached
from altair_helpers.graphs import get_min_max_chart
from matplotlib_helpers.graphs import get_min_max_plot
from gcloud_helpers.permissions import make_blob_public

from google.cloud import storage

# Reference: https://iexcloud.io/docs/api/?gclid=CjwKCAiA4o79BRBvEiwAjteoYP0BtY28kGPakJs9r71RIpoKP_v2OVC1_J_GNRzyUEBQjox_mf-NVxoCE-UQAvD_BwE#request-limits
# tl;dr 100 requests per second
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100)) # Number of requests to make before sleeping
RATE_LIMIT_SLEEP =  10 # Amount of time to sleep whenever "waiting"

# Deployment constants.
BUCKET_DIR = "/data/market_navigator/static_data"

BUCKET_NAME = "market-navigator-data"

# Analysis constants.
NUM_BUS_DAYS = 252 # TODO(olshansky): Better way to convert 52 weeks to business days
MAX_DELTA_PER = 0.2
# DELTAS = [0.05, 0.1, 0.15, 0.2, 0.25]
DELTAS = [0.1, 0.2]

# Graph visualization constants.
RED = "#FF0000"
BLUE = "#0000FF"

START_DATE = datetime.strptime(os.getenv('START_DATE'), '%Y-%m-%d') if 'START_DATE' in os.environ else None
END_DATE = datetime.strptime(os.getenv('END_DATE'), '%Y-%m-%d') if 'END_DATE' in os.environ else None

from dataclasses import dataclass
from typing import Dict

@dataclass
class MinMaxDataframe(object):
    df_min: pd.DataFrame
    df_max: pd.DataFrame

@dataclass
class MinMaxDataframes(object):
    dfs_min: Dict[int, pd.DataFrame]
    dfs_max: Dict[int, pd.DataFrame]

def is_prod():
    return os.getenv('ENVIRONMENT') == "PROD"

def env_prefix():
    return "" if is_prod() else "dev_"

# Track usage here: https://iexcloud.io/console/usage
if is_prod():
    os.environ["IEX_API_VERSION"] = "iexcloud-v1"
    IEX_TOKEN = os.getenv("IEX_TOKEN")
    store = pd.HDFStore(f'{BUCKET_DIR}/iex_store.h5')
    FIRST_SYMBOL_IDX = int(os.getenv('FIRST_SYMBOL_IDX'))
    LAST_SYMBOL_IDX = int(os.getenv('LAST_SYMBOL_IDX'))
    NUM_YEARS_HISTORY = int(os.getenv('NUM_YEARS_HISTORY'))
else:
    os.environ["IEX_API_VERSION"] = "iexcloud-sandbox"
    IEX_TOKEN = "Tpk_57fa15c2c86b4dadbb31e0c1ad1db895"
    if not os.path.exists(BUCKET_DIR):
        BUCKET_DIR = "."
        store = pd.HDFStore(f'../dev_iex_store.h5')
    requests_cache.install_cache('iex_cache')
    FIRST_SYMBOL_IDX = 0
    LAST_SYMBOL_IDX = 11
    NUM_YEARS_HISTORY = 4

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

def configure_dates():
    if None not in (START_DATE, END_DATE):
        return (START_DATE, END_DATE)

    end_date = datetime.now()
    start_date = end_date - relativedelta(years=NUM_YEARS_HISTORY)
    # Need to add a delta because 15 years is the max: https://iexcloud.io/docs/api/#historical-prices
    start_date += (relativedelta(days=7) if NUM_YEARS_HISTORY >= 15 else relativedelta(days=0))
    return (start_date, end_date)

def get_min_max_dfs(symbols, local_store=None):
    if local_store is None:
        local_store = store

    (start_date, end_date) = configure_dates()

    num_requests_since_last_sleep = 0
    for symbol in symbols:
        try:
            df = get_historical_data_cached(local_store, symbol, start_date, end_date, close_only=True, output_format='pandas', token=IEX_TOKEN)
            num_requests_since_last_sleep += 1
            if num_requests_since_last_sleep > RATE_LIMIT_REQUESTS:
                print("About to flush the store")
                local_store.flush(fsync=True)
                print("Finished flushing the store")
                time.sleep(RATE_LIMIT_SLEEP)
                num_requests_since_last_sleep = 0

            df['rolling_max'] = df['close'].rolling(window=NUM_BUS_DAYS, min_periods=NUM_BUS_DAYS).max()
            df['rolling_min'] = df['close'].rolling(window=NUM_BUS_DAYS, min_periods=NUM_BUS_DAYS).min()

            dfs_min = {}
            dfs_max = {}
            for max_delta in DELTAS:
                df_min = pd.DataFrame(columns=['date'])
                df_min.set_index('date', inplace=True)
                df_min[f'{symbol}_near_min'] = df.apply(is_near_min(max_delta), axis=1)
                dfs_min[max_delta] = df_min

                df_max = pd.DataFrame(columns=['date'])
                df_max.set_index('date', inplace=True)
                df_max[f'{symbol}_near_max'] = df.apply(is_near_max(max_delta), axis=1)
                dfs_max[max_delta] = df_max

            print(f"Successfully processed {symbol}", flush=True)
        except Exception as e:
            print(f"Failed to process {symbol}: {e}.", flush=True)

    return MinMaxDataframes(dfs_min=dfs_min, dfs_max=dfs_max)

def compute_near_max_min(symbols):
    min_max_dfs = get_min_max_dfs(symbols)
    dfs_res = {}
    for delta in DELTAS:
        df_res = pd.DataFrame(columns=['date'])
        df_res.set_index('date', inplace=True)

        df_res['near_min'] = min_max_dfs.dfs_min[delta].apply(count_trues, axis=1)
        df_res['near_max'] = min_max_dfs.dfs_max[delta].apply(count_trues, axis=1)

        dfs_res[delta] = df_res
        print(f"DONE computing min & max for {delta}", flush=True)
    return dfs_res

def save_daily_results(df, delta):
    curr_date = "{:%Y_%m_%d}".format(datetime.now())
    prefix = env_prefix()

    ## Save the figures

    # ax = get_min_max_plot(df, delta)
    # fig = ax.get_figure()
    # fig.savefig(f"{BUCKET_DIR}/{env_prefix}per_high_low_{curr_date}.png")
    # fig.savefig(f"{BUCKET_DIR}/{env_prefix}per_high_low_latest.png")

    df_alt = df.dropna(thresh=1)
    data_alt = df_alt.reset_index().melt('date')
    chart = get_min_max_chart(data_alt)

    with alt.data_transformers.enable(max_rows=None):
        print(f'{BUCKET_DIR}/{prefix}per_high_low_{curr_date}.html')
        chart.save(f'{BUCKET_DIR}/{prefix}per_high_low_{delta}_{curr_date}.html', embed_options={'renderer':'svg'})
        chart.save(f'{BUCKET_DIR}/{prefix}per_high_low_{delta}_latest.html', embed_options={'renderer':'svg'})

    make_blob_public(BUCKET_NAME, f"{prefix}per_high_low_{delta}_latest.html")

    # Save the metadata
    data = {
        'near_max' : df.iloc[-1].near_max,
        'near_min' : df.iloc[-1].near_min,
        'avg_near_max' : df["near_max"].mean(),
        'avg_near_min' : df["near_min"].mean(),
        'max_delta_per' : delta
    }

    with open(f'{BUCKET_DIR}/{prefix}per_high_low_{delta}_{curr_date}.json', 'w') as f:
        json.dump(data, f)
    with open(f'{BUCKET_DIR}/{prefix}per_high_low_{delta}_latest.json', 'w') as f:
        json.dump(data, f)

    make_blob_public(BUCKET_NAME, f"{prefix}per_high_low_{delta}_latest.json")

def close_store():
    try:
        store.close()
        print("Successfully closed `store` file.")
    except Exception as e:
        print("Error close `store` file:", e)

def main():
    all_symbols = get_symbols(token=IEX_TOKEN)
    symbols_df = all_symbols[FIRST_SYMBOL_IDX:LAST_SYMBOL_IDX]
    symbols = [symbol_metadata['symbol'] for _, symbol_metadata in symbols_df.iterrows()]
    print(f"DONE retrieving {len(all_symbols)} symbols. About to process {FIRST_SYMBOL_IDX} to {LAST_SYMBOL_IDX}", flush=True)
    dfs_res = get_min_max_dfs(symbols)
    print("DONE computing get_min_max_dfs.", flush=True)
    close_store()
    for delta in DELTAS: save_daily_results(dfs_res[delta])
    print("DONE saving results.", flush=True)

if __name__ == "__main__":
    with warnings.catch_warnings():
        # This happens when we try to save a symbol such as 'AAIC-B' in the HDF5 store
        # More details here: https://stackoverflow.com/questions/58414068/how-to-get-rid-of-naturalnamewarning
        warnings.filterwarnings("ignore", category=tables.NaturalNameWarning)
        main()
