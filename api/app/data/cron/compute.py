# 1. Download full file from S3
# 2. Maybe append new data to store
# 3. Get list of tickers
# 4. Compute data for all tickers
# 6.

import logging
import pandas as pd
from app.data.reader import read_daily_data_from_hdf_store
from app.data.processor import compute_new_data


def compute_all_tickers_data(hdf_store_path: str = '/Volumes/SDCard/Quandl/daily_data.h5'):
    store = pd.HDFStore(hdf_store_path)
    tickers = store.get_storer('daily_data').attrs.tickers.split(';')
    for ticker in tickers:
        df = read_daily_data_from_hdf_store(store, ticker)
        if not compute_new_data(ticker, df):
            logging.error(f"Error calculating data for {ticker}")
        else:
            logging.error(f"Successfully calculated data for {ticker}")