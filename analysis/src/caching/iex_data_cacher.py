import pandas as pd

import argparse
import tables
import logging
import os
import time
import warnings
import requests_cache
import pandas as pd
import logging

from iexfinance.refdata import get_symbols
from datetime import datetime
from typing import List
from analysis.src.altair_helpers.graphs import get_min_max_chart
from analysis.src.gcloud_helpers.permissions import make_blob_public
from analysis.src.iex_helpers.caching import get_historical_data_cached
from analysis.src.matplotlib_helpers.graphs import get_min_max_plot
from dateutil.relativedelta import relativedelta


from datetime import datetime, date
from iexfinance.stocks import get_historical_data

# Assumptions:
# 1. No missing data in existing dataframes in the store; data is complete between (date_min, date_max).
# 2. The requested data is of the same format (URL, params, retrieved columns, etc...).
# Reference for metadata: https://moonbooks.org/Articles/How-to-add-metadata-to-a-data-frame-with-pandas-in-python-/#store-in-a-hdf5-file
def get_historical_data_cached(store, symbol, start_date, end_date, **kwargs):
    # This is necessary to avoid fetching new data if the hours/minutes/seconds changed.
    def sanitize_date(date):
        return datetime(date.year, date.month, date.day)

    # This is necessary for performance reasons to avoid inferring column
    # types when saving the files.
    def format_df_columns(df):
        df["close"] = pd.to_numeric(df["close"])
        df["volume"] = pd.to_numeric(df["volume"])
        return df

    start_date = sanitize_date(start_date)
    end_date = sanitize_date(end_date)

    print(f"{symbol}: Trying to access historical data between {start_date} and {end_date}.")

    if symbol not in store:
        print(f"{symbol}: No data is cached.")
        df = format_df_columns(get_historical_data(symbol, start_date, end_date, **kwargs))
        metadata = {'min_date': start_date, 'max_date': end_date}
    else:
        df = store[symbol]
        metadata = store.get_storer(symbol).attrs.metadata

        print(f"{symbol}: Data is catched between {metadata['min_date']} and {metadata['max_date']}.")

        if start_date < metadata['min_date']:
            print(f"{symbol}: Requesting data between {start_date} and {metadata['min_date']}.")
            df = df.append(format_df_columns(get_historical_data(symbol, start_date, metadata['min_date'], **kwargs)))
            metadata['min_date'] = start_date

        if end_date > metadata['max_date']:
            print(f"{symbol}: Requesting data between {metadata['max_date']} and {end_date}.")
            print(f"delta_days = {(datetime.now() - metadata['max_date']).days}")
            df = df.append(format_df_columns(get_historical_data(symbol, metadata['max_date'], end_date, **kwargs)))
            metadata['max_date'] = end_date

        # Not using store.append() because of this deduplication need.
        df = df[~df.index.duplicated(keep='first')]

    store[symbol] = df
    store.get_storer(symbol).attrs.metadata = metadata

    return df

def _configure_dates():
    if None not in (START_DATE, END_DATE):
        return (START_DATE, END_DATE)

    end_date = datetime.now()
    start_date = end_date - relativedelta(years=NUM_YEARS_HISTORY)
    # Need to add a delta because 15 years is the max: https://iexcloud.io/docs/api/#historical-prices
    start_date += (
        relativedelta(days=7) if NUM_YEARS_HISTORY >= 15 else relativedelta(days=0)
    )
    return (start_date, end_date)

class HistoricalDataCacher:
    def __init__(self, symbols: List[str], store: pd.HDFStore) -> None:
        self.store = store
        self.symbols = symbols
        pass

    def _close_store(self):
        try:
            self.store.close()
            print("Successfully closed `store` file.")
        except Exception:
            logging.exception("Error closing store.")

    def _flush_store(self):
        try:
            print("About to flush the store")
            self.store.flush(fsync=True)
        except Exception:
            logging.exception("Error flushing store.")

    def _cache_data(self):
        num_requests_since_last_sleep = 0
        (start_date, end_date) = self._configure_dates()
        for symbol in self.symbols:
            try:
                get_historical_data_cached(
                    self.store,
                    symbol,
                    start_date,
                    end_date,
                    close_only=True,
                    output_format="pandas",
                    token=IEX_TOKEN,
                )
                num_requests_since_last_sleep += 1
                if num_requests_since_last_sleep > RATE_LIMIT_REQUESTS:
                    self._flush_store()
                    time.sleep(RATE_LIMIT_SLEEP)
                    num_requests_since_last_sleep = 0
            except Exception as e:
                logging.exception("Failed to process {symbol}")

    def cache_data(self):
        self._cache_data()