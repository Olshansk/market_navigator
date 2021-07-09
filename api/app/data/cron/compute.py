# 1. Download full file from S3
# 2. Maybe append new data to store
# 3. Get list of tickers
# 4. Compute data for all tickers
# 6.

import fire
import logging
import pandas as pd

from app.data.reader import read_daily_data_from_hdf_store
from app.data.processor import compute_new_data
from app.files.s3 import download_file, file_last_modified_timestamp, BUCKET_PRIVATE


def download_store_and_compute_all_tickers_data():
    filename = '/tmp/daily_data.h5'
    download_file('daily_data.h5', filename, BUCKET_PRIVATE)
    compute_all_tickers_data(filename)


def compute_all_tickers_data(hdf_store_path: str = '/Volumes/SDCard/Quandl/daily_data.h5'):
    store = pd.HDFStore(hdf_store_path)
    tickers = store.get_storer('daily_data').attrs.tickers.split(';')
    for ticker in tickers[0:2]:
        df = read_daily_data_from_hdf_store(store, ticker)
        if not compute_new_data(ticker, df):
            logging.error(f"Error calculating data for {ticker}")
        else:
            logging.info(f"Successfully calculated data for {ticker}")

if __name__ == '__main__':
    fire.Fire({
        'compute_all': compute_all_tickers_data
    })